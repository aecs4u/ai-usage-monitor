# AI Usage Monitor

**Track your AI coding assistant usage across Claude Code, Cline, Codex CLI, and more—with realtime monitoring, cost analytics, and beautiful terminal dashboards.**

[![PyPI Version](https://img.shields.io/pypi/v/ai-usage-monitor.svg)](https://pypi.org/project/ai-usage-monitor/)
[![Downloads](https://static.pepy.tech/badge/ai-usage-monitor/month)](https://pepy.tech/project/ai-usage-monitor)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![AI Usage Monitor Screenshot](https://raw.githubusercontent.com/aecs4u/ai-usage-monitor/main/doc/scnew.png)

## Why This Exists

AI coding assistants are incredibly powerful, but costs can add up quickly. This tool gives you **complete visibility** into your usage patterns across **9 different AI tools**, helping you:

- 💰 **Optimize spending** - See exactly where your tokens go
- 📊 **Track trends** - Month-over-month comparisons and projections
- 🎯 **Stay within limits** - Real-time monitoring with P90 limit detection
- 🔒 **Keep data local** - Everything runs offline, no data leaves your machine
- 🎨 **Beautiful dashboards** - Rich terminal UI with progress bars and tables

**Works with:** Claude Code, Cline, Codex CLI, Gemini CLI, Roo Code, Kilo Code, GitHub Copilot, OpenCode, Pi Agent

---

## Table of Contents

- [Why This Exists](#why-this-exists)
- [Key Features](#key-features)
- [Supported AI Tools](#supported-ai-tools)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command-Line Options](#command-line-options)
  - [View Modes](#view-modes)
  - [Date Range Filtering](#date-range-filtering)
  - [Configuration File](#configuration-file)
- [MCP Server Integration](#mcp-server-integration)
- [Subscription Plans & Savings](#subscription-plans--savings)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Community](#community)
- [License](#license)
- [Contributing](#contributing)

---

## Key Features

### v4.0.0 - Multi-Tool Support & Enhanced Analytics

- **Multi-Tool Monitoring** - Support for 9 AI coding tools (Claude Code, Codex CLI, Gemini CLI, Cline, Roo Code, Kilo Code, GitHub Copilot, OpenCode, Pi Agent)
- **Subscription Savings** - Calculate and display how much you save with subscription plans vs API pricing
- **Month-over-Month Comparison** - Track usage trends with delta calculations
- **Date Range Filtering** - Filter reports by custom date ranges (`--from-date`, `--to-date`)
- **MCP Server** - Integrate with AI assistants via Model Context Protocol
- **TOML Configuration** - Configure settings via `~/.ai-usage-monitor.toml`
- **Real-time Monitoring** - Configurable refresh rates (0.1-20 Hz)
- **Rich Terminal UI** - Beautiful color-coded progress bars and tables
- **P90 Analysis** - Machine learning-based limit detection
- **Cost Analytics** - Model-specific pricing with cache token calculations

---

## Supported AI Tools

| Tool | Data Format | Default Path |
|------|-------------|--------------|
| **Claude Code** | JSONL | `~/.claude/projects/` |
| **Codex CLI** | JSONL | `~/.codex/sessions/` |
| **Gemini CLI** | JSON | `~/.gemini/` |
| **Cline** | JSON | VS Code globalStorage |
| **Roo Code** | SQLite | VS Code globalStorage |
| **Kilo Code** | JSON | `~/.vscode/globalStorage/kilocode.kilo-code/` |
| **GitHub Copilot** | SQLite | VS Code workspaceStorage |
| **OpenCode** | JSON/TXT | `~/.local/share/opencode/` |
| **Pi Agent** | JSONL | `~/.pi/agent/sessions/` |

---

## Installation

### With uv (Recommended)

```bash
# Install from PyPI
uv tool install ai-usage-monitor

# Run from anywhere
ai-usage-monitor
```

### With pip

```bash
pip install ai-usage-monitor

# If command not found, add ~/.local/bin to PATH:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

ai-usage-monitor
```

### With pipx

```bash
pipx install ai-usage-monitor
ai-usage-monitor
```

### From Source

```bash
git clone https://github.com/aecs4u/ai-usage-monitor.git
cd ai-usage-monitor
uv tool install .
```

---

## Quick Start

```bash
# Monthly usage report (default - great for quick check)
ai-usage-monitor

# Monthly report with subscription savings (Max5 plan)
ai-usage-monitor --plan max5

# Real-time monitoring
ai-usage-monitor --view realtime

# Daily usage report
ai-usage-monitor --view daily

# Monitor specific tool
ai-usage-monitor --tool codex-cli

# Filter by date range
ai-usage-monitor --view daily --from-date 2025-01-01 --to-date 2025-01-15
```

### Command Aliases

The tool can be invoked using any of these commands:
- `ai-usage-monitor` (primary)
- `usage-monitor` (short)
- `um` (shortest)

---

## Usage

### Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--tool` | string | auto | Tool to monitor: `auto`, `all`, `claude-code`, `codex-cli`, `gemini-cli`, `cline`, `roo-code`, `kilo-code`, `github-copilot`, `opencode`, `pi-agent` |
| `--plan` | string | custom | Plan type: `pro`, `max5`, `max20`, `custom` |
| `--view` | string | monthly | View mode: `realtime`, `daily`, `monthly` |
| `--from-date` | string | None | Start date filter (YYYY-MM-DD) |
| `--to-date` | string | None | End date filter (YYYY-MM-DD) |
| `--timezone` | string | auto | Timezone (auto-detected) |
| `--theme` | string | auto | Display theme: `light`, `dark`, `classic`, `auto` |
| `--refresh-rate` | int | 10 | Data refresh rate in seconds (1-60) |
| `--custom-limit-tokens` | int | None | Token limit for custom plan |
| `--version`, `-v` | flag | - | Show version information |
| `--clear` | flag | - | Clear saved configuration |

### View Modes

#### Monthly View (Default)
Summary report with monthly aggregated usage data and subscription savings analysis. Great for quick checks of your overall usage.

#### Real-time View
Live monitoring with progress bars, current session data, and burn rate analysis.

```bash
ai-usage-monitor --view realtime
```

#### Daily View
Aggregated daily statistics with token breakdown and costs.

```bash
ai-usage-monitor --view daily --plan max5
```

Output includes:
- Daily token usage table
- Summary with total tokens and API-equivalent cost
- Subscription savings calculations (for Pro/Max5/Max20 plans)
- Data range indicator

#### Monthly View
Monthly aggregated data with month-over-month comparison.

```bash
ai-usage-monitor --view monthly --plan max5
```

Output includes:
- Monthly usage table
- Month-over-month comparison with deltas
- Subscription savings per month
- Overall trend analysis

### Date Range Filtering

Filter reports to specific date ranges:

```bash
# View January 2025 only
ai-usage-monitor --view daily --from-date 2025-01-01 --to-date 2025-01-31

# Last week
ai-usage-monitor --view daily --from-date 2025-01-16

# December 2024 monthly report
ai-usage-monitor --view monthly --from-date 2024-12-01 --to-date 2024-12-31
```

### Configuration File

Create `~/.ai-usage-monitor.toml` for persistent settings:

```toml
[general]
default_tool = "auto"
theme = "dark"
timezone = "America/New_York"
time_format = "12h"
refresh_rate = 10
plan = "max5"
view = "realtime"

[tools.claude-code]
enabled = true
data_path = "~/.claude/projects"

[tools.codex-cli]
enabled = true

[tools.cline]
enabled = false

[cloud]
url = ""
api_key = ""
auto_upload = false
```

---

## MCP Server Integration

AI Usage Monitor includes an MCP (Model Context Protocol) server for integration with AI assistants.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_daily_stats` | Get daily usage statistics |
| `get_model_usage` | Get usage breakdown by model |
| `get_cost_breakdown` | Get cost analysis by period |
| `compare_tools` | Compare usage across different tools |
| `list_available_tools` | List all available AI tools |

### Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "ai-usage-monitor": {
      "command": "ai-usage-monitor-mcp",
      "args": []
    }
  }
}
```

---

## Subscription Plans & Savings

The monitor tracks your API-equivalent usage and calculates savings for subscription plans.

### Plan Limits

| Plan | Token Limit | Monthly Price | Best For |
|------|-------------|---------------|----------|
| **Pro** | 19,000 | $20/mo | Light usage |
| **Max5** | 88,000 | $100/mo | Regular development |
| **Max20** | 220,000 | $200/mo | Heavy usage |
| **Custom** | P90-based | API pricing | Pay-as-you-go |

### Savings Display

When using `--plan max5` or `--plan max20`, the summary shows:

```
SUBSCRIPTION SAVINGS (MAX5 Plan)
   Subscription Cost: $200.00 (2 mo x $100)
   You Saved: $1,675.88 (89.3%)
```

The "Cost*" column in tables shows API-equivalent pricing, not your actual charges.

---

## Development

### From Source

```bash
git clone https://github.com/aecs4u/ai-usage-monitor.git
cd ai-usage-monitor

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest src/tests/ -v

# Run with coverage
pytest --cov=ai_usage_monitor --cov-report=html
```

### Project Structure

```
src/ai_usage_monitor/
├── adapters/           # Tool-specific adapters (9 tools)
├── cli/                # CLI entry point and bootstrap
├── core/               # Models, settings, plans, pricing
├── data/               # Data reading and aggregation
├── mcp/                # MCP server implementation
├── monitoring/         # Real-time session monitoring
├── terminal/           # Terminal management and themes
├── ui/                 # Display components and layouts
└── utils/              # Formatting, time utilities
```

---

## Troubleshooting

### No Data Found

1. Ensure the AI tool has been used and created usage data
2. Check the default data path exists (e.g., `~/.claude/projects/`)
3. Try specifying the tool explicitly: `--tool claude-code`

### Command Not Found

Add `~/.local/bin` to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Permission Errors

Use a virtual environment or `uv`/`pipx` instead of system pip:

```bash
uv tool install ai-usage-monitor
```

### Theme Issues

Force a specific theme if auto-detection fails:

```bash
ai-usage-monitor --theme dark
```

---

## Migration from claude-monitor

If upgrading from the old `claude-monitor` package:

1. Uninstall the old package:
   ```bash
   pip uninstall claude-monitor
   ```

2. Install the new package:
   ```bash
   pip install ai-usage-monitor
   ```

3. Update your shell aliases:
   ```bash
   # Old: claude-monitor, cmonitor, ccmonitor
   # New: ai-usage-monitor, usage-monitor, um
   ```

4. Configuration is automatically migrated from `~/.claude-monitor/` to `~/.ai-usage-monitor/`

---

## Community

We'd love to hear from you! Here's how to get involved:

- 💬 **[Discussions](https://github.com/aecs4u/ai-usage-monitor/discussions)** - Ask questions, share usage tips, request features
- 🐛 **[Issues](https://github.com/aecs4u/ai-usage-monitor/issues)** - Report bugs, track feature requests
- 🌟 **[Good First Issues](https://github.com/aecs4u/ai-usage-monitor/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)** - Start contributing to the project
- 📖 **[Contributing Guide](CONTRIBUTING.md)** - Learn how to help improve the project

**Star this repo** ⭐ if you find it useful! It helps others discover the project.

---

## License

[MIT License](LICENSE) - feel free to use and modify as needed.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Looking to contribute?** Check out issues labeled [`good first issue`](https://github.com/aecs4u/ai-usage-monitor/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) or [`help wanted`](https://github.com/aecs4u/ai-usage-monitor/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).

---

## Acknowledgments

Originally forked from [Maciek-roboblog/Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor).

---

<div align="center">

**Star this repo if you find it useful!**

[Report Bug](https://github.com/aecs4u/ai-usage-monitor/issues) | [Request Feature](https://github.com/aecs4u/ai-usage-monitor/issues)

</div>
