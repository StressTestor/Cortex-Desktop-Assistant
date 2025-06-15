# Contributing to Cortex Desktop Assistant

Thank you for your interest in contributing to Cortex Desktop Assistant! We welcome all contributions, whether they're bug reports, feature requests, documentation improvements, or code contributions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/yourusername/cortex-desktop-assistant.git
   cd cortex-desktop-assistant
   ```
3. **Set up your development environment**
   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```
4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

2. **Make your changes** following the project's coding style:
   - Use type hints for all function parameters and return values
   - Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
   - Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
   - Keep commits small and focused on a single feature/bugfix

3. **Run code formatters and linters**:
   ```bash
   # Auto-format code
   black .
   
   # Sort imports
   isort .
   
   # Check for type errors
   mypy .
   
   # Check for style issues
   flake8
   ```

4. **Update documentation** if your changes affect user-facing features

5. **Commit your changes** with a clear and descriptive commit message:
   ```
   feat: add new TTS engine integration
   
   - Add support for NewTTS engine
   - Update configuration options
   - Add tests for new functionality
   ```

6. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a pull request** against the `main` branch

## Reporting Issues

When reporting issues, please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Any relevant error messages or logs

## Code Review Process

1. A maintainer will review your PR and may request changes
2. Once approved, your PR will be merged into the main branch
3. The changes will be included in the next release

## Development Dependencies

- Python 3.10+
- [Poetry](https://python-poetry.org/) (for dependency management)
- [pre-commit](https://pre-commit.com/) (for git hooks)

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
