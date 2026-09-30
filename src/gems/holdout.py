"""Whole 8-connected catalogue segment hide/recover, with Euclidean training purges."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import distance_transform_edt, label


@dataclass
class Fold:
    id: int
    name: str
    region: np.ndarray
    hidden: np.ndarray
    visible_catalogue: np.ndarray
    train_domain: np.ndarray
    hidden_component_ids: np.ndarray
    dense_truth: np.ndarray
    sparse_truth: np.ndarray
    sparse_known: np.ndarray


def quadrants(footprint: np.ndarray):
    footprint = np.asarray(footprint, dtype=bool)
    yy, xx = np.nonzero(footprint)
    if len(yy) == 0:
        raise ValueError("Empty footprint")
    ymid, xmid = int(np.median(yy)), int(np.median(xx))
    y, x = np.ogrid[: footprint.shape[0], : footprint.shape[1]]
    q = np.full(footprint.shape, -1, dtype=np.int8)
    for i, cond in enumerate(
        [
            (y < ymid) & (x < xmid),
            (y < ymid) & (x >= xmid),
            (y >= ymid) & (x < xmid),
            (y >= ymid) & (x >= xmid),
        ]
    ):
        q[footprint & cond] = i
    return q, ["NW", "NE", "SW", "SE"]


def farther_than(mask: np.ndarray, radius: float) -> np.ndarray:
    # scipy EDT on an all-True array sees a virtual boundary; handle an empty mask explicitly.
    return distance_transform_edt(~mask) > radius if mask.any() else np.ones(mask.shape, dtype=bool)


class WholeSegmentHoldout:
    def __init__(self, footprint, catalogue, buffer_px=15):
        self.footprint = np.asarray(footprint, dtype=bool)
        self.catalogue = np.asarray(catalogue, dtype=bool) & self.footprint
        if self.footprint.ndim != 2 or self.catalogue.shape != self.footprint.shape:
            raise ValueError("Footprint/catalogue shape mismatch")
        if buffer_px < 0:
            raise ValueError("Negative buffer")
        self.buffer_px = buffer_px
        self.quad, self.names = quadrants(self.footprint)
        self.components, self.n_components = label(self.catalogue, structure=np.ones((3, 3)))

    def fold(self, i: int) -> Fold:
        if i not in range(4):
            raise ValueError("Fold id must be 0..3")
        region = self.quad == i
        ids = np.unique(self.components[region & self.catalogue])
        ids = ids[ids > 0]
        hidden = np.isin(self.components, ids) & self.catalogue
        train = (
            self.footprint
            & ~region
            & farther_than(region, self.buffer_px)
            & farther_than(hidden, self.buffer_px)
        )
        visible = self.catalogue & ~hidden & train
        # Randomize WHOLE globally-defined IDs, never connected pieces clipped to a quadrant.
        rng = np.random.default_rng(4242 + i)
        count = max(1, int(round(0.20 * len(ids)))) if len(ids) else 0
        sparse_ids = rng.choice(ids, count, replace=False) if count else np.array([], dtype=int)
        sparse = np.isin(self.components, sparse_ids) & region & self.catalogue
        sparse_known = self.catalogue & ~np.isin(self.components, sparse_ids)
        return Fold(
            i, self.names[i], region, hidden, visible, train, ids, hidden & region, sparse, sparse_known
        )

    def audit(self, fold: Fold) -> dict:
        partly_visible = np.intersect1d(
            fold.hidden_component_ids, np.unique(self.components[fold.visible_catalogue])
        )
        return {
            "fold": fold.name,
            "withheld_whole_components": len(fold.hidden_component_ids),
            "withheld_pixels_full_grid": int(fold.hidden.sum()),
            "withheld_pixels_in_quadrant": int(fold.dense_truth.sum()),
            "withheld_pixels_outside_quadrant": int((fold.hidden & ~fold.region).sum()),
            "training_pixels": int(fold.train_domain.sum()),
            "visible_positive_pixels": int(fold.visible_catalogue.sum()),
            "hidden_pixels_seen_by_model": int((fold.hidden & fold.visible_catalogue).sum()),
            "partly_visible_component_count": len(partly_visible),
            "buffer_type": "Euclidean",
            "buffer_pixels": self.buffer_px,
            "passes": len(partly_visible) == 0 and not (fold.hidden & fold.train_domain).any(),
            "catalogue_derived_external_inputs_allowed": False,
        }
