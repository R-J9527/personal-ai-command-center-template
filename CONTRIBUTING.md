# Contributing to Personal AI Command Center Template

Thank you for your interest in contributing to this project!

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/personal-ai-command-center-template.git
   cd personal-ai-command-center-template
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

### Code Style
- Follow **PEP 8** guidelines
- Use **Black** for code formatting: `black .`
- Check code with **Flake8**: `flake8 .`
- Run **Pylint**: `pylint *.py`

### Testing
- Write tests for new features
- Run tests: `pytest`
- Ensure coverage doesn't decrease

### Commits
- Use clear, descriptive commit messages
- Reference issues when relevant: `Fixes #123`
- Keep commits atomic and focused

## Submitting a Pull Request

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes and commit them
3. Push to your fork: `git push origin feature/your-feature-name`
4. Open a Pull Request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/examples if applicable

## Privacy & Security

⚠️ **Important**: Never commit:
- Personal workspace data (`workspace/` directory)
- Credentials or API keys (use `.env` files)
- Calendar identifiers or health data
- Private project history

## Questions?

- Check existing [issues](../../issues) and [discussions](../../discussions)
- Open a new issue for bugs or feature requests
- Use discussions for questions

Thank you for contributing! 🎉
