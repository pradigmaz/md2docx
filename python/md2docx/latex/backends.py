"""
LaTeX rendering backend detection and initialization.
"""

import os
import sys
from pathlib import Path

# Auto-configure Cairo DLL path on Windows
if sys.platform == 'win32':
    _module_dir = Path(__file__).parent.parent.parent  # python/ folder
    _cairo_paths = [
        _module_dir.parent / 'cairo-windows-1.17.2' / 'lib' / 'x64',
        _module_dir / 'cairo-windows-1.17.2' / 'lib' / 'x64',
        Path(sys.prefix) / 'Scripts',
        Path(sys.prefix) / 'Library' / 'bin',
    ]
    for _cairo_path in _cairo_paths:
        if _cairo_path.exists() and (_cairo_path / 'cairo.dll').exists():
            os.environ['PATH'] = str(_cairo_path) + os.pathsep + os.environ.get('PATH', '')
            break

# Backend availability flags
ZIAMATH_AVAILABLE = False
MATPLOTLIB_AVAILABLE = False
SVG_BACKEND = None  # 'cairosvg' or 'svglib'

# Try cairosvg first
try:
    import ziamath as zm
    import cairosvg
    _test_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>'
    cairosvg.svg2png(bytestring=_test_svg.encode())
    ZIAMATH_AVAILABLE = True
    SVG_BACKEND = 'cairosvg'
except (ImportError, OSError):
    pass

# Try svglib as fallback
if not ZIAMATH_AVAILABLE:
    try:
        import ziamath as zm
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        import io
        _test_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'
        _drawing = svg2rlg(io.StringIO(_test_svg))
        ZIAMATH_AVAILABLE = True
        SVG_BACKEND = 'svglib'
    except (ImportError, OSError, Exception):
        pass

# Matplotlib fallback
if not ZIAMATH_AVAILABLE:
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("Agg")
        MATPLOTLIB_AVAILABLE = True
    except ImportError:
        pass
