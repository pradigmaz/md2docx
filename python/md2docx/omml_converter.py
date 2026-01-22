"""
LaTeX to OMML (Office Math Markup Language) converter.
Converts LaTeX formulas to native Word math format.
"""

import re
import warnings
from lxml import etree

try:
    import latex2mathml.converter
    import mathml2omml
    OMML_AVAILABLE = True
except ImportError:
    OMML_AVAILABLE = False


# OMML namespace
OMML_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

NSMAP = {
    'm': OMML_NS,
    'w': WORD_NS,
}


class OmmlConverter:
    """Converts LaTeX formulas to OMML for Word documents."""
    
    def __init__(self):
        self.enabled = OMML_AVAILABLE
        if not self.enabled:
            warnings.warn("latex2mathml or mathml2omml not available. Install with: pip install latex2mathml mathml2omml")
    
    def latex_to_omml(self, latex: str) -> etree._Element | None:
        """
        Convert LaTeX formula to OMML element.
        
        Args:
            latex: LaTeX formula (without $ delimiters)
            
        Returns:
            lxml Element with OMML or None on failure
        """
        if not self.enabled:
            return None
        
        try:
            # Preprocess LaTeX for better compatibility
            latex = self._preprocess_latex(latex)
            
            # Convert LaTeX to MathML
            mathml = latex2mathml.converter.convert(latex)
            
            # Convert MathML to OMML
            import html.entities
            omml_str = mathml2omml.convert(mathml, html.entities.name2codepoint)
            
            # Add namespace declaration to OMML string
            # mathml2omml outputs with m: prefix but no xmlns declaration
            omml_str = omml_str.replace(
                '<m:oMath>',
                f'<m:oMath xmlns:m="{OMML_NS}">'
            )
            
            # Parse OMML string to element
            omml_elem = etree.fromstring(omml_str.encode('utf-8'))
            
            return omml_elem
            
        except Exception as e:
            warnings.warn(f"Failed to convert LaTeX to OMML: {latex[:50]}... Error: {e}")
            return None
    
    def _preprocess_latex(self, latex: str) -> str:
        """Preprocess LaTeX for better MathML conversion."""
        # Remove leading/trailing whitespace
        latex = latex.strip()
        
        # Handle \text{} command - convert to \mathrm{}
        latex = re.sub(r'\\text\{([^}]*)\}', r'\\mathrm{\1}', latex)
        
        # Handle \dots -> \ldots
        latex = latex.replace(r'\dots', r'\ldots')
        
        # Handle \neq -> \ne
        latex = latex.replace(r'\neq', r'\ne')
        
        return latex
    
    def create_inline_omath(self, latex: str) -> etree._Element | None:
        """
        Create inline oMath element for embedding in paragraph.
        
        Args:
            latex: LaTeX formula
            
        Returns:
            m:oMath element or None
        """
        omml = self.latex_to_omml(latex)
        if omml is None:
            return None
        
        # The result from mathml2omml is already m:oMath
        # Just ensure it has correct namespace
        if omml.tag.endswith('oMath'):
            return omml
        
        # Wrap in oMath if needed
        omath = etree.Element(f'{{{OMML_NS}}}oMath', nsmap=NSMAP)
        omath.append(omml)
        return omath
    
    def create_block_omath_para(self, latex: str) -> etree._Element | None:
        """
        Create block oMathPara element for standalone formula paragraph.
        
        Args:
            latex: LaTeX formula
            
        Returns:
            m:oMathPara element or None
        """
        omml = self.latex_to_omml(latex)
        if omml is None:
            return None
        
        # Create oMathPara wrapper for block display
        omath_para = etree.Element(f'{{{OMML_NS}}}oMathPara', nsmap=NSMAP)
        
        # Add math properties for centering
        omath_para_pr = etree.SubElement(omath_para, f'{{{OMML_NS}}}oMathParaPr')
        jc = etree.SubElement(omath_para_pr, f'{{{OMML_NS}}}jc')
        jc.set(f'{{{OMML_NS}}}val', 'center')
        
        # Add the oMath element
        if omml.tag.endswith('oMath'):
            omath_para.append(omml)
        else:
            omath = etree.SubElement(omath_para, f'{{{OMML_NS}}}oMath')
            omath.append(omml)
        
        return omath_para


def is_omml_available() -> bool:
    """Check if OMML conversion is available."""
    return OMML_AVAILABLE
