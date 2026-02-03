"""
List node handlers for markdown AST.
"""

import re


class ListHandlerMixin:
    """Mixin for handling list nodes."""
    
    def handle_list(self, node: dict, prev_list_type: str) -> str:
        """Handle list node. Returns current list type."""
        ordered = node.get("attrs", {}).get("ordered", False)
        list_type = "List Number" if ordered else "List Bullet"
        current_type = "ordered" if ordered else "bullet"
        
        children = node.get("children", [])
        
        for idx, item in enumerate(children):
            restart = (idx == 0 and ordered and prev_list_type != current_type)
            self.handle_list_item(item, list_type, restart)
        
        return current_type
    
    def handle_list_item(self, node: dict, list_type: str, is_first: bool = False, level: int = 0):
        """Handle list item node.
        
        Creates multiple paragraphs for list items with multiple lines:
        - First line (header): LEFT alignment
        - Continuation lines: JUSTIFY for long text, LEFT for short/formulas
        """
        ordered = list_type == "List Number"
        
        for child in node.get("children", []):
            ctype = child.get("type")
            if ctype in ["paragraph", "block_text"]:
                # Get children and split by softbreak/linebreak
                children = child.get("children", [])
                lines = self._split_by_breaks(children)
                
                for line_idx, line_children in enumerate(lines):
                    if line_idx == 0:
                        # First line - create list item with bullet/number
                        p = self.builder.add_list_item(ordered=ordered, restart=(is_first and ordered), level=level)
                    else:
                        # Continuation lines - determine alignment
                        justify = self._should_justify_line(line_children)
                        p = self.builder.add_list_continuation(justify=justify)
                    
                    self.inline.render_children(line_children, p)
                    
            elif ctype == "list":
                # Handle nested list
                nested_ordered = child.get("attrs", {}).get("ordered", False)
                nested_list_type = "List Number" if nested_ordered else "List Bullet"
                for idx, nested_item in enumerate(child.get("children", [])):
                    self.handle_list_item(nested_item, nested_list_type, is_first=(idx == 0), level=level + 1)
            elif ctype == "table":
                # Handle table inside list item
                self.handle_table(child)
            else:
                # Fallback - create list item if not created yet
                p = self.builder.add_list_item(ordered=ordered, restart=(is_first and ordered), level=level)
                self.inline.render_children([child], p)
    
    def _split_by_breaks(self, children: list) -> list:
        """Split children list by softbreak/linebreak nodes into separate lines."""
        lines = []
        current_line = []
        
        for child in children:
            ctype = child.get("type")
            if ctype in ["softbreak", "linebreak"]:
                if current_line:
                    lines.append(current_line)
                    current_line = []
            else:
                current_line.append(child)
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [[]]
    
    def _should_justify_line(self, children: list) -> bool:
        """Determine if line should use JUSTIFY alignment.
        
        Returns False (LEFT) for:
        - Short lines (< 50 chars of actual text)
        - Lines that are mostly formulas
        
        Returns True (JUSTIFY) for long text lines.
        """
        if not children:
            return False
        
        # Estimate actual text length (excluding formula markers)
        text_len = 0
        formula_count = 0
        
        for child in children:
            ctype = child.get("type")
            if ctype == "text":
                raw = child.get("raw", "")
                formula_count += raw.count("⟦LATEX_INLINE:")
                formula_count += raw.count("⟦LATEX_BLOCK:")
                clean_text = re.sub(r'⟦LATEX_(?:INLINE|BLOCK):\d+⟧', '', raw)
                text_len += len(clean_text)
            elif ctype == "strong":
                for c in child.get("children", []):
                    if c.get("type") == "text":
                        raw = c.get("raw", "")
                        formula_count += raw.count("⟦LATEX_INLINE:")
                        clean_text = re.sub(r'⟦LATEX_(?:INLINE|BLOCK):\d+⟧', '', raw)
                        text_len += len(clean_text)
        
        # Short lines -> LEFT
        if text_len < 50:
            return False
        
        # Lines with many formulas and little text -> LEFT
        if formula_count >= 2 and text_len < 40:
            return False
        
        return True
