"""
CLI.py
------
Command-line interface for pdf-encryptor.
Supports single-file encryption and batch directory processing.

Usage:
    python -m src.cli encrypt input.pdf output.pdf --password "secret"
    python -m src.cli batch ./pdfs ./encrypted --password "secret"
"""

import argparse
import sys
from src.encryptor import encrypt_pdf, batch_encrypt, SUPPORTED_ALGORITHMS, DEFAULT_ALGORITHM


def print_result(result: dict) -> None:
    """Print a single encryption result in a readable format."""
    if result["success"]:
        print(f"  ✓  {result['input']}  →  {result['output']}  ({result['pages']} pages)")
    else:
        print(f"  ✗  {result['input']}  —  ERROR: {result['error']}")


def cmd_encrypt(args: argparse.Namespace) -> None:
    """Handle the 'encrypt' subcommand."""
    print(f"\nEncrypting: {args.input}")

    result = encrypt_pdf(
        input_path=args.input,
        output_path=args.output,
        user_password=args.password,
        owner_password=args.owner_password,
        algorithm=args.algorithm,
        preserve_metadata=not args.no_metadata,
    )

    print_result(result)

    if not result["success"]:
        sys.exit(1)

    print("\nDone.\n")


def cmd_batch(args: argparse.Namespace) -> None:
    """Handle the 'batch' subcommand."""
    print(f"\nBatch encrypting PDFs in: {args.input_dir}")
    print(f"Output directory        : {args.output_dir}\n")

    results = batch_encrypt(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        user_password=args.password,
        owner_password=args.owner_password,
        algorithm=args.algorithm,
        preserve_metadata=not args.no_metadata,
    )

    if not results:
        print("No PDFs were processed.\n")
        return

    for result in results:
        print_result(result)

    succeeded = sum(1 for r in results if r["success"])
    failed = len(results) - succeeded

    print(f"\nSummary: {succeeded} succeeded, {failed} failed out of {len(results)} files.\n")

    if failed > 0:
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pdf-encryptor",
        description="Encrypt PDF files with AES-256 password protection.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Shared arguments factory ---
    def add_common_args(sub: argparse.ArgumentParser) -> None:
        sub.add_argument(
            "--password", "-p",
            required=True,
            help="User password to open the encrypted PDF.",
        )
        sub.add_argument(
            "--owner-password", "-op",
            default=None,
            dest="owner_password",
            help="Owner password for full permissions (default: same as --password).",
        )
        sub.add_argument(
            "--algorithm", "-a",
            choices=SUPPORTED_ALGORITHMS,
            default=DEFAULT_ALGORITHM,
            help=f"Encryption algorithm (default: {DEFAULT_ALGORITHM}).",
        )
        sub.add_argument(
            "--no-metadata",
            action="store_true",
            help="Skip copying metadata from source PDF.",
        )

    # --- encrypt subcommand ---
    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a single PDF file.",
    )
    encrypt_parser.add_argument("input",  help="Path to the source PDF.")
    encrypt_parser.add_argument("output", help="Path for the encrypted output PDF.")
    add_common_args(encrypt_parser)
    encrypt_parser.set_defaults(func=cmd_encrypt)

    # --- batch subcommand ---
    batch_parser = subparsers.add_parser(
        "batch",
        help="Encrypt all PDFs in a directory.",
    )
    batch_parser.add_argument("input_dir",  help="Directory containing source PDFs.")
    batch_parser.add_argument("output_dir", help="Directory for encrypted output PDFs.")
    add_common_args(batch_parser)
    batch_parser.set_defaults(func=cmd_batch)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
