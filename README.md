# PDF Encryptor

> A lightweight Python tool to password-protect PDFs with AES-256, batch support and a clean CLI.

---

## Features

- **AES-256 encryption** (default) — with fallback support for AES-128, RC4-128, RC4-40
- **Separate user & owner passwords** — control who can open vs. who has full permissions
- **Metadata preservation** — copies author, title and subject from source PDF
- **Batch mode** — encrypt all PDFs in a directory in one command
- **Clean CLI** — intuitive subcommands with helpful error messages
- **Importable Python API** — use `encrypt_pdf()` directly in your own scripts

---


## Installation

**Requirements:** Python 3.10+

```bash
# 1. Clone the repository
git clone https://github.com/AdarshZolekar/PDF-Encryptor.git
cd PDF-Encryptor

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r Requirements.txt
```

---

## Usage

### CLI — Single File

```bash
python -m src.cli encrypt input.pdf encrypted.pdf --password "your_password"
```

With optional flags:

```bash
python -m src.cli encrypt input.pdf encrypted.pdf \
  --password "user_pass" \
  --owner-password "owner_pass" \
  --algorithm AES-256 \
  --no-metadata
```

### CLI — Batch Directory

```bash
python -m src.cli batch ./pdfs/ ./encrypted_pdfs/ --password "batch_password"
```

**Example output:**
```
Batch encrypting PDFs in: ./pdfs/
Output directory        : ./encrypted_pdfs/

  ✓  pdfs/report.pdf       →  encrypted_pdfs/report.pdf       (12 pages)
  ✓  pdfs/invoice.pdf      →  encrypted_pdfs/invoice.pdf      (3 pages)
  ✗  pdfs/locked.pdf       —  ERROR: 'locked.pdf' is already encrypted.

Summary: 2 succeeded, 1 failed out of 3 files.
```

### Python API

```python
from src.encryptor import encrypt_pdf, batch_encrypt

# Single file
result = encrypt_pdf(
    input_path="report.pdf",
    output_path="report_encrypted.pdf",
    user_password="open123",
    owner_password="admin456",
    algorithm="AES-256",
)
print(result)
# {'success': True, 'input': 'report.pdf', 'output': 'report_encrypted.pdf', 'pages': 12, 'error': None}

# Batch
results = batch_encrypt(
    input_dir="./pdfs",
    output_dir="./encrypted",
    user_password="secret",
)
```

---

## CLI Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--password` | `-p` | User password to open the PDF *(required)* |
| `--owner-password` | `-op` | Owner password for full permissions |
| `--algorithm` | `-a` | Encryption algorithm (default: `AES-256`) |
| `--no-metadata` | — | Skip copying metadata from source |

**Supported algorithms:** `AES-256`, `AES-128`, `RC4-128`, `RC4-40`

---

## Running Tests

```bash
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Technologies

| Tool | Purpose |
|------|---------|
| [pypdf](https://pypdf.readthedocs.io/) | PDF reading, writing, and encryption |
| [pytest](https://pytest.org/) | Testing framework |
| Python 3.10+ | Language runtime |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes using clear messages (see below)
4. Push and open a Pull Request

**Commit message conventions:**
```
feat: add support for decryption mode
fix: handle already-encrypted PDFs gracefully
test: add edge case for empty batch directory
docs: update CLI usage examples
refactor: split encryption logic into helper functions
```

---

## License

This project is open-source under the MIT License.

---

## Contributions

Contributions are welcome!

- Open an issue for bugs or feature requests

- Submit a pull request for improvements.


<p align="center">
  <a href="#top">
    <img src="https://img.shields.io/badge/%E2%AC%86-Back%20to%20Top-blue?style=for-the-badge" alt="Back to Top"/>
  </a>
</p>

