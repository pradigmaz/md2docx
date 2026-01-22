"""
LaTeX formula rendering module.
Supports ziamath (full LaTeX) with matplotlib fallback.
"""

import os
import re
import tempfile
import warnings

# Try ziamath first (full LaTeX support without system LaTeX)
try:
    import ziamath as zm
    import cairosvg
    ZIAMATH_AVAILABLE = True
except ImportError:
    ZIAMATH_AVAILABLE = False
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("Agg")
        MATPLOTLIB_AVAILABLE = True
    except ImportError:
        MATPLOTLIB_AVAILABLE = False


class LaTeXRenderer:
    """Renders LaTeX formulas to PNG images."""
    
    def __init__(self):
        self.temp_files: list[str] = []
        self.use_ziamath = False
        self.use_tex = False
        self.enabled = self._check_support()
        
        # Regex patterns for LaTeX formulas
        # Block formulas: $$...$$ OR $ on its own line ... $ on its own line
        self.block_pattern = re.compile(
            r"\$\$(.+?)\$\$"  # $$...$$ style
            r"|"
            r"(?:^|\n)\$[ \t]*\n(.*?)\n[ \t]*\$(?=\n|$)",  # $ on own line
            re.DOTALL
        )
        # Inline formulas: $...$ (single line, no newlines inside)
        self.inline_pattern = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)")
        self.block_marker_pattern = re.compile(r"%%LATEX_BLOCK:(\d+)%%")
        self.inline_marker_pattern = re.compile(r"%%LATEX_INLINE:(\d+)%%")
    
    def _check_support(self) -> bool:
        """Check available rendering backends."""
        if ZIAMATH_AVAILABLE:
            self.use_ziamath = True
            return True
        
        if not MATPLOTLIB_AVAILABLE:
            return False
            
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
        fig = plt.figure(figsize=(1, 1))
        fig.text(0.5, 0.5, r"$x$", fontsize=12, usetex=usetex)
        temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp.close()
        fig.savefig(temp.name, transparent=True, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
        os.unlink(temp.name)
    
    def render_to_png(self, formula: str, is_block: bool = False) -> str | None:
        """
        Render LaTeX formula to PNG file.
        
        Args:
            formula: LaTeX formula (without $ delimiters)
            is_block: True for block formulas (larger size)
            
        Returns:
            Path to PNG file or None on failure
        """
        if not self.enabled:
            return None
        
        try:
            if self.use_ziamath:
                return self._render_ziamath(formula)
            else:
                return self._render_matplotlib(formula, is_block)
        except Exception as e:
            warnings.warn(f"Failed to render: {formula[:50]}... Error: {e}")
            return None
    
    def _render_ziamath(self, formula: str) -> str:
        """Render using ziamath."""
        # Normalize formula to avoid rendering issues
        formula = self._normalize_for_ziamath(formula)
        
        latex = zm.Latex(formula)
        svg = latex.svg()
        
        temp = tempfile.NamedTemporaryFile(suffix=".png", prefix="latex_", delete=False)
        temp.close()
        
        # Render with transparent background
        cairosvg.svg2png(bytestring=svg.encode(), write_to=temp.name, scale=2.0)
        self.temp_files.append(temp.name)
        return temp.name
    
    def _render_matplotlib(self, formula: str, is_block: bool) -> str:
        """Render using matplotlib."""
        formula = self._normalize_for_mathtext(formula)
        
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
    
    def _normalize_for_ziamath(self, formula: str) -> str:
        """Normalize LaTeX for ziamath rendering.
        
        Ziamath has issues with \\left and \\right delimiters causing
        extremely tall SVG output. Replace with regular delimiters.
        """
        # Remove \left and \right - they cause height issues in ziamath
        formula = re.sub(r'\\left\s*([(\[{|])', r'\1', formula)
        formula = re.sub(r'\\right\s*([)\]}|])', r'\1', formula)
        formula = re.sub(r'\\left\s*\\.', '', formula)  # \left.
        formula = re.sub(r'\\right\s*\\.', '', formula)  # \right.
        return formula
    
    def _normalize_for_mathtext(self, formula: str) -> str:
        """Normalize LaTeX for matplotlib mathtext."""
        if self.use_tex:
            return formula
        
        def replace_text(m):
            text = m.group(1)
            normalized = "".join("\\ " if c.isspace() else c for c in text)
            return f"\\text{{{normalized}}}"
        
        return re.sub(r"\\text\{([^}]*)\}", replace_text, formula)
    
    def extract_blocks(self, text: str) -> tuple[str, dict[int, str]]:
        """Extract block formulas ($$...$$ or $\\n...\\n$) and replace with markers."""
        blocks = {}
        
        def replace(m):
            idx = len(blocks)
            # m.group(1) is $$...$$ style, m.group(2) is $\n...\n$ style
            formula = m.group(1) or m.group(2)
            # Normalize whitespace - replace newlines with spaces
            formula = ' '.join(formula.split())
            blocks[idx] = formula
            # Add blank lines around marker so mistune treats it as separate paragraph
            return f"\n\n%%LATEX_BLOCK:{idx}%%\n\n"
        
        return self.block_pattern.sub(replace, text), blocks
    
    def extract_inlines(self, text: str) -> tuple[str, dict[int, str]]:
        """Extract $...$ inline formulas and replace with markers."""
        inlines = {}
        
        def replace(m):
            idx = len(inlines)
            inlines[idx] = m.group(1)
            return f"%%LATEX_INLINE:{idx}%%"
        
        return self.inline_pattern.sub(replace, text), inlines
    
    def cleanup(self):
        """Remove temporary PNG files."""
        for path in self.temp_files:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                warnings.warn(f"Failed to delete {path}: {e}")
        self.temp_files.clear()
    
    @staticmethod
    def get_image_size(png_path: str) -> tuple[int, int]:
        """Get PNG dimensions in pixels."""
        try:
            from PIL import Image
            with Image.open(png_path) as img:
                return img.size
        except ImportError:
            # Read PNG header directly
            import struct
            with open(png_path, 'rb') as f:
                f.read(16)
                w = struct.unpack('>I', f.read(4))[0]
                h = struct.unpack('>I', f.read(4))[0]
                return (w, h)
        except Exception:
            return (100, 20)
