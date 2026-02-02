"""
Main markdown processor - facade for the parsing subsystem.
"""

from ..document_builder import DocumentBuilder
from .ast_processor import ASTProcessor


class MarkdownProcessor:
    """Processes markdown AST and builds DOCX document.
    
    This is the main entry point for markdown processing.
    It delegates to specialized components for preprocessing,
    parsing, and rendering.
    """
    
    def __init__(self, builder: DocumentBuilder):
        self.builder = builder
        self._processor = ASTProcessor(builder)
    
    def parse(self, text: str) -> list:
        """Parse markdown text to AST."""
        return self._processor.parse(text)
    
    def process(self, ast: list):
        """Process AST nodes."""
        self._processor.process(ast)
