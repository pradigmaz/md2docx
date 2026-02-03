"""
Regex patterns for LaTeX formula extraction.
"""

import re


# Block formulas: $$...$$ or multiline $...$
BLOCK_PATTERN = re.compile(
    r"\$\$([^$]+)\$\$"
    r"|"
    r"(?:^|(?<=\n))[ \t]*\$[ \t]*\n([^$]*?)\n[ \t]*\$[ \t]*(?=\n|$)"
    r"|"
    r"(?:^|(?<=\n))[ \t]*\$[ \t]*(\\begin\{[^}]+\}[^$]*?\\end\{[^}]+\})[ \t]*\$[ \t]*(?=\n|$)",
    re.DOTALL
)

# Inline formulas: $...$ (single line, no newlines inside)
INLINE_PATTERN = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)")

# Markers for extracted formulas - use Unicode brackets to avoid breaking markdown parsing
BLOCK_MARKER_PATTERN = re.compile(r"⟦LATEX_BLOCK:(\d+)⟧")
INLINE_MARKER_PATTERN = re.compile(r"⟦LATEX_INLINE:(\d+)⟧")


def extract_blocks(text: str) -> tuple[str, dict[int, str]]:
    """Extract block formulas and replace with markers."""
    blocks = {}

    def replace(m):
        idx = len(blocks)
        formula = m.group(1) or m.group(2) or m.group(3)
        if formula:
            formula = formula.replace('\\\\\\\\', '\\x00LB\\x00')
            formula = ' '.join(formula.split())
            formula = formula.replace('\\x00LB\\x00', ' \\\\\\\\ ')
            blocks[idx] = formula
            return f"\n\n⟦LATEX_BLOCK:{idx}⟧\n\n"
        return m.group(0)

    return BLOCK_PATTERN.sub(replace, text), blocks


def extract_inlines(text: str) -> tuple[str, dict[int, str]]:
    """Extract $...$ inline formulas and replace with markers."""
    inlines = {}
    
    def replace(m):
        idx = len(inlines)
        inlines[idx] = m.group(1)
        return f"⟦LATEX_INLINE:{idx}⟧"
    
    return INLINE_PATTERN.sub(replace, text), inlines
