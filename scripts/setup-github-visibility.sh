#!/bin/bash
# Script to set up GitHub repository for maximum visibility
# Requires: gh CLI (GitHub CLI)

set -e

echo "🚀 Setting up GitHub repository for maximum visibility..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo "❌ Not logged into GitHub CLI. Please run: gh auth login"
    exit 1
fi

echo ""
echo "${BLUE}Step 1: Setting repository topics...${NC}"
gh repo edit --add-topic ai
gh repo edit --add-topic cli
gh repo edit --add-topic monitoring
gh repo edit --add-topic developer-tools
gh repo edit --add-topic tokens
gh repo edit --add-topic observability
gh repo edit --add-topic claude
gh repo edit --add-topic anthropic
gh repo edit --add-topic cost-tracking
gh repo edit --add-topic usage-analytics
gh repo edit --add-topic python-cli
gh repo edit --add-topic ai-observability
echo "${GREEN}✅ Topics added${NC}"

echo ""
echo "${BLUE}Step 2: Enabling GitHub Discussions...${NC}"
gh repo edit --enable-discussions || echo "⚠️  Discussions may already be enabled or require manual setup"
echo "${GREEN}✅ Discussions enabled${NC}"

echo ""
echo "${BLUE}Step 3: Creating labels for issues...${NC}"

# Create labels if they don't exist
gh label create "good first issue" --description "Good for newcomers" --color "7057ff" --force
gh label create "help wanted" --description "Extra attention is needed" --color "008672" --force
gh label create "documentation" --description "Improvements or additions to documentation" --color "0075ca" --force
gh label create "enhancement" --description "New feature or request" --color "a2eeef" --force
gh label create "UX" --description "User experience improvements" --color "d4c5f9" --force

echo "${GREEN}✅ Labels created${NC}"

echo ""
echo "${BLUE}Step 4: Setting repository description...${NC}"
gh repo edit --description "Monitor AI tool usage (Claude Code, Cline, etc.) with realtime dashboards, cost tracking, and multi-tool aggregation"
echo "${GREEN}✅ Description set${NC}"

echo ""
echo "${BLUE}Step 5: Creating example 'good first issue'...${NC}"

# Create a sample good first issue
gh issue create \
  --title "Add timezone configuration examples to README" \
  --label "good first issue,documentation" \
  --body "## Description

We need to add clear examples showing how to configure timezone settings in the README.

## Tasks
- [ ] Add example showing how to set timezone in ~/.ai-usage-monitor.toml
- [ ] Show common timezone values (UTC, America/New_York, Europe/London, etc.)
- [ ] Explain the 'auto' option for automatic detection

## Example Section Location
In the 'Configuration File' section of the README, after the basic configuration example.

## Resources
- Current config docs: [Configuration File section](../README.md#configuration-file)
- Timezone utils: src/ai_usage_monitor/utils/time_utils.py

## Why This is a Good First Issue
- Clear scope (just documentation)
- No code changes required
- Helps new users understand an important feature
- Good introduction to the project structure

Feel free to ask questions in the comments!" \
  || echo "⚠️  Issue creation skipped (may already exist)"

echo "${GREEN}✅ Example issue created${NC}"

echo ""
echo "🎉 ${GREEN}GitHub visibility setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Enable Discussions manually if it failed: Settings → Features → Discussions"
echo "  2. Add a website URL: Settings → About → Website"
echo "  3. Create more 'good first issue' items"
echo "  4. Announce on social media (see docs/GITHUB_VISIBILITY_GUIDE.md)"
echo ""
echo "📚 Full guide: docs/GITHUB_VISIBILITY_GUIDE.md"
