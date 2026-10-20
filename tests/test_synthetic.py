import numpy as np
import pytest
from coolguard import synthetic


def test_deterministic():
    a = synthetic.render_case("shadow", 1, 3)
    b = synthetic.render_case("shadow", 1, 3)
    assert np.array_equal(a[0], b[0]) and a[2].corners == b[2].corners


def test_ground_truth_inside_frame_and_matches_homography():
    import cv2
    for cat in synthetic.CATEGORIES:
        scene, page, spec = synthetic.render_case(cat, 0, 1)
        gt = np.array(spec.corners)
        assert gt[:, 0].min() >= -1 and gt[:, 0].max() <= spec.width + 1
        assert gt[:, 1].min() >= -1 and gt[:, 1].max() <= spec.height + 1
        if cat != "lowres":
            H = np.array(spec.homography)
            src = np.array([[[0, 0]], [[synthetic.PAGE_W - 1, 0]], [[synthetic.PAGE_W - 1, synthetic.PAGE_H - 1]],
                            [[0, synthetic.PAGE_H - 1]]], np.float32)
            assert np.allclose(cv2.perspectiveTransform(src, H).reshape(4, 2), gt, atol=1e-3)


def test_limits_and_validation(tmp_path):
    with pytest.raises(ValueError):
        synthetic.render_case("nope", 0, 0)
    with pytest.raises(ValueError):
        synthetic.render_case("clean", 5, 0)
    with pytest.raises(ValueError):
        synthetic.render_case("clean", 0, 0, width=100000, height=480)
    with pytest.raises(ValueError):
        synthetic.generate_corpus(tmp_path, seeds=list(range(21)))
    with pytest.raises(ValueError):
        synthetic.generate_corpus(tmp_path, seeds=list(range(20)), categories=list(synthetic.CATEGORIES))
