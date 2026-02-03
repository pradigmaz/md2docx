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
    
    def fix_indented_tables(self, text: str) -> str:
        """Remove leading indentation from table rows.
        
        Tables inside list items have indentation which prevents
        mistune from recognizing them as tables.
        """
        lines = text.split('\n')
        result = []
        in_table = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check if this is a table row (starts and ends with |)
            if stripped.startswith('|') and stripped.endswith('|'):
                in_table = True
                # Remove leading whitespace from table rows
                result.append(stripped)
            elif in_table and stripped.startswith('|'):
                # Continuation of table (might not end with | if broken)
                result.append(stripped)
            else:
                in_table = False
                result.append(line)
        
        return '\n'.join(result)
    
    def fix_nested_list_indentation(self, text: str) -> str:
        """Fix nested list items that have 4-space indentation.
        
        Mistune treats 4-space indented lines as code blocks.
        Nested list items should use 2-space indentation.
        """
        lines = text.split('\n')
        result = []
        
        for line in lines:
            # Check if line starts with 4 spaces followed by list marker (* or -)
            # and convert to 2-space indentation
            match = re.match(r'^(    +)([*\-])\s+', line)
            if match:
                spaces = match.group(1)
                marker = match.group(2)
                rest = line[match.end():]
                # Convert 4-space blocks to 2-space
                new_indent = '  ' * (len(spaces) // 4)
                result.append(f'{new_indent}{marker} {rest}')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def clean_text(self, text: str) -> str:
        """Clean up garbage characters and formatting artifacts.
        
        Removes things like repeated punctuation (,,.), trailing commas, etc.
        """
        # ,: -> : (comma before colon is OCR artifact, e.g. "классы,:" -> "классы:")
        text = re.sub(r',:', ':', text)
        # ,. or ,,. or ,,,. -> . (keep the period)
        text = re.sub(r',+\.', '.', text)
        # ?. or ?.. -> ? (question mark is already sentence-ending)
        text = re.sub(r'\?\.+', '?', text)
        # ?, or ?,. -> ? (comma/period after question mark is garbage)
        text = re.sub(r'\?[,.]+', '?', text)
        # !. or !.. -> !
        text = re.sub(r'!\.+', '!', text)
        # !, -> ! (comma after exclamation is garbage)
        text = re.sub(r'!,+', '!', text)
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
    
    def merge_brackets_with_formulas(self, text: str) -> str:
        """Merge parentheses with inline formulas.
        
        Converts ($formula$) to $(formula)$ so brackets render as part of formula.
        This prevents Word from breaking lines between bracket and formula.
        """
        # ($...$): -> $(...)$: - include trailing colon
        text = re.sub(r'\(\$([^$]+)\$\)([:;,.]?)', r'$(\1)\2$', text)
        # [$...$] -> $[...]$
        text = re.sub(r'\[\$([^$]+)\$\]([:;,.]?)', r'$[\1]\2$', text)
        return text
    
    def preprocess(self, text: str) -> str:
        """Apply all preprocessing steps."""
        text = self.fix_broken_table_lines(text)
        text = self.fix_indented_tables(text)
        text = self.fix_nested_list_indentation(text)
        text = self.merge_brackets_with_formulas(text)
        text = self.clean_text(text)
        return text
