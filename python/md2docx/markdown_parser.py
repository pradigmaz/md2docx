"""
Markdown parsing and AST processing module.
"""

import re
import mistune

from .document_builder import DocumentBuilder
from .inline_renderer import InlineRenderer
from .node_handlers import NodeHandlers


class MarkdownProcessor:
    """Processes markdown AST and builds DOCX document."""
    
    def __init__(self, builder: DocumentBuilder):
        self.builder = builder
        self.inline = InlineRenderer(builder)
        self.handlers = NodeHandlers(builder, self.inline)
    
    def _fix_broken_table_lines(self, text: str) -> str:
        """Fix table lines that were broken by text wrapping.
        
        Some editors wrap long lines, breaking markdown tables.
        This joins lines that appear to be continuations of table rows.
        """
        lines = text.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if line.strip().startswith('|'):
                while not line.rstrip().endswith('|') and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip().startswith('|'):
                        break
                    if not next_line.strip():
                        break
                    line = line.rstrip() + next_line.lstrip()
                    i += 1
            
            fixed_lines.append(line)
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def parse(self, text: str) -> list:
        """Parse markdown text to AST."""
        # Fix broken table lines first
        text = self._fix_broken_table_lines(text)
        
        # Remove footnote references like [^1], [^2], etc.
        text = re.sub(r'\[\^\d+\]', '', text)
        
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
            
            if node.get("type") == "list":
                ordered = node.get("attrs", {}).get("ordered", False)
                self._prev_list_type = "ordered" if ordered else "bullet"
            elif node.get("type") not in ["blank_line"]:
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
        elif ntype == "table":
            self.handlers.handle_table(node)
        # Ignore: thematic_break, blank_line
