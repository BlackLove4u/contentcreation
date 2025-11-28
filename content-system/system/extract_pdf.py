"""extract_pdf.py
PDF text extraction stub.
"""

import argparse


def extract_pdf(pdf_path: str, out_dir: str):
    print(f"(stub) extracting text from {pdf_path} -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("--pdf", help="PDF file path")
    parser.add_argument(
        "--out",
        default="../extracted/text/",
        help="Output directory",
    )
    args = parser.parse_args()
    extract_pdf(args.pdf, args.out)


if __name__ == "__main__":
    main()
