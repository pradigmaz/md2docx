"""
Main LaTeX renderer class.
"""

import os
import tempfile
import warnings

from .backends import ZIAMATH_AVAILABLE, MATPLOTLIB_AVAILABLE, SVG_BACKEND
from .normalizers import normalize_for_ziamath, normalize_for_mathtext
from .patterns import (
    BLOCK_PATTERN, INLINE_PATTERN,
    BLOCK_MARKER_PATTERN, INLINE_MARKER_PATTERN,
    extract_blocks, extract_inlines
)
from .utils import get_image_size, cleanup_temp_files, svg_to_png_svglib


class LaTeXRenderer:
    """Renders LaTeX formulas to PNG images."""
    
    def __init__(self):
        self.temp_files: list[str] = []
        self.use_ziamath = False
        self.use_tex = False
        self.enabled = self._check_support()
        
        # Expose patterns as instance attributes for compatibility
        self.block_pattern = BLOCK_PATTERN
        self.inline_pattern = INLINE_PATTERN
        self.block_marker_pattern = BLOCK_MARKER_PATTERN
        self.inline_marker_pattern = INLINE_MARKER_PATTERN
    
    def _check_support(self) -> bool:
        """Check available rendering backends."""
        if ZIAMATH_AVAILABLE:
            self.use_ziamath = True
            return True
        
        if not MATPLOTLIB_AVAILABLE:
            return False
        
        import matplotlib
        import matplotlib.pyplot as plt
        
        # Try matplotlib with usetex
        try:
            matplotlib.rcParams["text.usetex"] = True
            self._test_matplotlib(usetex=True)
            self.use_tex = True
            return True
        except Exception:
            pass
        
        # Try matplotlib mathtext
        try:
            matplotlib.rcParams["text.usetex"] = False
            self._test_matplotlib(usetex=False)
            self.use_tex = False
            return True
        except Exception as e:
            warnings.warn(f"LaTeX rendering not available: {e}")
            return False
    
    def _test_matplotlib(self, usetex: bool):
        """Test matplotlib rendering."""
        import matplotlib.pyplot as plt
        
        fig = plt.figure(figsize=(1, 1))
        fig.text(0.5, 0.5, r"$x$", fontsize=12, usetex=usetex)
        temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp.close()
        fig.savefig(temp.name, transparent=True, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
        os.unlink(temp.name)
    
    def render_to_png(self, formula: str, is_block: bool = False) -> str | None:
        """Render LaTeX formula to PNG file.
        
        Args:
            formula: LaTeX formula (without $ delimiters)
            is_block: True for block formulas (larger size)
            
        Returns:
            Path to PNG file or None on failure
        """
        if not self.enabled:
            return None
        
        # Try ziamath first, fall back to matplotlib on error
        if self.use_ziamath:
            try:
                return self._render_ziamath(formula)
            except Exception as e:
                # Try matplotlib as fallback for complex formulas
                if MATPLOTLIB_AVAILABLE:
                    try:
                        return self._render_matplotlib(formula, is_block)
                    except Exception:
                        pass
                warnings.warn(f"Failed to render: {formula[:50]}... Error: {e}")
                return None
        else:
            try:
                return self._render_matplotlib(formula, is_block)
            except Exception as e:
                warnings.warn(f"Failed to render: {formula[:50]}... Error: {e}")
                return None
    
    def _render_ziamath(self, formula: str) -> str:
        """Render using ziamath."""
        import ziamath as zm
        
        formula = normalize_for_ziamath(formula)
        
        latex = zm.Latex(formula)
        svg = latex.svg()
        
        temp = tempfile.NamedTemporaryFile(suffix=".png", prefix="latex_", delete=False)
        temp.close()
        
        if SVG_BACKEND == 'cairosvg':
            import cairosvg
            cairosvg.svg2png(bytestring=svg.encode(), write_to=temp.name, scale=2.0)
        else:
            svg_to_png_svglib(svg, temp.name, scale=2.0)
        
        self.temp_files.append(temp.name)
        return temp.name
    
    def _render_matplotlib(self, formula: str, is_block: bool) -> str:
        """Render using matplotlib."""
        import matplotlib.pyplot as plt
        
        formula = normalize_for_mathtext(formula, self.use_tex)
        
        length = len(formula)
        if is_block:
            width, height, fontsize = max(4, min(12, length/6)), 1, 16
        else:
            width, height, fontsize = max(2, min(6, length/10)), 0.5, 14
        
        fig = plt.figure(figsize=(width, height), dpi=300)
        fig.text(0.5, 0.5, f"${formula}$", fontsize=fontsize, 
                 usetex=self.use_tex, va="center", ha="center")
        
        temp = tempfile.NamedTemporaryFile(suffix=".png", prefix="latex_", delete=False)
        temp.close()
        
        fig.savefig(temp.name, dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
        
        self.temp_files.append(temp.name)
        return temp.name
    
    def extract_blocks(self, text: str) -> tuple[str, dict[int, str]]:
        """Extract block formulas and replace with markers."""
        return extract_blocks(text)
    
    def extract_inlines(self, text: str) -> tuple[str, dict[int, str]]:
        """Extract inline formulas and replace with markers."""
        return extract_inlines(text)
    
    def cleanup(self):
        """Remove temporary PNG files."""
        cleanup_temp_files(self.temp_files)
        self.temp_files.clear()
    
    @staticmethod
    def get_image_size(png_path: str) -> tuple[int, int]:
        """Get PNG dimensions in pixels."""
        return get_image_size(png_path)
