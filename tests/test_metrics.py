import json
import cv2
import numpy as np
import pytest
from coolguard import metrics, synthetic


def test_polygon_iou_identity_and_disjoint():
    q = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], np.float32)
    assert metrics.polygon_iou(q, q) == pytest.approx(1.0)
    assert metrics.polygon_iou(q, q + 100) == 0.0
    assert metrics.polygon_iou(q, q + [5, 0]) == pytest.approx(1 / 3, abs=1e-4)


def test_order_quad_is_permutation_invariant():
    q = np.array([[10, 10], [90, 12], [88, 80], [8, 78]], np.float32)
    ref = metrics.order_quad(q)
    for perm in ([1, 2, 3, 0], [3, 2, 1, 0], [2, 0, 3, 1]):
        assert np.allclose(metrics.order_quad(q[perm]), ref)


@pytest.mark.parametrize("cat", sorted(synthetic.CATEGORIES))
def test_oracle_always_accepted(cat):
    """A detector returning the true corners must pass every category/level (guards against an unfair metric)."""
    for lv in range(len(synthetic.CATEGORIES[cat])):
        scene, page, spec = synthetic.render_case(cat, lv, 0)
        gt = np.array(spec.corners, np.float32)
        ev = metrics.evaluate_case(scene, page, gt, gt)
        assert ev["accepted"], (cat, lv, ev)


def test_wrong_detections_rejected():
    scene, page, spec = synthetic.render_case("clean", 0, 0)
    gt = np.array(spec.corners, np.float32)
    assert not metrics.evaluate_case(scene, page, gt, None)["accepted"]
    shifted = gt + [40, 0]
    assert not metrics.evaluate_case(scene, page, gt, shifted)["accepted"]
    assert not metrics.evaluate_case(scene, page, gt, gt[:3])["accepted"]
    # point order is irrelevant by design (order_quad), so a permuted true quad is still accepted
    assert metrics.evaluate_case(scene, page, gt, gt[[0, 2, 1, 3]])["accepted"]
    nan = gt.copy(); nan[0, 0] = np.nan
    collinear = np.array([[0, 0], [10, 10], [20, 20], [30, 30]], np.float32)
    concave = np.array([[0, 0], [100, 0], [50, 20], [0, 100]], np.float32)
    for bad in (nan, collinear, concave):
        assert "invalid_quad" in metrics.evaluate_case(scene, page, gt, bad)["failure_reasons"]
