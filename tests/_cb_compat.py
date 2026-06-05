# tests/_cb_compat.py
# Import helper that patches numpy for nptyping compatibility BEFORE
# importing classy_blocks. Use this instead of `import classy_blocks as cb`
# in test files that run on Python 3.14 + numpy 2.x.
#
# nptyping 2.0.1 (vendored by classy_blocks 1.11.1) references many numpy
# type aliases that were removed in numpy 2.0. We patch them all here.
import numpy as np

_COMPAT_MAP = {
    # From nptyping/typing_.py lines 64-126
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

# Now safe to import classy_blocks
import classy_blocks as cb  # noqa: E402
