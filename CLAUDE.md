- My github username is beelzer.
- This project is a universal data scraper. Web, APIs, databases, the works.
- We use the latest python, and the best dependencies available.
- Never include attribution to or reference to claude, claude-code, anthropic, or AI in general in any commit messages
- Docker is available installed in WSL via Docker Desktop
- We are on Windows 11 using PyCharm 2025.2

## Setup Instructions (After Cloning/Copying Project)

When setting up this project after cloning or copying, run these initialization commands:

1. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

2. **Install Playwright browsers (for web scraping):**
   ```bash
   playwright install
   ```

3. **Sync Python dependencies:**
   ```bash
   uv sync --dev
   ```

4. **Verify setup:**
   ```bash
   scrap-e doctor
   ```
