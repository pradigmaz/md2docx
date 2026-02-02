"""
Markdown parsing and AST processing module.

This module is kept for backward compatibility.
All functionality has been moved to the parsers subpackage.
"""

from .parsers import MarkdownProcessor

__all__ = ["MarkdownProcessor"]
