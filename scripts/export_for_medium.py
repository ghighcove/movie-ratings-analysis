#!/usr/bin/env python3
"""
Export markdown article to Medium-compatible HTML with unique timestamped filenames.

This script generates cache-busting filenames to avoid Medium's aggressive caching issue
where it serves old cached content when the same filename is reused.

Usage:
    python scripts/export_for_medium.py article/medium_draft.md
"""

import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


def generate_unique_filename(article_name: str, html_content: str) -> str:
    """
    Generate unique timestamped filename to bypass Medium's aggressive caching.

    Format: {article_name}_{YYYYMMDD}_{HHMM}_{hash}.html
    Example: rating_inflation_20260212_0845_a3f2b1c4.html

    Args:
        article_name: Base name for the article (e.g., "rating_inflation")
        html_content: Full HTML content to hash

    Returns:
        Unique filename string
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    content_hash = hashlib.md5(html_content.encode()).hexdigest()[:8]
    return f"{article_name}_{timestamp}_{content_hash}.html"


def markdown_to_html(markdown_content: str, github_pages_base: str, repo_name: str) -> str:
    """
    Convert markdown to Medium-compatible HTML.

    Medium requirements:
    - Images must use absolute URLs (GitHub Pages URLs work)
    - Images should be wrapped in <p> tags
    - Basic markdown formatting (headers, bold, italic, links)

    Args:
        markdown_content: Raw markdown text
        github_pages_base: Base URL for GitHub Pages (e.g., "https://ghighcove.github.io")
        repo_name: Repository name (e.g., "movie-ratings-analysis")

    Returns:
        HTML string ready for Medium import
    """
    html = markdown_content

    # Convert markdown images to HTML with GitHub Pages URLs
    # Pattern: ![caption](../figures/fig.png) or ![caption](figures/fig.png)
    # Target: <p><img src="https://ghighcove.github.io/movie-ratings-analysis/figures/fig.png" alt="caption"></p>
    def replace_image(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        # Remove leading ../ if present
        if img_path.startswith('../'):
            img_path = img_path[3:]
        github_url = f"{github_pages_base}/{repo_name}/{img_path}"
        return f'<p><img src="{github_url}" alt="{alt_text}"></p>'

    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, html)

    # Convert headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # Convert bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Wrap paragraphs (lines that don't start with <)
    lines = html.split('\n')
    processed_lines = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if in_paragraph:
                processed_lines.append('</p>')
                in_paragraph = False
            processed_lines.append('')
            continue

        # Skip lines that are already HTML tags
        if stripped.startswith('<'):
            if in_paragraph:
                processed_lines.append('</p>')
                in_paragraph = False
            processed_lines.append(line)
            continue

        # Start or continue paragraph
        if not in_paragraph:
            processed_lines.append('<p>')
            in_paragraph = True

        processed_lines.append(line)

    if in_paragraph:
        processed_lines.append('</p>')

    html = '\n'.join(processed_lines)

    # Clean up multiple empty lines
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html


def export_article_for_medium(
    markdown_path: str,
    output_dir: str,
    github_pages_base: str = "https://ghighcove.github.io",
    repo_name: str = "movie-ratings-analysis"
) -> Tuple[str, str]:
    """
    Export markdown article to Medium-compatible HTML with unique filename.

    Args:
        markdown_path: Path to source markdown file
        output_dir: Directory to write HTML file
        github_pages_base: Base URL for GitHub Pages
        repo_name: Repository name for constructing image URLs

    Returns:
        Tuple of (local_file_path, github_pages_url)
    """
    # Read markdown
    markdown_path = Path(markdown_path)
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Convert to HTML
    html_content = markdown_to_html(markdown_content, github_pages_base, repo_name)

    # Generate unique filename
    article_name = markdown_path.stem  # e.g., "medium_draft"
    # Clean up the name if needed
    if article_name == "medium_draft":
        article_name = "rating_inflation"

    filename = generate_unique_filename(article_name, html_content)

    # Write HTML file
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Generate GitHub Pages URL
    github_url = f"{github_pages_base}/{repo_name}/article/{filename}"

    print(f"Exported to: {output_path}")
    print(f"File size: {output_path.stat().st_size:,} bytes")
    print(f"GitHub Pages URL: {github_url}")
    print()
    print("Next steps:")
    print(f"1. git add article/{filename}")
    print(f"2. git commit -m 'Add Medium export: {article_name}'")
    print("3. git push origin main")
    print("4. Wait 30 seconds for GitHub Pages rebuild")
    print("5. Import to Medium using the GitHub Pages URL above")

    return str(output_path), github_url


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/export_for_medium.py <markdown_file>")
        print("Example: python scripts/export_for_medium.py article/medium_draft.md")
        sys.exit(1)

    markdown_path = sys.argv[1]
    output_dir = "article"

    export_article_for_medium(markdown_path, output_dir)


if __name__ == '__main__':
    main()
