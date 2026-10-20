"""Runtime probe: what is actually executing. COOL is detected from the build, never from env vars."""
from __future__ import annotations

import os
import platform
import re
import sys

import cv2

_EVIDENCE_OPS = ["resize", "adaptiveThreshold", "findContours", "getPerspectiveTransform",
                 "warpPerspective", "createCLAHE", "Canny", "GaussianBlur", "threshold",
                 "approxPolyDP", "intersectConvexConvex"]


def probe() -> dict:
    info = cv2.getBuildInformation()
    custom_hal = re.search(r"Custom HAL:\s*(.*)", info)
    baseline = re.search(r"Baseline:\s*(.*)", info)
    cv_path = os.path.dirname(cv2.__file__)
    cool_path = "/opt/cool" in cv_path.replace("\\", "/")
    kleidi = bool(re.search(r"kleidicv", info, re.I))
    cool_evidence = {
        "cv2_file_under_opt_cool": cool_path,
        "build_mentions_kleidicv": kleidi,
        "custom_hal": custom_hal.group(1).strip() if custom_hal else None,
    }
    # 'verified' requires the install path AND an Arm build; env vars alone never count.
    arch = platform.machine().lower()
    verified = cool_path and arch in ("aarch64", "arm64")
    return {
        "python": sys.version.split()[0], "python_executable": sys.executable,
        "opencv_version": cv2.__version__, "opencv_is_v5": cv2.__version__.startswith("5."),
        "opencv_module_path": cv2.__file__,
        "platform": platform.platform(), "architecture": platform.machine(),
        "cpu_baseline": baseline.group(1).strip() if baseline else None,
        "available_ops": {n: hasattr(cv2, n) for n in _EVIDENCE_OPS},
        "num_threads": cv2.getNumThreads(),
        "cool": {"verified": bool(verified), "evidence": cool_evidence,
                 "note": "COOL is considered verified only when cv2 is imported from /opt/cool on an aarch64 host; "
                         "this does not by itself prove which kernels accelerated a given workload."},
        "aws_instance_type": os.environ.get("COOLGUARD_INSTANCE_TYPE", "not-applicable-or-unset"),
    }
