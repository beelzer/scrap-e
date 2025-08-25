# Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Quick Setup

Configure Git to use our commit template:

```bash
git config --local commit.template .github/.gitmessage
```

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

Must be one of the following:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to our CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

## Scope

Optional. Can be anything specifying the place of the commit change:

- `api` - API-related changes
- `cli` - CLI interface changes
- `scrapers` - Scraper implementations
- `core` - Core functionality
- `web` - Web scraper specific
- `db` - Database scraper specific
- `auth` - Authentication related
- `docs` - Documentation
- `deps` - Dependencies
- `config` - Configuration files
- `tests` - Test files

## Subject

- Use imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize first letter
- No dot (.) at the end
- Limit to 50 characters

## Body

- Use imperative, present tense
- Include motivation for the change and contrast with previous behavior
- Wrap at 72 characters
- Can use multiple paragraphs separated by blank lines
- Can use bullet points (use `-` or `*`)

## Footer

- **Breaking changes**: Start with `BREAKING CHANGE:` followed by description
- **Issue references**: Use `Fixes #123`, `Closes #456`, `Refs #789`
- **Co-authors**: `Co-authored-by: name <email>`

## Examples

### Simple feature
```
feat(api): add rate limiting

Implement token bucket algorithm for API rate limiting.
Default limits: 100 requests per minute per IP.

Closes #123
```

### Bug fix with details
```
fix(scrapers): handle empty responses in web scraper

Previously, the web scraper would crash when receiving empty
responses from servers. Now it properly handles these cases
by returning an empty result set and logging a warning.

- Add null check for response body
- Return empty list instead of throwing exception
- Add debug logging for empty responses

Fixes #456
```

### Breaking change
```
refactor(core)!: change scraper interface

The base scraper class now requires implementing the
validate() method. All existing scrapers need to be updated.

BREAKING CHANGE: Scraper.scrape() now returns ScraperResult
instead of dict. Update all code that calls scraper.scrape()
to handle the new return type.

Refs #789
```

### Chore
```
chore(deps): update playwright to v1.40.0

Update Playwright for better Chrome compatibility
and performance improvements.
```

### Documentation
```
docs(readme): add troubleshooting section

Add common issues and their solutions to help
new users get started quickly.
```

## Automated Enforcement

This repository uses:
- **commitlint**: Validates commit messages in CI
- **pre-commit hooks**: Can validate commit messages locally
- **GitHub Actions**: Enforces convention on PR titles

## Tools

### Commitizen
For interactive commit message creation:
```bash
npm install -g commitizen
npm install -g cz-conventional-changelog
echo '{ "path": "cz-conventional-changelog" }' > ~/.czrc
git cz
```

### Validate a commit message
```bash
echo "feat(api): add endpoint" | npx commitlint
```

## Why Conventional Commits?

1. **Automatic CHANGELOG generation**: Tools can generate changelogs from commits
2. **Automatic version bumping**: Determine semantic version bumps based on commits
3. **Better communication**: Clear intent of changes
4. **Easier navigation**: Structured history is easier to search
5. **CI/CD triggers**: Can trigger different pipelines based on commit type
6. **Team alignment**: Everyone follows the same convention

## IDE Integration

### VS Code
Install the "Conventional Commits" extension for commit message helpers.

### PyCharm
1. Go to Settings → Version Control → Git
2. Set "Path to commit message template" to `.github/.gitmessage`

### Command Line
```bash
# Set for this repository only
git config --local commit.template .github/.gitmessage

# Set globally for all repositories
git config --global commit.template ~/.gitmessage
```
