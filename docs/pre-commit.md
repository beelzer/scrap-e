# Pre-commit Hooks Guide

This project uses pre-commit hooks to ensure code quality and consistency.

## Installation

Pre-commit is already included in the dev dependencies:

```bash
# Install all dev dependencies including pre-commit
uv sync --extra dev

# Install the pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

## What's Included

### Code Quality Checks

- **Ruff**: Python linting and formatting
- **File fixes**: Trailing whitespace, end-of-file fixes, line endings
- **YAML/TOML validation**: Ensures configuration files are valid
- **JSON validation**: Checks JSON files for syntax errors
- **Large file detection**: Prevents accidentally committing large files
- **Merge conflict detection**: Catches unresolved merge conflicts

### Commit Standards

- **Conventional Commits**: Enforces conventional commit format (feat:, fix:, etc.)

## Running Manually

```bash
# Run on all files
uv run pre-commit run --all-files

# Run on specific hook
uv run pre-commit run ruff --all-files

# Update hooks to latest versions
uv run pre-commit autoupdate
```

## Bypassing Hooks

In rare cases where you need to bypass hooks:

```bash
# Skip pre-commit hooks
git commit --no-verify -m "your message"

# Skip specific hooks
SKIP=ruff git commit -m "your message"
```

## Conventional Commit Format

All commits must follow the conventional commit format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or changes
- `build`: Build system or dependency changes
- `ci`: CI/CD changes
- `chore`: Other changes that don't modify src or test files

### Examples

```bash
# Feature
git commit -m "feat: add rate limiting to web scraper"

# Bug fix with scope
git commit -m "fix(parser): handle empty HTML responses"

# Breaking change
git commit -m "feat!: change API response format

BREAKING CHANGE: API now returns JSON instead of XML"
```

## Troubleshooting

### Pre-commit not running

```bash
# Reinstall hooks
uv run pre-commit uninstall
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

### Hook failing repeatedly

```bash
# See detailed output
uv run pre-commit run --all-files --verbose

# Clean pre-commit cache
uv run pre-commit clean
```

## Configuration

Pre-commit configuration is in `.pre-commit-config.yaml`. Additional tool configurations:

- Ruff: `pyproject.toml` [tool.ruff] section
- YAML linting: `.yamllint.yml`
- Markdown linting: `.markdownlint.json`
