"""
Standalone CLI for converting Mermaid files to draw.io XML or HTML.

Usage:
    mermaid-to-drawio input.mmd                    # outputs XML to stdout
    mermaid-to-drawio input.mmd -o output.drawio   # saves .drawio file
    mermaid-to-drawio input.mmd --html             # outputs HTML div to stdout
    mermaid-to-drawio input.mmd --html -o out.html # saves HTML file
    cat input.mmd | mermaid-to-drawio -             # reads from stdin
"""

from __future__ import annotations

import argparse
import sys

from .converter import mermaid_to_html, mermaid_to_xml


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mermaid-to-drawio",
        description="Convert Mermaid diagrams to draw.io XML or HTML embeds.",
    )
    parser.add_argument(
        "input",
        help="Input .mmd file path, or '-' for stdin",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Output HTML embed div instead of raw XML",
    )

    args = parser.parse_args()

    # Read input
    if args.input == "-":
        text = sys.stdin.read()
    else:
        with open(args.input, encoding="utf-8") as f:
            text = f.read()

    # Convert
    if args.html:
        result = mermaid_to_html(text)
    else:
        result = mermaid_to_xml(text)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        sys.stdout.write(result)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
