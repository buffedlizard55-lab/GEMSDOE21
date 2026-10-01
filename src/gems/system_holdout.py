"""Conservative whole-fault-system grouping of catalogue components from official vectors.

Vectors are split/scorer metadata ONLY. They cannot be prediction features. Complete
raster components linked to one nonblank NUM are unioned; unmatched components remain
flagged proxies. One-cell linkage tolerance is never applied to the scoring mask.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from rasterio.features import bounds, rasterize
from rasterio.transform import rowcol
from scipy.ndimage import binary_dilation, label

from .holdout import Fold, farther_than, quadrants


class UnionFind:
    def __init__(self, count):
        self.parent = np.arange(count + 1)

    def find(self, value):
        value = int(value)
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = int(self.parent[value])
        return value

    def join(self, values):
        values = sorted(set(int(v) for v in values if v > 0))
        if not values:
            return
        roots = [self.find(v) for v in values]
        root = min(roots)
        for r in roots:
            self.parent[r] = root


def geometry_window(geometry, shape, transform, margin=2):
    left, bottom, right, top = bounds(geometry)
    rows, cols = rowcol(transform, [left, right], [top, bottom])
    r0, r1 = max(0, min(rows) - margin), min(shape[0], max(rows) + margin + 1)
    c0, c1 = max(0, min(cols) - margin), min(shape[1], max(cols) + margin + 1)
    if r0 >= r1 or c0 >= c1:
        return None
    return (slice(r0, r1), slice(c0, c1))


def link_systems(catalogue, records, transform):
    """Records have system (NUM or None), name and full EPSG:32611 line geometry."""
    catalogue = np.asarray(catalogue, dtype=bool)
    if catalogue.ndim != 2 or transform.b or transform.d or transform.a <= 0 or transform.e >= 0:
        raise ValueError("Need 2D catalogue and north-up transform")
    components, count = label(catalogue, structure=np.ones((3, 3)))
    unions = UnionFind(count)
    systems = defaultdict(set)
    system_geometry = defaultdict(list)
    system_names = defaultdict(set)
    trace_components = []
    vector_pixels = np.zeros(catalogue.shape, dtype=bool)
    linked_pixels = np.zeros(catalogue.shape, dtype=bool)
    missing_num = 0
    for i, record in enumerate(records):
        geometry = record["geometry"]
        sl = geometry_window(geometry, catalogue.shape, transform)
        if sl is None:
            continue
        system = record.get("system")
        if system is None or str(system).strip().lower() in ("", "none", "nan", "0"):
            missing_num += 1
            # Do not invent a geological ID or merge unrelated unnamed records.
            system = f"UNIDENTIFIED-TRACE-{i}"
        else:
            system = str(system).strip()
        name = str(record.get("name") or "").strip()
        system_names[system].add(name)
        system_geometry[system].append(geometry)
        window_transform = transform @ transform.translation(sl[1].start, sl[0].start)
        image = rasterize(
            [(geometry, 1)],
            out_shape=components[sl].shape,
            transform=window_transform,
            dtype="uint8",
            all_touched=False,
        ).astype(bool)
        vector_pixels[sl] |= image
        near = binary_dilation(image, iterations=1)  # Euclidean 1 cell, not a 300m credit buffer.
        linked_pixels[sl] |= near & catalogue[sl]
        ids = np.unique(components[sl][near & catalogue[sl]])
        ids = ids[ids > 0]
        systems[system].update(ids.tolist())
        trace_components.append((system, ids.tolist()))
    for ids in systems.values():
        unions.join(ids)
    roots = np.array([unions.find(i) for i in range(count + 1)], dtype=np.int32)
    groups = roots[components]
    geometry_by_group = defaultdict(list)
    system_group = {}
    for system, ids in systems.items():
        if ids:
            group = unions.find(min(ids))
            geometry_by_group[group].extend(system_geometry[system])
            system_group[system] = group
    linked_components = set(v for ids in systems.values() for v in ids)
    proxies = [i for i in range(1, count + 1) if i not in linked_components]
    name_conflicts = {
        k: sorted(v) for k, v in system_names.items() if len(v - {""}) > 1 and k in system_group
    }
    report = {
        "raster_components": count,
        "whole_groups": len(np.unique(groups[catalogue])),
        "vector_records_intersecting_grid": len(trace_components),
        "identified_systems_linked_to_catalogue": sum(not s.startswith("UNIDENTIFIED") for s in system_group),
        "records_missing_num": missing_num,
        "vector_raster_pixels": int(vector_pixels.sum()),
        "catalogue_exact_vector_overlap": int((catalogue & vector_pixels).sum()),
        "catalogue_pixels_within_one_cell_of_vectors": int(linked_pixels.sum()),
        "catalogue_pixels": int(catalogue.sum()),
        "unlinked_proxy_components": len(proxies),
        "unlinked_proxy_pixels": int(np.isin(components, proxies).sum()),
        "num_name_conflicts": name_conflicts,
        "system_to_group": system_group,
        "catalogue_used_as_predictor": False,
        "linkage_tolerance_pixels": 1,
        "scoring_mask_buffer_pixels": 0,
        "interpretation": "NUM-linked conservative groups plus flagged component proxies, not perfect physical fault-system truth",
    }
    return groups, dict(geometry_by_group), report


@dataclass
class SystemFold(Fold):
    hidden_geometry: np.ndarray


class SystemHoldout:
    def __init__(self, footprint, catalogue, groups, geometry_by_group, transform, buffer_px=15):
        self.footprint = np.asarray(footprint, dtype=bool)
        self.catalogue = np.asarray(catalogue, dtype=bool) & self.footprint
        self.groups = np.asarray(groups)
        if self.footprint.ndim != 2 or any(
            a.shape != self.footprint.shape for a in (self.catalogue, self.groups)
        ):
            raise ValueError("Footprint/catalogue/group shape mismatch")
        if (self.groups[self.catalogue] <= 0).any() or (self.groups[~self.catalogue] != 0).any():
            raise ValueError("Group IDs must cover exactly catalogue pixels")
        if not np.isfinite(buffer_px) or buffer_px < 0:
            raise ValueError("Buffer must be finite and nonnegative")
        self.geometry_by_group, self.transform, self.buffer_px = geometry_by_group, transform, buffer_px
        self.quad, self.names = quadrants(self.footprint)

    def fold(self, i):
        if i not in range(4):
            raise ValueError("Fold ID must be 0..3")
        region = self.quad == i
        ids = np.unique(self.groups[region & self.catalogue])
        hidden = np.isin(self.groups, ids) & self.catalogue
        geometries = [g for group in ids for g in self.geometry_by_group.get(int(group), [])]
        vector_hidden = (
            rasterize(
                [(g, 1) for g in geometries],
                out_shape=region.shape,
                transform=self.transform,
                dtype="uint8",
            ).astype(bool)
            if geometries
            else np.zeros_like(region)
        )
        hidden_geometry = hidden | vector_hidden
        train = (
            self.footprint
            & ~region
            & farther_than(region, self.buffer_px)
            & farther_than(hidden_geometry, self.buffer_px)
        )
        visible = self.catalogue & ~hidden & train
        rng = np.random.default_rng(4242 + i)
        count = max(1, int(round(0.20 * len(ids)))) if len(ids) else 0
        sparse_ids = rng.choice(ids, count, replace=False) if count else np.array([], dtype=int)
        sparse = np.isin(self.groups, sparse_ids) & region & self.catalogue
        sparse_known = self.catalogue & ~np.isin(self.groups, sparse_ids)
        return SystemFold(
            i,
            self.names[i],
            region,
            hidden,
            visible,
            train,
            ids,
            hidden & region,
            sparse,
            sparse_known,
            hidden_geometry,
        )

    def audit(self, fold):
        partly_visible = np.intersect1d(
            fold.hidden_component_ids, np.unique(self.groups[fold.visible_catalogue])
        )
        buffer_leaks = int((fold.train_domain & ~farther_than(fold.hidden_geometry, self.buffer_px)).sum())
        return {
            "fold": fold.name,
            "withheld_whole_groups": len(fold.hidden_component_ids),
            "withheld_pixels_full_grid": int(fold.hidden.sum()),
            "withheld_pixels_in_quadrant": int(fold.dense_truth.sum()),
            "withheld_pixels_outside_quadrant": int((fold.hidden & ~fold.region).sum()),
            "withheld_full_vector_and_label_geometry_pixels": int(fold.hidden_geometry.sum()),
            "training_pixels": int(fold.train_domain.sum()),
            "visible_positive_pixels": int(fold.visible_catalogue.sum()),
            "hidden_pixels_seen_by_model": int((fold.hidden & fold.visible_catalogue).sum()),
            "partly_visible_group_count": len(partly_visible),
            "training_pixels_inside_hidden_geometry_buffer": buffer_leaks,
            "buffer_type": "Euclidean",
            "buffer_pixels": self.buffer_px,
            "passes": not partly_visible.size
            and buffer_leaks == 0
            and not (fold.hidden & fold.train_domain).any(),
            "vectors_are_split_metadata_only": True,
        }
