#!/bin/bash
# Helper script for submitting AI Usage Monitor to awesome lists
# This script guides you through the submission process

set -e

echo "🌟 Awesome Lists Submission Helper"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed. Please install it first:${NC}"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not logged into GitHub CLI. Please run: gh auth login${NC}"
    exit 1
fi

# Check GitHub stars
echo -e "${BLUE}Checking GitHub stars...${NC}"
STARS=$(gh repo view aecs4u/ai-usage-monitor --json stargazerCount -q .stargazerCount)
echo -e "${GREEN}Current stars: ${STARS}${NC}"

if [ "$STARS" -lt 50 ]; then
    echo -e "${YELLOW}⚠️  Warning: You have fewer than 50 stars.${NC}"
    echo "   Some awesome lists prefer projects with more stars."
    echo "   Consider waiting until you have 50-100+ stars for better acceptance."
    echo ""
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        echo "Exiting. Come back when you have more stars!"
        exit 0
    fi
fi

echo ""
echo -e "${BLUE}Which awesome list would you like to submit to?${NC}"
echo "  1. awesome-python (220k+ stars)"
echo "  2. awesome-cli-apps (15k+ stars)"
echo "  3. awesome-ai-tools (10k+ stars)"
echo "  4. All of them"
echo ""
read -p "Enter choice (1-4): " choice

# Function to submit to awesome-python
submit_awesome_python() {
    echo ""
    echo -e "${BLUE}📝 Submitting to awesome-python...${NC}"
    echo ""

    REPO="vinta/awesome-python"
    BRANCH="add-ai-usage-monitor"

    # Check if already forked
    if gh repo view "$USER/awesome-python" &> /dev/null; then
        echo -e "${YELLOW}Fork already exists. Using existing fork.${NC}"
    else
        echo "Forking repository..."
        gh repo fork $REPO --clone=false
    fi

    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo ""
    echo "1. Clone your fork:"
    echo "   ${BLUE}gh repo clone $USER/awesome-python && cd awesome-python${NC}"
    echo ""
    echo "2. Create a branch:"
    echo "   ${BLUE}git checkout -b $BRANCH${NC}"
    echo ""
    echo "3. Edit README.md:"
    echo "   Find section: ${YELLOW}Command-line Tools → Productivity Tools${NC}"
    echo "   Add (alphabetically):"
    echo "   ${BLUE}* [ai-usage-monitor](https://github.com/aecs4u/ai-usage-monitor) - Track AI coding assistant usage with real-time dashboards, cost tracking, and multi-tool aggregation.${NC}"
    echo ""
    echo "4. Commit and push:"
    echo "   ${BLUE}git add README.md${NC}"
    echo "   ${BLUE}git commit -m \"Add ai-usage-monitor to Productivity Tools\"${NC}"
    echo "   ${BLUE}git push origin $BRANCH${NC}"
    echo ""
    echo "5. Create PR:"
    echo "   ${BLUE}gh pr create --title \"Add ai-usage-monitor\" --body \"Adds ai-usage-monitor, a CLI tool for tracking AI coding assistant usage with real-time dashboards and cost optimization. Published on PyPI, MIT license, ${STARS}+ stars.\"${NC}"
    echo ""
    read -p "Press Enter when done (or Ctrl+C to skip)..."
}

# Function to submit to awesome-cli-apps
submit_awesome_cli() {
    echo ""
    echo -e "${BLUE}📝 Submitting to awesome-cli-apps...${NC}"
    echo ""

    REPO="agarrharr/awesome-cli-apps"
    BRANCH="add-ai-usage-monitor"

    # Check if already forked
    if gh repo view "$USER/awesome-cli-apps" &> /dev/null; then
        echo -e "${YELLOW}Fork already exists. Using existing fork.${NC}"
    else
        echo "Forking repository..."
        gh repo fork $REPO --clone=false
    fi

    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo ""
    echo "1. Clone your fork:"
    echo "   ${BLUE}gh repo clone $USER/awesome-cli-apps && cd awesome-cli-apps${NC}"
    echo ""
    echo "2. Create a branch:"
    echo "   ${BLUE}git checkout -b $BRANCH${NC}"
    echo ""
    echo "3. Edit README.md:"
    echo "   Find section: ${YELLOW}Development → Devops${NC}"
    echo "   Add (alphabetically):"
    echo "   ${BLUE}- [ai-usage-monitor](https://github.com/aecs4u/ai-usage-monitor) - Monitor AI coding assistant usage with real-time dashboards and cost optimization.${NC}"
    echo ""
    echo "4. Commit and push:"
    echo "   ${BLUE}git add README.md${NC}"
    echo "   ${BLUE}git commit -m \"Add ai-usage-monitor\"${NC}"
    echo "   ${BLUE}git push origin $BRANCH${NC}"
    echo ""
    echo "5. Create PR:"
    echo "   ${BLUE}gh pr create --title \"Add ai-usage-monitor\" --body \"Adds ai-usage-monitor, a terminal-based monitoring tool for AI coding assistants. Features real-time dashboards, multi-tool support, and privacy-first operation.\"${NC}"
    echo ""
    read -p "Press Enter when done (or Ctrl+C to skip)..."
}

# Function to submit to awesome-ai-tools
submit_awesome_ai() {
    echo ""
    echo -e "${BLUE}📝 Submitting to awesome-ai-tools...${NC}"
    echo ""

    REPO="mahseema/awesome-ai-tools"
    BRANCH="add-ai-usage-monitor"

    # Check if already forked
    if gh repo view "$USER/awesome-ai-tools" &> /dev/null; then
        echo -e "${YELLOW}Fork already exists. Using existing fork.${NC}"
    else
        echo "Forking repository..."
        gh repo fork $REPO --clone=false
    fi

    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo ""
    echo "1. Clone your fork:"
    echo "   ${BLUE}gh repo clone $USER/awesome-ai-tools && cd awesome-ai-tools${NC}"
    echo ""
    echo "2. Create a branch:"
    echo "   ${BLUE}git checkout -b $BRANCH${NC}"
    echo ""
    echo "3. Edit README.md:"
    echo "   Find section: ${YELLOW}Developer Tools${NC} (or create ${YELLOW}Monitoring & Analytics${NC} subsection)"
    echo "   Add:"
    echo "   ${BLUE}- [AI Usage Monitor](https://github.com/aecs4u/ai-usage-monitor) - Track AI coding assistant usage across multiple tools with real-time dashboards, cost optimization, and privacy-first monitoring.${NC}"
    echo ""
    echo "4. Commit and push:"
    echo "   ${BLUE}git add README.md${NC}"
    echo "   ${BLUE}git commit -m \"Add AI Usage Monitor to Developer Tools\"${NC}"
    echo "   ${BLUE}git push origin $BRANCH${NC}"
    echo ""
    echo "5. Create PR:"
    echo "   ${BLUE}gh pr create --title \"Add AI Usage Monitor\" --body \"Adds AI Usage Monitor, a monitoring and analytics tool for AI coding assistants. Tracks usage across 9 tools including Claude Code, Cline, GitHub Copilot, etc.\"${NC}"
    echo ""
    read -p "Press Enter when done (or Ctrl+C to skip)..."
}

# Process choice
case $choice in
    1)
        submit_awesome_python
        ;;
    2)
        submit_awesome_cli
        ;;
    3)
        submit_awesome_ai
        ;;
    4)
        submit_awesome_python
        submit_awesome_cli
        submit_awesome_ai
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Fork(s) created!${NC}"
echo ""
echo -e "${BLUE}📚 For detailed instructions, see:${NC}"
echo "   docs/AWESOME_LIST_SUBMISSIONS.md"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  • Follow each repo's contributing guidelines"
echo "  • Test that your changes render correctly"
echo "  • Be patient - reviews can take 1-2 weeks"
echo "  • Respond promptly to feedback"
echo ""
echo -e "${GREEN}Good luck! 🚀${NC}"
