#!/usr/bin/env python3
"""Pre-build script: wrap $...$ in {::nomarkdown}...{:/nomarkdown} to prevent kramdown
from processing underscores as Markdown emphasis inside inline math."""

import re
import sys
from pathlib import Path

# Regex to match inline math $...$ but NOT block math $$...$$
# We match $ followed by content that doesn't start with $, ending with $
# and not preceded or followed by $
INLINE_MATH = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', re.DOTALL)


def protect_file(filepath: Path) -> bool:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Find all matches, but we need to be careful about:
    # 1. $$...$$ blocks - don't touch these
    # 2. $ inside code blocks - skip these
    # 3. $ that's already inside {::nomarkdown}

    # Strategy: replace $$...$$ with a placeholder, process $...$, then restore
    display_math_blocks = []

    def save_display(m):
        display_math_blocks.append(m.group(0))
        return f'DISPLAYMATHPLACEHOLDER{len(display_math_blocks) - 1}END'

    # Protect $$...$$ blocks
    content = re.sub(r'\$\$.+?\$\$', save_display, content, flags=re.DOTALL)

    # Protect code blocks (```...```)
    code_blocks = []

    def save_code(m):
        code_blocks.append(m.group(0))
        return f'CODEBLOCKPLACEHOLDER{len(code_blocks) - 1}END'

    content = re.sub(r'```.*?```', save_code, content, flags=re.DOTALL)
    content = re.sub(r'`[^`]+`', save_code, content)

    # Now wrap remaining $...$ in {::nomarkdown}
    def wrap_inline(m):
        return '{::nomarkdown}$' + m.group(1) + '${:/nomarkdown}'

    content = INLINE_MATH.sub(wrap_inline, content)

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        content = content.replace(f'CODEBLOCKPLACEHOLDER{i}END', block)

    # Restore display math blocks
    for i, block in enumerate(display_math_blocks):
        content = content.replace(f'DISPLAYMATHPLACEHOLDER{i}END', block)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    dirs = sys.argv[1:] if len(sys.argv) > 1 else ['_research', '_resources', '_posts']
    count = 0
    for d in dirs:
        for md_file in Path(d).rglob('*.md'):
            if protect_file(md_file):
                count += 1
    print(f'Protected inline math in {count} files')


if __name__ == '__main__':
    main()
