# GitHub Visibility Guide

This guide provides actionable steps to increase the project's visibility on GitHub and beyond.

## ✅ Quick Wins (Do These First!)

### 1. Repository Metadata

**Edit repository settings** (Settings → About):

- **Description**:
  ```
  Monitor AI tool usage (Claude Code, Cline, etc.) with realtime dashboards, cost tracking, and multi-tool aggregation
  ```

- **Website**: Link to documentation or PyPI page:
  ```
  https://github.com/aecs4u/ai-usage-monitor
  ```

- **Topics** (Add 10-12 for maximum discoverability):
  ```
  ai
  cli
  monitoring
  developer-tools
  tokens
  observability
  claude
  anthropic
  cost-tracking
  usage-analytics
  python-cli
  ai-observability
  ```

### 2. Enable GitHub Features

**In Settings → Features:**
- ✅ Enable **Discussions**
- ✅ Enable **Issues** (already enabled)
- ✅ Enable **Projects** (optional, for roadmap)
- ✅ Enable **Wiki** (optional, for extended docs)

### 3. Add Repository Shields

Already added to README:
- ✅ PyPI version badge
- ✅ Downloads badge
- ✅ Python version badge
- ✅ License badge
- ✅ PRs welcome badge
- ✅ Code style badge

**Consider adding:**
- GitHub stars: `![GitHub stars](https://img.shields.io/github/stars/aecs4u/ai-usage-monitor?style=social)`
- Latest release: `![GitHub release](https://img.shields.io/github/v/release/aecs4u/ai-usage-monitor)`
- Test status: Already via workflows

---

## 📝 Content Strategy

### 1. Create "Good First Issue" Labels

Create issues with clear scope and tag them appropriately:

**Example Issues:**

1. **Documentation improvements**
   - Label: `good first issue`, `documentation`
   - Title: "Add usage examples for Cline tool"
   - Description: Add 2-3 examples showing common Cline workflows

2. **Add adapter for new tool**
   - Label: `good first issue`, `enhancement`
   - Title: "Add adapter for [New Tool Name]"
   - Provide template and clear instructions

3. **Improve error messages**
   - Label: `good first issue`, `UX`
   - Title: "Make error message more helpful when no data found"
   - Describe specific error message to improve

4. **Add timezone to config examples**
   - Label: `good first issue`, `documentation`
   - Title: "Add timezone configuration examples to README"

5. **Create demo GIF/video**
   - Label: `good first issue`, `documentation`
   - Title: "Record asciicast demo of realtime monitoring"
   - Use asciinema to create terminal recording

**To create issues:**
```bash
gh issue create --label "good first issue,documentation" \
  --title "Add usage examples for Cline tool" \
  --body "We need more examples showing Cline-specific workflows..."
```

### 2. Add "Help Wanted" Issues

For features you'd like community help with:
- Export to different formats (CSV, JSON, Excel)
- Additional AI tool adapters
- Web dashboard frontend
- Performance optimizations
- Integration with other tools

---

## 🌍 Cross-Promotion Strategy

### 1. Social Media Announcements

**Reddit Posts:**

**r/Python:**
```markdown
Title: [Show] AI Usage Monitor - Track your AI coding assistant usage with beautiful CLI dashboards

I built a CLI tool to monitor AI coding assistant usage (Claude Code, Cline, Codex CLI, etc.)
after noticing my costs were climbing unexpectedly.

Features:
- Multi-tool support (9 different AI coding assistants)
- Real-time monitoring with configurable refresh rates
- Cost tracking and subscription savings calculations
- Beautiful terminal UI with progress bars
- Export capabilities
- MCP server integration
- Everything runs offline - no data leaves your machine

GitHub: https://github.com/aecs4u/ai-usage-monitor
PyPI: https://pypi.org/project/ai-usage-monitor/

Open source (MIT). Would love feedback and contributions!

[Screenshot of daily view]
```

**r/ClaudeAI:**
```markdown
Title: Monitor your Claude Code usage with this open-source CLI tool

Built a monitoring tool specifically designed for Claude Code (and other AI assistants).
Helps track token usage, costs, and identifies usage patterns.

- Real-time dashboards
- Daily/monthly reports
- Cost optimization insights
- Subscription savings calculator

Free and open source: https://github.com/aecs4u/ai-usage-monitor
```

**r/commandline:**
```markdown
Title: Beautiful CLI for monitoring AI coding assistant usage

Terminal-based monitoring tool with rich TUI for tracking AI usage across multiple tools.

GitHub: https://github.com/aecs4u/ai-usage-monitor
```

### 2. Hacker News

**Show HN Template:**
```markdown
Title: Show HN: AI Usage Monitor – Track your AI coding assistant usage

Hey HN! I built this after my AI coding assistant costs started climbing without me
noticing. It's a CLI tool that monitors usage across 9 different AI coding tools
(Claude Code, Cline, Codex CLI, etc.) with real-time dashboards.

Key features:
- Multi-tool support (Claude, Cline, Codex, Gemini, GitHub Copilot, etc.)
- Real-time monitoring with beautiful terminal UI
- Cost tracking and optimization recommendations
- Subscription savings calculations
- Offline-first (no data sent anywhere)
- MCP integration for AI assistants

Built with Python using Rich for the TUI. Open source (MIT).

Demo: [GIF/asciicast link]
GitHub: https://github.com/aecs4u/ai-usage-monitor

Would love feedback from the community!
```

### 3. Dev.to Article

**Title Ideas:**
- "Building a CLI to Track My AI Coding Assistant Costs"
- "How I Optimized My AI Tool Spending with Python"
- "Monitoring Multiple AI Coding Assistants with One Tool"

**Article Structure:**
1. Problem: Rising AI costs without visibility
2. Solution: Built a monitoring tool
3. Technical choices: Python, Rich, adapters pattern
4. Challenges overcome
5. Open source release
6. Call to action: Try it, contribute

### 4. Twitter/X Announcement

```markdown
🎉 Just released AI Usage Monitor v4.1.0!

Track your AI coding assistant usage (Claude Code, Cline, etc.) with:
- 📊 Real-time dashboards
- 💰 Cost optimization
- ⚡ 50%+ faster with incremental loading
- 🔒 Offline-first, privacy-focused

Open source (MIT)
👉 https://github.com/aecs4u/ai-usage-monitor

@AnthropicAI @ClaudeAI [screenshot]
```

---

## 📚 Community Building

### 1. GitHub Discussions Setup

**Create discussion categories:**
- 💡 Ideas (for feature requests)
- 🙏 Q&A (for user questions)
- 📢 Announcements (for releases)
- 🎉 Show and Tell (for user showcases)
- 💬 General

### 2. Welcome First-Time Contributors

Create `FIRST_TIMERS.md`:
```markdown
# Welcome First-Time Contributors! 👋

Thanks for your interest in contributing to AI Usage Monitor!

## Getting Started

1. Check out issues labeled [`good first issue`](link)
2. Read our [Contributing Guide](CONTRIBUTING.md)
3. Join our [Discussions](link) if you have questions
4. Fork, code, submit PR!

## Need Help?

- Ask in [Discussions](link)
- Comment on the issue you're working on
- Reach out to maintainers

We're here to help you succeed! 🎉
```

### 3. Respond to Issues/PRs Quickly

- Aim to respond to new issues within 24 hours
- Thank contributors for PRs
- Provide clear, constructive feedback
- Use labels effectively

---

## 📊 Tracking Success

### Metrics to Monitor

**GitHub:**
- Stars growth rate
- Issues/PRs activity
- Discussion engagement
- Unique visitors (Insights → Traffic)

**PyPI:**
- Total downloads
- Downloads per version
- Geographic distribution

**Community:**
- Active contributors
- Repeat contributors
- Community-driven features

### Tools

- **GitHub Insights** - Traffic, clones, popular content
- **PyPI Stats** - https://pepy.tech/project/ai-usage-monitor
- **Star History** - https://star-history.com

---

## 🎯 Quarterly Goals

### Q1 2025
- [ ] Reach 100 GitHub stars
- [ ] 10 community contributors
- [ ] 5 "good first issue" completions
- [ ] Featured in 1 tech newsletter/blog
- [ ] 1000+ monthly PyPI downloads

### Q2 2025
- [ ] 250 GitHub stars
- [ ] Listed in awesome-python
- [ ] 5000+ monthly downloads
- [ ] First community-contributed adapter

---

## 🔗 Link Building

### Add to Awesome Lists

Submit PRs to:
- [awesome-python](https://github.com/vinta/awesome-python) - CLI Development
- [awesome-cli](https://github.com/agarrharr/awesome-cli-apps) - Development
- [awesome-ai-tools](https://github.com/mahseema/awesome-ai-tools) - Monitoring
- [awesome-developer-tools](https://github.com/moimikey/awesome-devtools) - Productivity

### Package Registries

- ✅ PyPI (done)
- [ ] Homebrew formula (for macOS users)
- [ ] AUR package (for Arch Linux)
- [ ] Snap package (for Linux)

---

## 📧 Email Templates

### For Bloggers/Newsletters

```
Subject: New open-source CLI for AI usage monitoring

Hi [Name],

I recently released AI Usage Monitor, an open-source CLI tool for tracking
AI coding assistant usage across multiple tools (Claude Code, Cline, Codex CLI, etc.).

It helps developers:
- Monitor token usage and costs in real-time
- Optimize spending on AI tools
- Track usage patterns across 9 different AI assistants

Thought it might interest your readers at [Publication].

GitHub: https://github.com/aecs4u/ai-usage-monitor
Demo: [Link to demo/screenshot]

Happy to provide more details or answer questions!

Best,
[Your name]
```

---

## ✅ Action Checklist

Copy this to track progress:

**Repository Setup:**
- [ ] Update repository description
- [ ] Add website link
- [ ] Add 10+ topics
- [ ] Enable Discussions
- [ ] Create 5 "good first issue" labels
- [ ] Create 3 "help wanted" issues

**Content:**
- [ ] Post to r/Python
- [ ] Post to r/ClaudeAI
- [ ] Post to r/commandline
- [ ] Submit to Hacker News
- [ ] Write Dev.to article
- [ ] Tweet announcement

**Community:**
- [ ] Set up Discussion categories
- [ ] Create FIRST_TIMERS.md
- [ ] Respond to first 5 issues
- [ ] Thank first 3 contributors

**Link Building:**
- [ ] Submit to awesome-python
- [ ] Submit to awesome-cli
- [ ] Create Homebrew formula
- [ ] Reach out to 3 tech bloggers/newsletters

---

## Need Help?

Questions about this guide? Open an issue or discussion!
