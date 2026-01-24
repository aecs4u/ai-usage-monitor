# AI Usage Monitor for VS Code

Monitor AI coding assistant usage directly in Visual Studio Code with beautiful dashboards, real-time tracking, and cost analysis.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![VS Code](https://img.shields.io/badge/VS%20Code-1.85.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

### 📊 Real-Time Monitoring

- **Overview Panel**: Current month summary with total tokens, costs, and sessions
- **Daily Usage View**: Detailed breakdown of last 7 days with expandable metrics
- **Monthly Usage View**: Historical data across all months
- **Tools Panel**: See which AI tools are available and active

### 📈 Visual Dashboards

- **Interactive Charts**: Line and bar charts for tokens and costs
- **Cost Analysis**: Subscription recommendations based on your usage
- **Trend Analysis**: Understand your usage patterns over time

### 🔧 Smart Features

- **Auto-Refresh**: Automatically update data at configurable intervals
- **Multi-Tool Support**: Monitor Claude Code, Cline, GitHub Copilot, and 7 other AI tools
- **Export Data**: Export usage data to JSON or CSV for external analysis
- **Cost Optimization**: Get subscription recommendations to save money

### 🎨 Native VS Code Integration

- **Activity Bar Icon**: Quick access from the sidebar
- **Command Palette**: All features accessible via `Cmd+Shift+P` / `Ctrl+Shift+P`
- **Tree Views**: Collapsible, hierarchical data visualization
- **Theme-Aware**: Adapts to your VS Code theme (light/dark)

## Screenshots

### Overview Panel
![Overview Panel](screenshots/overview.png)

### Dashboard with Charts
![Dashboard](screenshots/dashboard.png)

### Cost Analysis
![Cost Analysis](screenshots/cost-analysis.png)

## Requirements

- **VS Code**: Version 1.85.0 or higher
- **AI Usage Monitor CLI**: Install with `pip install ai-usage-monitor`
- **Python**: 3.9 or higher

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Go to Extensions (`Cmd+Shift+X` / `Ctrl+Shift+X`)
3. Search for "AI Usage Monitor"
4. Click Install

### From VSIX File

1. Download the latest `.vsix` file from [Releases](https://github.com/aecs4u/ai-usage-monitor/releases)
2. Open VS Code
3. Go to Extensions (`Cmd+Shift+X` / `Ctrl+Shift+X`)
4. Click "..." menu → "Install from VSIX..."
5. Select the downloaded file

### Install CLI Dependency

The extension requires the AI Usage Monitor CLI:

```bash
pip install ai-usage-monitor
```

## Quick Start

1. **Open the Extension**
   - Click the AI Usage Monitor icon in the Activity Bar
   - Or use Command Palette: `AI Usage Monitor: Show Dashboard`

2. **View Your Usage**
   - **Overview**: See current month summary
   - **Daily**: View last 7 days of usage
   - **Monthly**: Browse historical data
   - **Tools**: Check which AI tools are detected

3. **Explore Dashboards**
   - Click the graph icon in Overview panel
   - Or use Command Palette: `AI Usage Monitor: Show Dashboard`

4. **Analyze Costs**
   - Use Command Palette: `AI Usage Monitor: Show Cost Analysis`
   - Get subscription recommendations

## Usage

### Commands

Access all commands via Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):

| Command | Description |
|---------|-------------|
| `AI Usage Monitor: Refresh` | Refresh all usage data |
| `AI Usage Monitor: Show Dashboard` | Open visual dashboard with charts |
| `AI Usage Monitor: Export Data` | Export usage data to JSON/CSV |
| `AI Usage Monitor: Show Cost Analysis` | View cost breakdown and recommendations |
| `AI Usage Monitor: Configure Settings` | Open extension settings |
| `AI Usage Monitor: Select AI Tool` | Choose which AI tool to monitor |

### Toolbar Actions

Each view has toolbar buttons for quick actions:

- 🔄 **Refresh**: Update data
- 📊 **Dashboard**: Open charts (Overview panel)
- 📤 **Export**: Save data to file (Daily/Monthly panels)

### Tree View Navigation

- **Click** any month/day to expand details
- **Right-click** for context menu options
- **Collapse/Expand** sections as needed

## Configuration

Configure the extension in VS Code settings (`Cmd+,` / `Ctrl+,`):

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `aiUsageMonitor.enableAutoRefresh` | `true` | Auto-refresh usage data |
| `aiUsageMonitor.refreshInterval` | `60` | Refresh interval (seconds) |
| `aiUsageMonitor.defaultTool` | `auto` | Default AI tool to monitor |
| `aiUsageMonitor.showNotifications` | `true` | Show milestone notifications |
| `aiUsageMonitor.cliPath` | `""` | Custom CLI path (auto-detect if empty) |
| `aiUsageMonitor.timezone` | `auto` | Timezone for dates |

### Example Configuration

```json
{
  "aiUsageMonitor.enableAutoRefresh": true,
  "aiUsageMonitor.refreshInterval": 30,
  "aiUsageMonitor.defaultTool": "cline",
  "aiUsageMonitor.showNotifications": true
}
```

## Supported AI Tools

The extension monitors these AI coding assistants:

- ✅ **Claude Code** (Anthropic's official CLI)
- ✅ **Cline** (VS Code extension, formerly Claude Dev)
- ✅ **Codex CLI** (OpenAI)
- ✅ **Gemini CLI** (Google)
- ✅ **GitHub Copilot** (Microsoft)
- ✅ **Roo Code**
- ✅ **Kilo Code**
- ✅ **OpenCode**
- ✅ **Pi Agent**

## How It Works

1. **Data Collection**: The CLI monitors AI tool usage by reading local data files
2. **Processing**: Data is aggregated by day and month
3. **Visualization**: The extension displays data in tree views and charts
4. **Privacy**: All data stays on your machine - no cloud sync

## Troubleshooting

### "CLI Not Found" Error

**Problem**: Extension can't find the AI Usage Monitor CLI

**Solution**:
1. Install the CLI: `pip install ai-usage-monitor`
2. Verify installation: `ai-usage-monitor --version`
3. If using a custom Python environment, set `aiUsageMonitor.cliPath` in settings

### "No Data Available"

**Problem**: Extension shows no usage data

**Solution**:
1. Use an AI coding assistant to generate some data
2. Check that the CLI works: `ai-usage-monitor --view monthly`
3. Verify the tool is detected: Check the "Tools" panel
4. Try refreshing: Click the refresh button or use the command

### Auto-Refresh Not Working

**Problem**: Data doesn't update automatically

**Solution**:
1. Check `aiUsageMonitor.enableAutoRefresh` is `true`
2. Verify `aiUsageMonitor.refreshInterval` is reasonable (10-300 seconds)
3. Reload VS Code window

### Charts Not Displaying

**Problem**: Dashboard shows blank charts

**Solution**:
1. Ensure you have usage data (check tree views)
2. Try closing and reopening the dashboard
3. Check browser console for errors (Help → Toggle Developer Tools)

## Performance

The extension is designed to be lightweight:

- **Minimal CPU**: Only refreshes when needed
- **Low Memory**: Efficient data caching
- **Async Operations**: Non-blocking CLI calls
- **Lazy Loading**: Charts only load when dashboard opens

## Privacy & Security

- ✅ **No Telemetry**: Extension doesn't collect usage data
- ✅ **Local Only**: All data stays on your machine
- ✅ **No Network**: No external API calls (except Chart.js CDN for dashboards)
- ✅ **Open Source**: Full source code available

## Contributing

Contributions are welcome! See the main repository:

🔗 **GitHub**: https://github.com/aecs4u/ai-usage-monitor

### Development Setup

1. Clone the repository
2. Navigate to `vscode-extension/` directory
3. Install dependencies: `npm install`
4. Open in VS Code
5. Press `F5` to launch Extension Development Host
6. Make changes and test
7. Submit a pull request

### Build & Package

```bash
# Compile TypeScript
npm run compile

# Package extension
npm run package

# Publish to marketplace
npm run publish
```

## Roadmap

- [ ] Real-time monitoring view with live updates
- [ ] Custom alerts and notifications
- [ ] Budget tracking and warnings
- [ ] Team usage aggregation
- [ ] Integration with CI/CD pipelines
- [ ] Custom report generation

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

- 🐛 **Report Bugs**: [GitHub Issues](https://github.com/aecs4u/ai-usage-monitor/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/aecs4u/ai-usage-monitor/discussions)
- 📧 **Email**: See repository for contact info

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Acknowledgments

- Built with [VS Code Extension API](https://code.visualstudio.com/api)
- Charts powered by [Chart.js](https://www.chartjs.org/)
- Part of the [AI Usage Monitor](https://github.com/aecs4u/ai-usage-monitor) project

---

**Made with ❤️ for developers tracking their AI usage**

⭐ Star us on [GitHub](https://github.com/aecs4u/ai-usage-monitor)
