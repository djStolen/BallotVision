# BallotVision

BallotVision is an automated verification tool designed to ensure the integrity of election protocol data. By using image processing (OCR) and mathematical rule validation, it detects inconsistencies in scanned election documents.

## Getting Started

This project utilizes a containerized development environment via **DevPod** to ensure identical results across different machines.

### Prerequisites
*   [DevPod](https://devpod.sh/) installed and configured on your host machine.
*   Docker (or a container runtime supported by DevPod).

### Installation
1.  Clone the repository.
2.  Make the control script executable:
```bash
chmod +x run.sh
```

## Development Workflow

We use a central `run.sh` script to manage the development lifecycle. This script automatically handles container lifecycle, testing, and linting.

| Command | Description |
| :--- | :--- |
| `./run.sh test` | Runs the full test suite via `pytest`. |
| `./run.sh lint` | Checks code formatting with `black` and `flake8`. |
| `./run.sh docs` | Generates project documentation using Doxygen. |
| `./run.sh shell` | Opens an interactive bash terminal inside the container. |

## Project Structure

```text
BallotVision/
├── .devcontainer/
│   └── Dockerfile               # Local development container configuration
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions continuous integration pipeline
├── src/
│   └── ballot_vision/
│       ├── __init__.py
│       ├── core/
│       │   └── models.py        # Core data models (ElectionProtocol, etc.)
│       ├── ocr/
│       │   ├── base.py          # Abstract base class for OCR engines
│       │   └── paddle_engine.py # PaddleOCR engine implementation with memory fixes
│       └── validation/
│           └── rules.py         # Business logic validation rules for protocols
├── tests/
│   ├── test_environment.py      # Basic environment verification tests
│   ├── test_ocr.py              # OCR engine initialization and processing tests
│   └── testfiles/               # Sample ballot PDFs and generated OCR data
├── pyproject.toml               # Tooling configs (pytest/coverage) & package metadata
├── requirements.txt             # Pinned package dependency list for CI and environments
├── process_files.py             # Batch CLI tool to run OCR over a target folder
└── run.sh                       # Automation script for running the test suite
```

# Testing

The project uses pytest for validation logic. To run the tests, simply execute:

```bash
./run.sh test
```
Tests are automatically executed inside the container environment, ensuring that OpenCV and other system dependencies are correctly linked.

# Run on test files

```bash
PYTHONPATH=src python3 process_files.py ./tests/testfiles/
```
