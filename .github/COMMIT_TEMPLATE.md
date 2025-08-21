# <type>: <subject> (Max 50 chars, no period at end)
# |<----  Using a maximum of 50 characters  ---->|

# Explain why this change is being made (wrap at 72 chars)
# |<----   Try to limit each line to 72 characters   ---->|

# Provide links or keys to any relevant tickets, issues, or resources
# Example: Fixes #123, Related to #456

# --- COMMIT END ---
# Type can be:
#   feat     (new feature)
#   fix      (bug fix)
#   refactor (refactoring code)
#   style    (formatting, missing semicolons, etc; no code change)
#   docs     (changes to documentation)
#   test     (adding or refactoring tests; no production code change)
#   perf     (performance improvements)
#   chore    (updating grunt tasks etc; no production code change)
#   build    (changes to build system or dependencies)
#   ci       (changes to CI configuration)
#
# Remember:
#   - Use imperative mood ("Add feature" not "Added feature")
#   - Do not end subject with period
#   - Separate subject from body with blank line
#   - Use body to explain what and why vs. how
#   - Can use multiple lines with "-" or "*" for bullet points
#
# Example:
# feat: Add rate limiting to web scraper
#
# Implement token bucket algorithm for rate limiting HTTP requests.
# This prevents overwhelming target servers and reduces the chance
# of being blocked.
#
# - Add RateLimiter class with configurable rates
# - Integrate with HttpScraper and BrowserScraper
# - Add configuration options for requests per second/minute
#
# Fixes #42
