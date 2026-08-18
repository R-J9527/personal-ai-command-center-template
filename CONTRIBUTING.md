# Contributing to Personal AI Command Center Template

Thank you for helping improve the template. Keep contributions aligned with
the repository's current scope: a portable specification, a standalone HTML
dashboard, example data, and a standard-library Python renderer.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/personal-ai-command-center-template.git
   cd personal-ai-command-center-template
   ```

3. **Optionally create a virtual environment for formatting and linting**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   python3 -m pip install -r requirements-dev.txt
   ```

The renderer has no third-party runtime dependencies.

## Development Workflow

### Validation

Run the checks that exist in this repository:

```bash
python3 -m compileall -q skills/build-personal-command-center/scripts

temp_dir="$(mktemp -d)"
python3 skills/build-personal-command-center/scripts/render_workbench.py \
  --data skills/build-personal-command-center/assets/workbench.example.json \
  --template skills/build-personal-command-center/assets/dashboard-template.html \
  --output "$temp_dir/personal-command-center.html"

test -s "$temp_dir/personal-command-center.html"
if grep -q '__WORKBENCH_DATA__' "$temp_dir/personal-command-center.html"; then
  echo "Unresolved dashboard marker" >&2
  exit 1
fi
```

When the optional development tools are installed, Python changes should also
pass:

```bash
black --check skills/build-personal-command-center/scripts
ruff check skills/build-personal-command-center/scripts
```

If a contribution adds a new runtime dependency, explain why the standard
library is insufficient before adding it. If it adds tests, document the real
test command at the same time.

### Commits
- Use clear, descriptive commit messages
- Reference issues when relevant: `Fixes #123`
- Keep commits atomic and focused

## Submitting a Pull Request

1. Create a feature branch: `git switch -c feature/your-feature-name`
2. Make your changes and commit them
3. Push to your fork: `git push origin feature/your-feature-name`
4. Open a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/examples if applicable

## Privacy & Security

⚠️ **Important**: Never commit:
- Personal workspace data (`workspace/` directory)
- Credentials or API keys (use `.env` files)
- Calendar identifiers or health data
- Private project history

## Scope and licensing

This repository currently does not grant an open-source license. Do not add or
change licensing terms without the repository owner's explicit approval.

For questions, open an issue without including private workspace data.
