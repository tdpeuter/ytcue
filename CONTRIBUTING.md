# Contributing to ytcue

Thank you for your interest in contributing to `ytcue`! We welcome contributions from everyone.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/YOUR_USERNAME/ytcue.git
    cd ytcue
    ```
3.  **Install the development environment**:
    We use `uv` for dependency management.
    ```bash
    uv sync
    ```
4.  **Create a new branch** for your feature or bugfix:
    ```bash
    git checkout -b feature/your-feature-name
    ```

## Development Workflow

### Code Style

We use `ruff` for linting and formatting. Please ensure your code passes these checks before submitting a PR.

```bash
uv run ruff check .
uv run ruff format .
```

### Type Checking

We use `mypy` for static type checking.

```bash
uv run mypy src
```

### Testing

We use `pytest` for testing. Please ensure all tests pass and add new tests for any new features.

```bash
uv run pytest
```

## Submitting a Pull Request

1.  **Commit your changes** with descriptive commit messages.
2.  **Push to your fork**:
    ```bash
    git push origin feature/your-feature-name
    ```
3.  **Open a Pull Request** on the main repository.

## Feedback and Questions

If you have any questions or feedback, please open an issue on GitHub.
