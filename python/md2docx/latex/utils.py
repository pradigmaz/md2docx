"""
Utility functions for LaTeX rendering.
"""

import os
import warnings


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


def cleanup_temp_files(temp_files: list[str]):
    """Remove temporary PNG files."""
    for path in temp_files:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            warnings.warn(f"Failed to delete {path}: {e}")


def svg_to_png_svglib(svg_string: str, output_path: str, scale: float = 2.0):
    """Convert SVG to PNG using svglib + reportlab."""
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    import io
    
    drawing = svg2rlg(io.StringIO(svg_string))
    
    if drawing is None:
        raise ValueError("Failed to parse SVG")
    
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)
    
    renderPM.drawToFile(drawing, output_path, fmt="PNG")
