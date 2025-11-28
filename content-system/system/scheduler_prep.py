"""scheduler_prep.py
Prepare content artifacts for scheduler ingestion.
"""

import os


def prepare_for_instagram(post_text: str, image_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "instagram_post.txt")
    with open(out_path, "w") as f:
        f.write(post_text)
    return out_path


if __name__ == "__main__":
    p = prepare_for_instagram(
        "Caption here", "image.jpg", "../scheduler_ready/instagram/"
    )
    print(p)
