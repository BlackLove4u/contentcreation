"""generate_content.py
Stubs for content generation: blog posts, scripts, social text.
"""

from typing import List


def make_blog(title: str, bullets: List[str]) -> str:
    body = f"# {title}\n\n"
    for b in bullets:
        body += f"- {b}\n"
    return body


def main_example():
    print(make_blog("Sample Title", ["point one", "point two"]))


if __name__ == "__main__":
    main_example()
