# tests/conftest.py
# Compatibility shim: nptyping 2.0.1 references numpy type aliases that were
# removed in numpy 2.0. This conftest patches them back BEFORE collection
# (before any test file does `import classy_blocks as cb`).
#
# This is ONLY needed for the test environment (Python 3.14 + numpy 2.4.6).
# The Blender addon uses Blender's bundled Python 3.12 + numpy 1.26, which
# has all these aliases natively.
import numpy as np

_COMPAT_MAP = {
    "bool8":         np.bool_,
    "object0":       np.object_,
    "int0":          np.intp,
    "int_":          np.intp,
    "uint0":         np.uintp,
    "uint":          np.uintp,
    "float_":        np.float64,
    "longfloat":     np.longdouble,
    "singlecomplex": np.complex64,
    "complex_":      np.complex128,
    "cfloat":        np.complex128,
    "clongfloat":    np.clongdouble,
    "longcomplex":   np.clongdouble,
    "string_":       np.bytes_,
    "bytes0":        np.bytes_,
    "unicode_":      np.str_,
    "str0":          np.str_,
    "void0":         np.void,
}

for _attr, _fallback in _COMPAT_MAP.items():
    if not hasattr(np, _attr):
        setattr(np, _attr, _fallback)
