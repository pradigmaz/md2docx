"""
LaTeX formula normalization for different backends.
"""

import re


def normalize_for_ziamath(formula: str) -> str:
    """Normalize LaTeX for ziamath rendering.
    
    Ziamath uses ziafont and supports most LaTeX math.
    Some adjustments needed for compatibility.
    """
    # Handle multiple primes (derivatives) - f'''(x) -> f^{(3)}(x)
    # Must do this BEFORE other processing
    formula = re.sub(r"(\w)''''", r"\1^{(4)}", formula)  # 4th derivative
    formula = re.sub(r"(\w)'''", r"\1^{(3)}", formula)   # 3rd derivative  
    formula = re.sub(r"(\w)''", r"\1^{\\prime\\prime}", formula)  # 2nd derivative
    formula = re.sub(r"(\w)'(?!')", r"\1^{\\prime}", formula)  # 1st derivative (not followed by another ')
    
    # Fix ^T after matrix environments - wrap matrix in braces
    # \end{pmatrix}^T -> \end{pmatrix}}^T (with opening brace before \begin)
    for env in ['pmatrix', 'bmatrix', 'vmatrix', 'Bmatrix', 'matrix']:
        # Pattern: \begin{env}...\end{env}^something
        pattern = rf'(\\begin\{{{env}\}}.*?\\end\{{{env}\}})(\^)'
        formula = re.sub(pattern, r'{\1}\2', formula, flags=re.DOTALL)
    
    # Remove \left and \right - they can cause height issues in ziamath
    formula = re.sub(r'\\left\s*([(\[{|])', r'\1', formula)
    formula = re.sub(r'\\right\s*([)\]}|])', r'\1', formula)
    formula = re.sub(r'\\left\s*\\.', '', formula)  # \left.
    formula = re.sub(r'\\right\s*\\.', '', formula)  # \right.
    
    return formula


def normalize_for_mathtext(formula: str, use_tex: bool = False) -> str:
    """Normalize LaTeX for matplotlib mathtext."""
    if use_tex:
        return formula
    
    # Remove \left and \right FIRST - mathtext doesn't support them
    formula = re.sub(r'\\left\s*([(\[{|.])', r'\1', formula)
    formula = re.sub(r'\\right\s*([)\]}|.])', r'\1', formula)
    formula = re.sub(r'\\left\s*\\.', '', formula)
    formula = re.sub(r'\\right\s*\\.', '', formula)
    
    # Mathtext doesn't support many LaTeX commands - map them
    replacements = [
        # Comparison operators
        (r'\\le(?![a-zA-Z])', r'\\leq'),
        (r'\\ge(?![a-zA-Z])', r'\\geq'),
        (r'\\ne(?![a-zA-Z])', r'\\neq'),
        # Dots
        (r'\\ldots', '...'),
        (r'\\cdots', '...'),
        (r'\\dots', '...'),
        # Arrows
        (r'\\Rightarrow', r'\\Longrightarrow'),
        (r'\\to(?![a-zA-Z])', r'\\rightarrow'),
        # Greek letters
        (r'\\varepsilon', r'\\epsilon'),
        # Spacing
        (r'\\quad', r'\\ \\ '),
        (r'\\qquad', r'\\ \\ \\ \\ '),
        # Other
        (r'\\cdot', r'\\times'),
    ]
    
    for pattern, repl in replacements:
        formula = re.sub(pattern, repl, formula)
    
    # Handle \text{} - convert to \mathrm{}
    def replace_text(m):
        text = m.group(1)
        normalized = "".join("\\ " if c.isspace() else c for c in text)
        return f"\\mathrm{{{normalized}}}"
    
    formula = re.sub(r"\\text\{([^}]*)\}", replace_text, formula)
    
    return formula
