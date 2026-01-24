#!/bin/bash
# Script to create "good first issue" items for the repository
# Requires: gh CLI (GitHub CLI)

set -e

echo "🎯 Creating 'good first issue' items..."

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
echo "${BLUE}Creating Issue 1: Add timezone examples to README...${NC}"
gh issue create \
  --title "Add timezone configuration examples to README" \
  --label "good first issue,documentation" \
  --body "## 📝 Description

We need to add clear examples showing how to configure timezone settings in the README.

## 🎯 Tasks
- [ ] Add example showing how to set timezone in \`~/.ai-usage-monitor.toml\`
- [ ] Show common timezone values (UTC, America/New_York, Europe/London, Asia/Tokyo, etc.)
- [ ] Explain the 'auto' option for automatic detection
- [ ] Add command-line timezone override examples

## 📍 Location
In the **Configuration File** section of the README, after the basic configuration example.

## 📚 Resources
- Current config docs: [Configuration File section](../README.md#configuration-file)
- Timezone utils: \`src/ai_usage_monitor/utils/time_utils.py\`
- Time format detection: \`get_system_timezone()\` function

## 💡 Why This is a Good First Issue
- Clear scope (just documentation)
- No code changes required
- Helps new users understand an important feature
- Good introduction to the project structure

## ✅ Acceptance Criteria
- [ ] TOML config example includes timezone setting
- [ ] At least 5 common timezones shown as examples
- [ ] 'auto' option is explained
- [ ] Command-line override example included

Feel free to ask questions in the comments! We're here to help. 😊" \
  2>/dev/null && echo "${GREEN}✅ Issue 1 created${NC}" || echo "⚠️  Issue 1 may already exist"

echo ""
echo "${BLUE}Creating Issue 2: Create terminal demo recording...${NC}"
gh issue create \
  --title "Create asciinema demo of realtime monitoring" \
  --label "good first issue,documentation,demo" \
  --body "## 📝 Description

We need a beautiful terminal recording (asciinema) showing the realtime monitoring feature in action.

## 🎯 Tasks
- [ ] Install asciinema (\`pip install asciinema\`)
- [ ] Record a 30-60 second demo of \`ai-usage-monitor --view realtime\`
- [ ] Show the monitoring dashboard with live updates
- [ ] Demonstrate token usage, burn rate, and progress bars
- [ ] Upload to asciinema.org
- [ ] Add link to README (create new \"Demo\" section)

## 📍 What to Record
1. Start with command: \`ai-usage-monitor --view realtime\`
2. Let it run for 30-60 seconds showing live updates
3. Exit cleanly with Ctrl+C

## 🎨 Tips for Great Recording
- Use a dark terminal theme for consistency
- Set terminal size to 120x30 for readability
- Clear terminal before recording (\`clear\`)
- Optional: Use \`asciinema rec --cols 120 --rows 30 demo.cast\`

## 📚 Resources
- asciinema: https://asciinema.org/
- Recording guide: https://asciinema.org/docs/getting-started
- Example recording: \`asciinema rec demo.cast\`

## 💡 Why This is a Good First Issue
- Fun and visual task
- Easy to verify (just watch the recording!)
- No code changes needed
- Helps users understand the tool before installing
- Great way to contribute without coding

## ✅ Acceptance Criteria
- [ ] Recording is 30-60 seconds long
- [ ] Shows realtime view with live updates
- [ ] Good terminal contrast (readable text)
- [ ] Uploaded to asciinema.org
- [ ] Link added to README in new \"Demo\" section

Questions? Ask away! 🚀" \
  2>/dev/null && echo "${GREEN}✅ Issue 2 created${NC}" || echo "⚠️  Issue 2 may already exist"

echo ""
echo "${BLUE}Creating Issue 3: Improve error message for no data found...${NC}"
gh issue create \
  --title "Improve error message when no usage data is found" \
  --label "good first issue,UX,enhancement" \
  --body "## 📝 Description

When users run the tool but have no data files, the error message could be more helpful by suggesting next steps.

## 🎯 Current Behavior
\`\`\`
No data available for claude-code
\`\`\`

## 🎯 Desired Behavior
\`\`\`
No usage data found for Claude Code

Possible reasons:
  • No data files exist yet (use the tool to generate data)
  • Data directory not found: ~/.claude/projects/
  • Tool may not be installed or hasn't been used

Try:
  • Use Claude Code to generate some usage data
  • Check if data path is correct: ai-usage-monitor --tool claude-code --help
  • Try another tool: ai-usage-monitor --tool all

For more help: https://github.com/aecs4u/ai-usage-monitor/discussions
\`\`\`

## 📍 Location
File: \`src/ai_usage_monitor/cli/main.py\`
Function: \`_run_monitoring()\` around line 285

## 📚 Resources
- Current error message: Line 285 in main.py
- Display function: \`print_themed()\` from terminal module
- Example helpful errors: Search for \"No data\" in codebase

## 💡 Why This is a Good First Issue
- Small scope (one error message)
- Immediate user impact
- Easy to test (just run with no data)
- Good introduction to the CLI code
- Improves user experience

## ✅ Acceptance Criteria
- [ ] Error message is more descriptive
- [ ] Includes possible reasons for no data
- [ ] Suggests actionable next steps
- [ ] Links to help resources
- [ ] Maintains consistent formatting with other messages

Need help getting started? Just ask! 👋" \
  2>/dev/null && echo "${GREEN}✅ Issue 3 created${NC}" || echo "⚠️  Issue 3 may already exist"

echo ""
echo "${BLUE}Creating Issue 4: Add usage examples for Cline tool...${NC}"
gh issue create \
  --title "Add Cline-specific usage examples to README" \
  --label "good first issue,documentation" \
  --body "## 📝 Description

Add concrete examples showing how to monitor Cline (VS Code extension) usage specifically.

## 🎯 Tasks
- [ ] Add Cline examples to Quick Start section
- [ ] Show how to find Cline data location
- [ ] Demonstrate filtering Cline data by date
- [ ] Add troubleshooting tip for Cline data location
- [ ] Optional: Add screenshot of Cline monitoring

## 📍 Examples to Add

\`\`\`bash
# Monitor Cline usage
ai-usage-monitor --tool cline

# View Cline daily usage
ai-usage-monitor --tool cline --view daily

# Export Cline data
ai-usage-monitor --tool cline --export json --export-path cline_usage.json
\`\`\`

## 📍 Location
Add to README.md in the \"Quick Start\" section, after the basic examples

## 📚 Resources
- Cline adapter: \`src/ai_usage_monitor/adapters/implementations/cline.py\`
- Cline data location: VS Code globalStorage
- Supported AI Tools table in README

## 💡 Why This is a Good First Issue
- Documentation only
- Helps Cline users specifically
- Clear scope and acceptance criteria
- No code changes needed
- Good for someone familiar with Cline

## ✅ Acceptance Criteria
- [ ] At least 3 Cline-specific examples added
- [ ] Data location clearly documented
- [ ] Export example included
- [ ] Formatting matches existing examples
- [ ] Examples are tested and work

Questions about Cline or how to contribute? Ask below! 💬" \
  2>/dev/null && echo "${GREEN}✅ Issue 4 created${NC}" || echo "⚠️  Issue 4 may already exist"

echo ""
echo "${BLUE}Creating Issue 5: Add cost optimization tips to documentation...${NC}"
gh issue create \
  --title "Add cost optimization tips and best practices" \
  --label "good first issue,documentation,enhancement" \
  --body "## 📝 Description

Create a new documentation section with practical tips for optimizing AI tool costs based on usage data.

## 🎯 Tasks
- [ ] Create new file: \`docs/COST_OPTIMIZATION_TIPS.md\`
- [ ] Add tips for identifying expensive usage patterns
- [ ] Show how to use burn rate to predict costs
- [ ] Explain subscription savings calculator
- [ ] Add examples of reading exported data
- [ ] Link from main README

## 💡 Suggested Content

**Topics to cover:**
1. Understanding the data
   - What the numbers mean
   - How costs are calculated
   - Cache token savings

2. Identifying expensive patterns
   - High burn rate sessions
   - Comparing daily/monthly trends
   - Month-over-month growth

3. Optimization strategies
   - When to use subscriptions vs API
   - Leveraging prompt caching
   - Monitoring session lengths

4. Using export data
   - Analyzing in Excel/Python
   - Setting up alerts
   - Creating custom reports

## 📚 Resources
- Burn rate calculation: \`src/ai_usage_monitor/core/calculations.py\`
- Pricing calculator: \`src/ai_usage_monitor/core/pricing.py\`
- Export functionality: \`src/ai_usage_monitor/utils/export.py\`
- Subscription plans: \`src/ai_usage_monitor/core/plans.py\`

## 💡 Why This is a Good First Issue
- Creative documentation task
- Helps users save money (high impact!)
- No code changes required
- Can draw from personal experience
- Good for someone with AI tool usage experience

## ✅ Acceptance Criteria
- [ ] New file created: \`docs/COST_OPTIMIZATION_TIPS.md\`
- [ ] At least 5 practical tips included
- [ ] Examples with real numbers
- [ ] Linked from main README
- [ ] Well-formatted markdown
- [ ] Includes screenshots or examples

Share your cost optimization experiences! 💰" \
  2>/dev/null && echo "${GREEN}✅ Issue 5 created${NC}" || echo "⚠️  Issue 5 may already exist"

echo ""
echo "${BLUE}Creating Issue 6: Add comparison table of AI tools...${NC}"
gh issue create \
  --title "Create comparison table of supported AI tools" \
  --label "good first issue,documentation" \
  --body "## 📝 Description

Add a comparison table showing features, pricing models, and characteristics of each supported AI tool.

## 🎯 Tasks
- [ ] Research pricing for each supported tool
- [ ] Identify key differentiating features
- [ ] Create markdown table
- [ ] Add to new section in README
- [ ] Include links to official docs

## 📊 Table Structure

| Tool | Provider | Model(s) | Pricing | Subscription | Cache Support |
|------|----------|----------|---------|--------------|---------------|
| Claude Code | Anthropic | Sonnet, Opus | API + Subscription | Yes (Max5, Max20) | Yes |
| Cline | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |

## 📍 Location
Add new section \"Tool Comparison\" after \"Supported AI Tools\" in README

## 📚 Resources
- Adapters directory: \`src/ai_usage_monitor/adapters/implementations/\`
- Each adapter has metadata about the tool
- Official tool websites for pricing
- Supported tools table in README

## 💡 Why This is a Good First Issue
- Research-focused task
- Helps users choose tools
- No code changes needed
- Can be done incrementally
- Good for someone who uses multiple AI tools

## ✅ Acceptance Criteria
- [ ] Table includes all 9 supported tools
- [ ] Pricing information is current and accurate
- [ ] Links to official docs included
- [ ] Table is well-formatted
- [ ] Added to README in logical location

Research and compare away! 🔍" \
  2>/dev/null && echo "${GREEN}✅ Issue 6 created${NC}" || echo "⚠️  Issue 6 may already exist"

echo ""
echo "🎉 ${GREEN}Good first issues created!${NC}"
echo ""
echo "View all issues:"
echo "  gh issue list --label \"good first issue\""
echo ""
echo "Or visit:"
echo "  https://github.com/aecs4u/ai-usage-monitor/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22"
