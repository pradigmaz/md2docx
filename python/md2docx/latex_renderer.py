"""
LaTeX formula rendering module.

This module is kept for backward compatibility.
All functionality has been moved to the latex subpackage.
"""

from .latex import LaTeXRenderer, ZIAMATH_AVAILABLE, MATPLOTLIB_AVAILABLE, SVG_BACKEND

__all__ = ["LaTeXRenderer", "ZIAMATH_AVAILABLE", "MATPLOTLIB_AVAILABLE", "SVG_BACKEND"]
