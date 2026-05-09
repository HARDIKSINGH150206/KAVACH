# Contributing to KAVACH

Thank you for contributing to KAVACH. This repository is a prototype for offline dual-vector fraud detection with audio and SMS scoring.

## Getting Started

1. Create a Python 3.10+ virtual environment.
2. Install runtime dependencies:
   ```bash
   python -m venv kavach-env
   source kavach-env/bin/activate
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```
3. Install frontend dependencies:
   ```bash
   npm --prefix frontend install
   ```

## Quality Guidelines

- Run backend tests before opening a pull request: `./kavach-env/bin/python -m pytest tests/ -v`
- Run frontend tests before opening a pull request: `cd frontend && npm run test -- --run`
- Format Python files with `black` and `isort`: `pre-commit run --all-files`
- Use `ruff` to catch linting issues.

## Pull Requests

- Keep changes small and focused.
- Include tests for new behavior.
- Update documentation when adding or changing features.

## Reporting Issues

Please open issues for bugs, missing documentation, or feature requests. Include a clear description and reproduction steps.
