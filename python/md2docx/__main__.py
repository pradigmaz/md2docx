"""
CLI entry point for md2docx.

Usage:
    python -m md2docx input.md output.docx
    python -m md2docx input.md output.docx --settings '{"fontSize": 12}'
"""

import argparse
import json

from .converter import Md2DocxConverter


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to DOCX with LaTeX support"
    )
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output DOCX file")
    parser.add_argument(
        "--settings", "-s",
        type=str,
        default="{}",
        help="JSON formatting settings"
    )
    
    args = parser.parse_args()
    
    try:
        settings = json.loads(args.settings)
    except json.JSONDecodeError:
        settings = {}
    
    converter = Md2DocxConverter(args.input, args.output, settings)
    converter.convert()


if __name__ == "__main__":
    main()
