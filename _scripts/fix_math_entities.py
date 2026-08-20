#!/usr/bin/env python3
"""Post-build script: unescape HTML entities inside math blocks so KaTeX can render them."""

import re
import sys
import os
from pathlib import Path

def fix_math_in_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix display math: \[ ... \]
    def fix_display(m):
        inner = m.group(1)
        inner = inner.replace('&lt;', '<')
        inner = inner.replace('&gt;', '>')
        inner = inner.replace('&amp;', '&')
        return r'\[' + inner + r'\]'

    content = re.sub(r'\\\[(.*?)\\\]', fix_display, content, flags=re.DOTALL)

    # Fix inline math: $ ... $
    def fix_inline(m):
        inner = m.group(1)
        inner = inner.replace('&lt;', '<')
        inner = inner.replace('&gt;', '>')
        inner = inner.replace('&amp;', '&')
        return '$' + inner + '$'

    content = re.sub(r'\$(.*?)\$', fix_inline, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    site_dir = sys.argv[1] if len(sys.argv) > 1 else '_site'
    count = 0
    for html_file in Path(site_dir).rglob('*.html'):
        if fix_math_in_html(str(html_file)):
            count += 1
    print(f'Fixed math entities in {count} files')

if __name__ == '__main__':
    main()
