#!/bin/bash
# Script to configure branch protection rules for Renovate integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up branch protection rules for Renovate integration...${NC}"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Not in a git repository. Please run this script from the repository root.${NC}"
    exit 1
fi

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo -e "${YELLOW}Repository: $REPO${NC}"

# Function to set branch protection
set_branch_protection() {
    local branch=$1
    echo -e "${GREEN}Configuring protection for branch: $branch${NC}"

    # Create the branch protection rule
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "/repos/$REPO/branches/$branch/protection" \
        -f "required_status_checks[strict]=true" \
        -f "required_status_checks[contexts][]=CI Status Summary" \
        -f "required_status_checks[contexts][]=Security Scan" \
        -f "enforce_admins=false" \
        -f "required_pull_request_reviews[dismiss_stale_reviews]=true" \
        -f "required_pull_request_reviews[require_code_owner_reviews]=false" \
        -f "required_pull_request_reviews[required_approving_review_count]=0" \
        -f "required_pull_request_reviews[require_last_push_approval]=false" \
        -f "restrictions=null" \
        -f "allow_force_pushes=false" \
        -f "allow_deletions=false" \
        -f "block_creations=false" \
        -f "required_conversation_resolution=true" \
        -f "lock_branch=false" \
        -f "allow_fork_syncing=true" \
        2>/dev/null || echo -e "${YELLOW}Note: Some settings may require admin permissions${NC}"

    # Enable auto-merge for the repository
    echo -e "${GREEN}Enabling auto-merge for repository...${NC}"
    gh api \
        --method PATCH \
        -H "Accept: application/vnd.github+json" \
        "/repos/$REPO" \
        -f "allow_auto_merge=true" \
        -f "allow_squash_merge=true" \
        -f "allow_merge_commit=false" \
        -f "allow_rebase_merge=false" \
        -f "delete_branch_on_merge=true" \
        2>/dev/null || echo -e "${YELLOW}Note: Repository settings may require admin permissions${NC}"
}

# Set protection for main branch
set_branch_protection "main"

# Set protection for develop branch if it exists
if git show-ref --verify --quiet refs/remotes/origin/develop; then
    set_branch_protection "develop"
fi

# Create labels for Renovate
echo -e "${GREEN}Creating labels for Renovate...${NC}"

create_label() {
    local name=$1
    local color=$2
    local description=$3

    gh label create "$name" --color "$color" --description "$description" 2>/dev/null || \
    gh label edit "$name" --color "$color" --description "$description" 2>/dev/null || \
    echo -e "${YELLOW}Label '$name' already exists or couldn't be updated${NC}"
}

# Create dependency-related labels
create_label "dependencies" "0366d6" "Pull requests that update a dependency file"
create_label "auto-merge" "00ff00" "PRs that will be automatically merged when checks pass"
create_label "do-not-merge" "ff0000" "PRs that should not be merged automatically"
create_label "security" "ee0701" "Security-related updates"
create_label "major-update" "ff9800" "Major version dependency updates"
create_label "minor-update" "fbca04" "Minor version dependency updates"
create_label "patch-update" "0e8a16" "Patch version dependency updates"
create_label "needs-rebase" "d93f0b" "PR needs to be rebased"
create_label "renovate" "027fa7" "Renovate bot PRs"
create_label "linting" "c5def5" "Linting and formatting tool updates"
create_label "testing" "bfd4f2" "Testing tool updates"
create_label "documentation" "0075ca" "Documentation tool updates"
create_label "ci" "2188ff" "Continuous Integration updates"
create_label "type-stubs" "d4c5f9" "Type stub package updates"

echo -e "${GREEN}Branch protection setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Ensure Renovate bot has write access to the repository"
echo "2. Check that the Renovate app is installed for your organization/repository"
echo "3. Verify the branch protection rules in Settings > Branches"
echo "4. Monitor the Dependency Dashboard issue once it's created"
echo ""
echo -e "${GREEN}To manually trigger Renovate for failing PRs, run:${NC}"
echo "  gh workflow run renovate-rebase.yml"
