"""
Test_Encryptor.py
-----------------
Unit tests for the pdf-encryptor core module.
Uses temporary directories to avoid polluting the workspace.
"""

import os
import pytest
from pathlib import Path
from pypdf import PdfWriter, PdfReader

from src.encryptor import encrypt_pdf, batch_encrypt, SUPPORTED_ALGORITHMS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a minimal single-page PDF for testing."""
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return pdf_path


@pytest.fixture
def sample_pdf_dir(tmp_path: Path) -> Path:
    """Create a directory with 3 minimal PDFs for batch testing."""
    pdf_dir = tmp_path / "input_pdfs"
    pdf_dir.mkdir()
    for i in range(3):
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_dir / f"doc_{i+1}.pdf", "wb") as f:
            writer.write(f)
    return pdf_dir


# ---------------------------------------------------------------------------
# Single-file encryption tests
# ---------------------------------------------------------------------------

class TestEncryptPdf:

    def test_basic_encryption_succeeds(self, sample_pdf, tmp_path):
        """Encrypted file should be created at the specified output path."""
        output = tmp_path / "encrypted.pdf"
        result = encrypt_pdf(
            input_path=str(sample_pdf),
            output_path=str(output),
            user_password="test123",
        )
        assert result["success"] is True
        assert output.exists()

    def test_encrypted_file_is_readable_with_correct_password(self, sample_pdf, tmp_path):
        """pypdf should be able to open the encrypted file using the correct password."""
        output = tmp_path / "encrypted.pdf"
        encrypt_pdf(str(sample_pdf), str(output), user_password="secret")

        reader = PdfReader(str(output))
        assert reader.is_encrypted
        assert reader.decrypt("secret") is not None

    def test_result_contains_page_count(self, sample_pdf, tmp_path):
        """Result dict should report the correct page count."""
        output = tmp_path / "encrypted.pdf"
        result = encrypt_pdf(str(sample_pdf), str(output), user_password="pass")
        assert result["pages"] == 1

    def test_file_not_found_raises(self, tmp_path):
        """Should raise FileNotFoundError for a missing input file."""
        with pytest.raises(FileNotFoundError):
            encrypt_pdf(
                input_path="nonexistent.pdf",
                output_path=str(tmp_path / "out.pdf"),
                user_password="pass",
            )

    def test_invalid_algorithm_raises(self, sample_pdf, tmp_path):
        """Should raise ValueError for an unsupported algorithm."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            encrypt_pdf(
                input_path=str(sample_pdf),
                output_path=str(tmp_path / "out.pdf"),
                user_password="pass",
                algorithm="FAKE-512",
            )

    def test_all_supported_algorithms(self, sample_pdf, tmp_path):
        """Each supported algorithm should produce a valid encrypted file."""
        for algo in SUPPORTED_ALGORITHMS:
            output = tmp_path / f"encrypted_{algo}.pdf"
            result = encrypt_pdf(
                input_path=str(sample_pdf),
                output_path=str(output),
                user_password="pass",
                algorithm=algo,
            )
            assert result["success"] is True, f"Failed for algorithm: {algo}"
            assert output.exists()

    def test_output_directory_is_created(self, sample_pdf, tmp_path):
        """Output directory should be auto-created if it doesn't exist."""
        output = tmp_path / "new_subdir" / "encrypted.pdf"
        result = encrypt_pdf(str(sample_pdf), str(output), user_password="pass")
        assert result["success"] is True
        assert output.exists()

    def test_already_encrypted_pdf_returns_error(self, sample_pdf, tmp_path):
        """Re-encrypting an already-encrypted PDF should return an error result."""
        encrypted = tmp_path / "already_encrypted.pdf"
        encrypt_pdf(str(sample_pdf), str(encrypted), user_password="pass1")

        output = tmp_path / "re_encrypted.pdf"
        result = encrypt_pdf(str(encrypted), str(output), user_password="pass2")
        assert result["success"] is False
        assert "already encrypted" in result["error"].lower()


# ---------------------------------------------------------------------------
# Batch encryption tests
# ---------------------------------------------------------------------------

class TestBatchEncrypt:

    def test_batch_encrypts_all_pdfs(self, sample_pdf_dir, tmp_path):
        """All PDFs in the directory should be encrypted."""
        output_dir = tmp_path / "output"
        results = batch_encrypt(
            input_dir=str(sample_pdf_dir),
            output_dir=str(output_dir),
            user_password="batch_pass",
        )
        assert len(results) == 3
        assert all(r["success"] for r in results)

    def test_batch_missing_directory_raises(self, tmp_path):
        """Should raise FileNotFoundError for a missing input directory."""
        with pytest.raises(FileNotFoundError):
            batch_encrypt(
                input_dir=str(tmp_path / "ghost_dir"),
                output_dir=str(tmp_path / "out"),
                user_password="pass",
            )

    def test_batch_empty_directory_returns_empty_list(self, tmp_path):
        """Should return an empty list if no PDFs exist in the directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        results = batch_encrypt(
            input_dir=str(empty_dir),
            output_dir=str(tmp_path / "out"),
            user_password="pass",
        )
        assert results == []
