# BallotVision

BallotVision is an automated verification tool designed to ensure the integrity of election protocol data. By using image processing (OCR) and mathematical rule validation, it detects inconsistencies in scanned election documents (*Записник*).

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
├── .devcontainer/      # Container configuration
├── src/
│   └── ballot_vision/  # Source code
│       ├── core/       # Data models and logic
│       └── validation/ # Validation rules (ProtocolValidator)
├── tests/              # Pytest suites and fixtures
├── docs/               # Documentation output
├── run.sh              # Project control script
└── pyproject.toml      # Project metadata and pytest configuration
```

# Testing

The project uses pytest for validation logic. To run the tests, simply execute:

```bash
./run.sh test
```
Tests are automatically executed inside the container environment, ensuring that OpenCV and other system dependencies are correctly linked.

