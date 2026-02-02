"""
AST processing and node dispatch.
"""

import mistune
from .preprocessor import TextPreprocessor
from .inline_renderer import InlineRenderer
from .node_handlers import NodeHandlers


class ASTProcessor:
    """Processes markdown AST and dispatches to handlers."""
    
    def __init__(self, builder):
        self.builder = builder
        self.preprocessor = TextPreprocessor()
        self.inline = InlineRenderer(builder)
        self.handlers = NodeHandlers(builder, self.inline)
        self._prev_list_type = None
    
    def parse(self, text: str) -> list:
        """Parse markdown text to AST."""
        # Preprocess text
        text = self.preprocessor.preprocess(text)
        
        # Extract LaTeX before parsing (prevents mistune from breaking formulas)
        text, self.builder.latex_blocks = self.builder.latex.extract_blocks(text)
        text, self.builder.latex_inlines = self.builder.latex.extract_inlines(text)
        
        md = mistune.create_markdown(renderer=None, plugins=['table'])
        return md(text)
    
    def process(self, ast: list):
        """Process AST nodes."""
        self._prev_list_type = None
        for node in ast:
            self._process_node(node)
            # Track if this was a list for continuation
            if node.get("type") == "list":
                ordered = node.get("attrs", {}).get("ordered", False)
                self._prev_list_type = "ordered" if ordered else "bullet"
            elif node.get("type") not in ["blank_line"]:
                # Reset if non-list, non-blank node
                if node.get("type") != "paragraph" or not self._is_block_formula_only(node):
                    self._prev_list_type = None
    
    def _is_block_formula_only(self, node: dict) -> bool:
        """Check if paragraph contains only a block formula marker."""
        children = node.get("children", [])
        if len(children) == 1 and children[0].get("type") == "text":
            text = children[0].get("raw", "").strip()
            return self.builder.latex.block_marker_pattern.fullmatch(text) is not None
        return False
    
    def _process_node(self, node: dict):
        """Process single AST node."""
        ntype = node.get("type")
        
        if ntype == "heading":
            self.handlers.handle_heading(node)
        elif ntype == "paragraph":
            self.handlers.handle_paragraph(node)
        elif ntype == "list":
            self._prev_list_type = self.handlers.handle_list(node, self._prev_list_type)
        elif ntype == "block_code":
            self.handlers.handle_code_block(node)
        elif ntype == "block_quote":
            self.handlers.handle_blockquote(node)
        elif ntype == "thematic_break":
            pass  # Ignore --- separators
        elif ntype == "blank_line":
            pass  # Ignore blank lines
        elif ntype == "table":
            self.handlers.handle_table(node)
