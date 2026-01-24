# Changelog

All notable changes to the AI Usage Monitor VS Code extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-24

### Added

#### Core Features
- Initial release of AI Usage Monitor for VS Code
- Activity bar integration with custom icon
- Four tree view panels: Overview, Daily Usage, Monthly Usage, and Tools

#### Monitoring Capabilities
- Real-time usage tracking for 9 AI coding assistants
- Auto-refresh with configurable interval (10-300 seconds)
- Token usage breakdown (input, output, cache creation, cache read)
- Cost tracking and analysis
- Session counting

#### Visualization
- Interactive dashboard with Chart.js integration
- Daily token usage chart (line chart, last 14 days)
- Daily cost chart (bar chart, last 14 days)
- Monthly token usage chart (bar chart)
- Monthly cost chart (line chart)
- Theme-aware charts (adapts to VS Code theme)

#### Cost Analysis
- Dedicated cost analysis panel
- Subscription recommendation engine
- Savings calculator for Max5 and Max20 plans
- Usage trend analysis
- Cost projection for next month

#### Data Management
- Export to JSON with full metadata
- Export to CSV for spreadsheet analysis
- Save dialog integration
- Custom export path configuration

#### Commands
- `aiUsageMonitor.refresh` - Refresh all usage data
- `aiUsageMonitor.showDashboard` - Open visual dashboard
- `aiUsageMonitor.exportData` - Export usage data
- `aiUsageMonitor.showCosts` - Show cost analysis
- `aiUsageMonitor.configure` - Open settings
- `aiUsageMonitor.selectTool` - Select AI tool to monitor

#### Configuration
- `enableAutoRefresh` - Toggle auto-refresh (default: true)
- `refreshInterval` - Set refresh interval in seconds (default: 60)
- `defaultTool` - Choose default AI tool (default: auto)
- `showNotifications` - Toggle milestone notifications (default: true)
- `cliPath` - Custom CLI path (default: auto-detect)
- `timezone` - Timezone for dates (default: auto)

#### Supported Tools
- Claude Code (Anthropic)
- Cline (VS Code extension)
- Codex CLI (OpenAI)
- Gemini CLI (Google)
- GitHub Copilot (Microsoft)
- Roo Code
- Kilo Code
- OpenCode
- Pi Agent

#### User Experience
- Collapsible tree views with expand/collapse
- Toolbar actions for quick access
- Context menus for tree items
- Tooltips with detailed information
- Loading states and error handling
- "CLI not found" guidance
- "No data available" helpful messages

#### Technical
- TypeScript implementation
- Async/await for CLI operations
- Efficient data caching
- Memory-optimized tree providers
- Non-blocking UI operations
- Error recovery and fallback handling

### Technical Details

#### Architecture
- Extension host activation on startup
- CLI manager for subprocess communication
- Separate providers for each tree view
- Webview panels for dashboards
- Event-driven refresh mechanism

#### Performance
- Lazy loading of chart libraries
- Minimal CPU usage (only on refresh)
- Efficient JSON parsing
- Cached tree data
- Debounced configuration changes

#### Privacy
- No telemetry collection
- Local data processing only
- No external API calls (except Chart.js CDN)
- No user data transmission

### Dependencies

#### Runtime
- VS Code Engine: ^1.85.0
- Node.js: 20.x
- TypeScript: ^5.3.3

#### Development
- @types/vscode: ^1.85.0
- @types/node: 20.x
- @typescript-eslint/eslint-plugin: ^6.15.0
- @typescript-eslint/parser: ^6.15.0
- eslint: ^8.56.0
- @vscode/test-electron: ^2.3.8
- @vscode/vsce: ^2.22.0

#### External (CDN)
- Chart.js: 4.4.0 (for dashboards)

### Known Issues

None at this time.

### Breaking Changes

None (initial release).

## [Unreleased]

### Planned Features
- Real-time monitoring view with live updates
- Custom alerts when usage exceeds thresholds
- Budget tracking and warnings
- Team usage aggregation
- Integration with CI/CD pipelines
- Custom report generation
- Notification center for milestones
- Export to PDF format
- Comparison between time periods
- Cost forecasting with ML

### Under Consideration
- Integration with GitHub Actions
- Slack/Discord notifications
- Multi-workspace support
- Custom dashboard widgets
- API for external integrations

---

## Version History

- **1.0.0** (2025-01-24) - Initial release

---

## Upgrading

To upgrade to the latest version:

1. Open VS Code
2. Go to Extensions
3. Find "AI Usage Monitor"
4. Click "Update" if available

Or use the command line:
```bash
code --install-extension aecs4u.ai-usage-monitor --force
```

## Migration Guide

### From CLI Only to Extension

If you've been using the CLI (`ai-usage-monitor`) and want to add the VS Code extension:

1. Your existing data is automatically available
2. No migration needed - the extension uses the same data files
3. You can continue using the CLI alongside the extension
4. Settings are separate - configure each independently

### Future Migrations

Breaking changes and migration steps will be documented here.

---

For more information, see the [README](README.md) or visit the [GitHub repository](https://github.com/aecs4u/ai-usage-monitor).
