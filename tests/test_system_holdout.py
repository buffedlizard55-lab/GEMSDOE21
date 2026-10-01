import numpy as np
from rasterio.transform import from_origin

from gems.system_holdout import SystemHoldout, link_systems


TRANSFORM = from_origin(0, 6000, 100, 100)


def record(y, x1, x2, system, name="Example"):
    return {
        "system": system,
        "name": name,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [100 * x1 + 50, 6000 - 100 * y - 50],
                [100 * x2 + 50, 6000 - 100 * y - 50],
            ],
        },
    }


def test_disconnected_same_system_hidden_everywhere_and_vector_buffer_purged():
    cat = np.zeros((60, 60), bool)
    cat[10, 5:21] = True
    cat[40, 40:51] = True
    cat[45, 5:15] = True
    records = [record(10, 5, 20, "123"), record(40, 35, 50, "123"), record(45, 5, 14, "999")]
    groups, geometry, audit = link_systems(cat, records, TRANSFORM)
    assert audit["raster_components"] == 3 and audit["whole_groups"] == 2
    assert groups[10, 5] == groups[40, 50] != groups[45, 5]
    h = SystemHoldout(np.ones_like(cat), cat, groups, geometry, TRANSFORM, buffer_px=2)
    fold = h.fold(0)
    assert fold.hidden[40, 50] and not fold.visible_catalogue[40, 50]
    assert fold.hidden_geometry[40, 35] and not fold.train_domain[41, 35]
    assert fold.visible_catalogue[45, 5]
    assert h.audit(fold)["passes"]
    assert h.audit(fold)["withheld_pixels_outside_quadrant"] == 11
    assert not (fold.hidden & fold.train_domain).any()


def test_shared_component_unions_vector_systems_transitively():
    cat = np.zeros((60, 60), bool)
    cat[10, 5:20] = True
    cat[20, 5:20] = True
    cat[40, 40:51] = True
    records = [
        record(10, 5, 19, "A"),
        record(20, 5, 19, "A"),
        record(20, 5, 19, "B"),
        record(40, 40, 50, "B"),
    ]
    groups, _, report = link_systems(cat, records, TRANSFORM)
    assert report["whole_groups"] == 1
    assert groups[10, 5] == groups[40, 50]


def test_unidentified_or_unmatched_components_remain_flagged_proxies():
    cat = np.zeros((60, 60), bool)
    cat[10, 5:20] = True
    cat[40, 40:51] = True
    groups, _, report = link_systems(cat, [record(10, 5, 19, None)], TRANSFORM)
    assert report["records_missing_num"] == 1 and report["unlinked_proxy_components"] == 1
    assert groups[10, 5] != groups[40, 50]


def test_sparse_reference_neutralizes_whole_system_not_clipped_pieces():
    cat = np.zeros((60, 60), bool)
    records = []
    for i, y in enumerate(range(3, 25, 4)):
        cat[y, 3:55] = True
        records.append(record(y, 3, 54, str(i + 1)))
    groups, geometry, _ = link_systems(cat, records, TRANSFORM)
    h = SystemHoldout(np.ones_like(cat), cat, groups, geometry, TRANSFORM, buffer_px=1)
    f = h.fold(0)
    chosen = np.unique(groups[f.sparse_truth])
    for group in chosen:
        assert not (f.sparse_known & (groups == group)).any()
    assert np.array_equal(f.sparse_truth, h.fold(0).sparse_truth)
