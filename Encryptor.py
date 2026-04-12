"""
Encryptor.py
------------
Core PDF encryption logic using pypdf.
Supports AES-256 encryption, metadata preservation,
and both single-file and batch processing.
"""

import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter


# Supported encryption algorithms
SUPPORTED_ALGORITHMS = ["AES-256", "AES-128", "RC4-128", "RC4-40"]
DEFAULT_ALGORITHM = "AES-256"


def encrypt_pdf(
    input_path: str,
    output_path: str,
    user_password: str,
    owner_password: str = None,
    algorithm: str = DEFAULT_ALGORITHM,
    preserve_metadata: bool = True,
) -> dict:
    """
    Encrypt a single PDF file with a password.

    Args:
        input_path      : Path to the source PDF file.
        output_path     : Path where the encrypted PDF will be saved.
        user_password   : Password required to open the PDF.
        owner_password  : Password for full permissions (defaults to user_password).
        algorithm       : Encryption algorithm. Defaults to AES-256.
        preserve_metadata: Whether to copy metadata from source PDF.

    Returns:
        dict: Result summary with keys — success, input, output, pages, error.

    Raises:
        FileNotFoundError : If the input PDF does not exist.
        ValueError        : If the algorithm is not supported.
    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(
            f"Unsupported algorithm '{algorithm}'. "
            f"Choose from: {', '.join(SUPPORTED_ALGORITHMS)}"
        )

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.suffix.lower() == ".pdf":
        raise ValueError(f"Input file is not a PDF: {input_path}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        reader = PdfReader(str(input_path))

        # Handle already-encrypted PDFs
        if reader.is_encrypted:
            raise ValueError(
                f"'{input_path.name}' is already encrypted. "
                "Decrypt it first before re-encrypting."
            )

        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Preserve original metadata if requested
        if preserve_metadata and reader.metadata:
            writer.add_metadata(reader.metadata)

        # Apply encryption
        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password or user_password,
            algorithm=algorithm,
        )

        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return {
            "success": True,
            "input": str(input_path),
            "output": str(output_path),
            "pages": len(reader.pages),
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "input": str(input_path),
            "output": None,
            "pages": 0,
            "error": str(exc),
        }


def batch_encrypt(
    input_dir: str,
    output_dir: str,
    user_password: str,
    owner_password: str = None,
    algorithm: str = DEFAULT_ALGORITHM,
    preserve_metadata: bool = True,
) -> list[dict]:
    """
    Encrypt all PDF files in a directory.

    Args:
        input_dir        : Directory containing PDFs to encrypt.
        output_dir       : Directory where encrypted PDFs will be saved.
        user_password    : Password required to open each PDF.
        owner_password   : Password for full permissions.
        algorithm        : Encryption algorithm. Defaults to AES-256.
        preserve_metadata: Whether to copy metadata from each source PDF.

    Returns:
        list[dict]: List of result summaries (one per PDF found).

    Raises:
        FileNotFoundError: If input_dir does not exist.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    pdf_files = sorted(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {input_dir}")
        return []

    results = []
    for pdf_file in pdf_files:
        output_path = output_dir / pdf_file.name
        result = encrypt_pdf(
            input_path=str(pdf_file),
            output_path=str(output_path),
            user_password=user_password,
            owner_password=owner_password,
            algorithm=algorithm,
            preserve_metadata=preserve_metadata,
        )
        results.append(result)

    return results
