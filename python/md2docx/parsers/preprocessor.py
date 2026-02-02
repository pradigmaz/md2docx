"""
Text preprocessing before markdown parsing.
"""

import re


class TextPreprocessor:
    """Preprocesses markdown text before parsing."""
    
    def fix_broken_table_lines(self, text: str) -> str:
        """Fix table lines that were broken by text wrapping.
        
        Some editors wrap long lines, breaking markdown tables.
        This joins lines that appear to be continuations of table rows.
        """
        lines = text.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this looks like a table row (starts with |)
            if line.strip().startswith('|'):
                # A complete table row should end with |
                # Keep joining lines until we get a complete row
                while not line.rstrip().endswith('|') and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # If next line starts with |, it's a new row, stop joining
                    if next_line.strip().startswith('|'):
                        break
                    # If next line is empty, stop joining
                    if not next_line.strip():
                        break
                    # Join the continuation
                    line = line.rstrip() + next_line.lstrip()
                    i += 1
            
            fixed_lines.append(line)
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def clean_text(self, text: str) -> str:
        """Clean up garbage characters and formatting artifacts.
        
        Removes things like repeated punctuation (,,.), trailing commas, etc.
        """
        # ,. or ,,. or ,,,. -> . (keep the period)
        text = re.sub(r',+\.', '.', text)
        # ?. or ?.. -> ? (question mark is already sentence-ending)
        text = re.sub(r'\?\.+', '?', text)
        # !. or !.. -> !
        text = re.sub(r'!\.+', '!', text)
        # ,, at end of sentence (before newline or end of text) -> . (likely OCR artifact)
        text = re.sub(r',,(\s*\n)', r'.\1', text)
        text = re.sub(r',,$', '.', text)
        # Single trailing comma at end of sentence (before newline) -> . (likely OCR artifact)
        text = re.sub(r',(\s*\n)', r'.\1', text)
        # Remove repeated commas in middle of text (,, -> ,) - only if not at sentence end
        text = re.sub(r',{2,}(?!\s*[\n$])', ',', text)
        # Remove repeated periods (..) but keep ... (ellipsis)
        text = re.sub(r'\.{2}(?!\.)', '.', text)
        # Clean up spaces before punctuation
        text = re.sub(r'\s+([,.])', r'\1', text)
        return text
    
    def preprocess(self, text: str) -> str:
        """Apply all preprocessing steps."""
        text = self.fix_broken_table_lines(text)
        text = self.clean_text(text)
        return text
