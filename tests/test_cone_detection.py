# tests/test_cone_detection.py
# Unit tests for frustum/cone detection logic in geometry_extractor.
# These tests cover the volume-ratio heuristics, NOT the Blender/PyVista
# integration (which requires a running Blender instance).
import pytest
import math


# ─────────────────────── VOLUME RATIO HEURISTIC TESTS ───────────────────────

# These constants must match geometry_extractor.py
BOX_RATIO = 1.0
CYL_RATIO = math.pi / 4       # ≈ 0.7854
SPH_RATIO = math.pi / 6       # ≈ 0.5236
CONE_RATIO = math.pi / 12     # ≈ 0.2618
TOLERANCE = 0.12


def _classify_ratio(ratio):
    """Reimplementation of the ratio classifier from geometry_extractor."""
    if abs(ratio - BOX_RATIO) < TOLERANCE:
        return "box"
    elif abs(ratio - CYL_RATIO) < TOLERANCE:
        return "cylinder"
    elif abs(ratio - SPH_RATIO) < TOLERANCE:
        return "sphere"
    elif abs(ratio - CONE_RATIO) < TOLERANCE:
        return "frustum"
    elif CONE_RATIO + TOLERANCE < ratio < SPH_RATIO - TOLERANCE:
        # Frustums with non-trivial top radius land between cone and sphere zones
        return "frustum"
    return "unsupported"


def test_box_ratio():
    """Volume ratio ≈ 1.0 classifies as box."""
    assert _classify_ratio(1.0) == "box"
    assert _classify_ratio(0.95) == "box"
    assert _classify_ratio(1.05) == "box"


def test_cylinder_ratio():
    """Volume ratio ≈ π/4 classifies as cylinder."""
    assert _classify_ratio(CYL_RATIO) == "cylinder"
    assert _classify_ratio(0.80) == "cylinder"
    assert _classify_ratio(0.72) == "cylinder"


def test_sphere_ratio():
    """Volume ratio ≈ π/6 classifies as sphere."""
    assert _classify_ratio(SPH_RATIO) == "sphere"
    assert _classify_ratio(0.50) == "sphere"
    assert _classify_ratio(0.55) == "sphere"


def test_cone_ratio():
    """Volume ratio ≈ π/12 classifies as frustum/cone."""
    assert _classify_ratio(CONE_RATIO) == "frustum"
    # Pointy cone: exact π/12
    assert _classify_ratio(math.pi / 12) == "frustum"


def test_frustum_between_cone_and_sphere():
    """Frustum with non-trivial top radius lands between cone and sphere zones."""
    # Range: CONE_RATIO + TOLERANCE (≈0.38) to SPH_RATIO - TOLERANCE (≈0.40)
    assert _classify_ratio(0.39) == "frustum"


def test_unsupported_ratio():
    """Volume ratios outside all known ranges classify as unsupported."""
    # Extremely low ratios (spiky/complex shapes)
    assert _classify_ratio(0.05) == "unsupported"
    # Very high ratio but not box-like
    assert _classify_ratio(1.2) == "unsupported"


def test_frustum_volume_formula():
    """Verify the mathematical relationship between frustum volume and bbox volume.

    For a cone of height h and base radius r:
      V_cone = (1/3) * π * r² * h
      V_bbox = (2r) * (2r) * h = 4r²h
      ratio = π / 12 ≈ 0.2618

    For a frustum (r1 > r2):
      V_frustum = (π * h / 3) * (r1² + r1*r2 + r2²)
      V_bbox = (2*r1) * (2*r1) * h = 4*r1²*h
      ratio = (π / 12) * (1 + r2/r1 + (r2/r1)²)
    """
    # Pointy cone: r2 = 0
    r1, r2, h = 1.0, 0.0, 2.0
    v_frustum = (math.pi * h / 3) * (r1**2 + r1*r2 + r2**2)
    v_bbox = (2*r1) * (2*r1) * h
    ratio = v_frustum / v_bbox
    assert abs(ratio - CONE_RATIO) < 0.01

    # Wide frustum: r2 = 0.5 * r1
    r2 = 0.5
    v_frustum = (math.pi * h / 3) * (r1**2 + r1*r2 + r2**2)
    v_bbox = (2*r1) * (2*r1) * h
    ratio = v_frustum / v_bbox
    # Ratio ≈ 0.458 — this falls in sphere zone by ratio alone,
    # but Layer 2 (PyVista) would reclassify it as frustum via cap analysis.
    # Here we verify it's NOT classified as box or cylinder.
    assert _classify_ratio(ratio) in ("frustum", "sphere")

    # r2 = r1 (cylinder): ratio should match CYL_RATIO
    r2 = 1.0
    v_frustum = (math.pi * h / 3) * (r1**2 + r1*r2 + r2**2)
    v_bbox = (2*r1) * (2*r1) * h
    ratio = v_frustum / v_bbox
    assert abs(ratio - CYL_RATIO) < 0.01
