"""
AST node type handlers.

This module combines all handler mixins into a single NodeHandlers class.
"""

from .block_handlers import BlockHandlerMixin
from .list_handlers import ListHandlerMixin
from .table_handlers import TableHandlerMixin


class NodeHandlers(BlockHandlerMixin, ListHandlerMixin, TableHandlerMixin):
    """Handles specific AST node types.
    
    Combines functionality from:
    - BlockHandlerMixin: paragraphs, headings, code blocks, blockquotes
    - ListHandlerMixin: ordered and unordered lists
    - TableHandlerMixin: tables
    """
    
    def __init__(self, builder, inline_renderer):
        self.builder = builder
        self.inline = inline_renderer
