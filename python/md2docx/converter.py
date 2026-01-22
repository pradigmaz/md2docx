"""
Main converter module.
"""

import sys
from pathlib import Path

from .document_builder import DocumentBuilder
from .markdown_parser import MarkdownProcessor


class Md2DocxConverter:
    """
    Markdown to DOCX converter with LaTeX support.
    
    Usage:
        converter = Md2DocxConverter("input.md", "output.docx")
        converter.convert()
    """
    
    def __init__(self, input_md: str, output_docx: str, settings: dict = None):
        """
        Initialize converter.
        
        Args:
            input_md: Path to input markdown file
            output_docx: Path to output DOCX file
            settings: Optional formatting settings dict
        """
        self.input_path = Path(input_md)
        self.output_path = Path(output_docx)
        self.builder = DocumentBuilder(settings)
        self.processor = MarkdownProcessor(self.builder)
    
    def convert(self):
        """Convert markdown file to DOCX."""
        if not self.input_path.exists():
            print(f"Error: Input file {self.input_path} not found.")
            sys.exit(1)
        
        # Read markdown
        text = self.input_path.read_text(encoding="utf-8")
        
        # Parse and process
        ast = self.processor.parse(text)
        self.processor.process(ast)
        
        # Save
        self.builder.save(str(self.output_path))
        print(f"Successfully converted {self.input_path} to {self.output_path}")
