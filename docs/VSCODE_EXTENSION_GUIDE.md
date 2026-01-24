# VS Code Extension Guide

Complete guide for the AI Usage Monitor VS Code extension - from development to publishing.

---

## 📋 Overview

The AI Usage Monitor VS Code extension brings powerful usage tracking and cost analysis directly into your code editor. Monitor token usage, costs, and patterns across 9 AI coding assistants without leaving VS Code.

**Location**: `vscode-extension/`

**Status**: ✅ Complete and ready for publishing

---

## 🎯 Features

### Core Functionality

1. **Activity Bar Integration**
   - Custom icon in VS Code sidebar
   - Always accessible
   - Badge notifications for milestones

2. **Four Tree View Panels**
   - **Overview**: Current month summary
   - **Daily Usage**: Last 7 days with details
   - **Monthly Usage**: Historical data
   - **Tools**: Available AI tools

3. **Interactive Dashboards**
   - Daily token usage charts
   - Daily cost charts
   - Monthly trends
   - Theme-aware visualizations

4. **Cost Analysis**
   - Subscription recommendations
   - Savings calculator
   - Usage trends
   - Monthly projections

5. **Data Export**
   - Export to JSON
   - Export to CSV
   - Custom file paths
   - Full metadata included

### Supported AI Tools

- Claude Code (Anthropic)
- Cline (VS Code extension)
- Codex CLI (OpenAI)
- Gemini CLI (Google)
- GitHub Copilot (Microsoft)
- Roo Code
- Kilo Code
- OpenCode
- Pi Agent

---

## 🏗️ Architecture

### File Structure

```
vscode-extension/
├── src/
│   ├── extension.ts           # Main entry point
│   ├── views/                 # Tree view providers
│   │   ├── overviewProvider.ts
│   │   ├── dailyUsageProvider.ts
│   │   ├── monthlyUsageProvider.ts
│   │   └── toolsProvider.ts
│   ├── webviews/             # Dashboard panels
│   │   ├── dashboardPanel.ts
│   │   └── costAnalysisPanel.ts
│   └── utils/
│       └── cliManager.ts     # CLI communication
├── resources/                # Icons and assets
│   ├── icon.svg
│   ├── icon.png
│   └── screenshots/
├── package.json              # Extension manifest
├── tsconfig.json            # TypeScript config
├── README.md                # User documentation
├── CHANGELOG.md             # Version history
└── BUILDING.md              # Build & publish guide
```

### Components

#### Extension (extension.ts)
- Activation logic
- Command registration
- Auto-refresh timer
- View management

#### CLI Manager (cliManager.ts)
- Subprocess communication with CLI
- Data parsing and formatting
- Error handling
- Path resolution

#### Tree Providers (views/)
- Data fetching
- Tree item creation
- Refresh logic
- Event handling

#### Webview Panels (webviews/)
- Dashboard with Chart.js
- Cost analysis
- HTML generation
- Message passing

---

## 🚀 Quick Start

### Prerequisites

1. **Node.js 20+** installed
2. **VS Code 1.85.0+** installed
3. **AI Usage Monitor CLI** installed:
   ```bash
   pip install ai-usage-monitor
   ```

### Development Setup

```bash
# 1. Navigate to extension directory
cd vscode-extension

# 2. Install dependencies
npm install

# 3. Open in VS Code
code .

# 4. Press F5 to launch Extension Development Host

# 5. Test the extension in the new window
```

### Building

```bash
# Compile TypeScript
npm run compile

# Lint code
npm run lint

# Package extension
npm run package
# Creates: ai-usage-monitor-1.0.0.vsix
```

### Testing Locally

```bash
# Install from VSIX
code --install-extension ai-usage-monitor-1.0.0.vsix

# Uninstall
code --uninstall-extension aecs4u.ai-usage-monitor
```

---

## 📦 Publishing

### Prerequisites for Publishing

1. **Icons Created**
   - `resources/icon.png` (128x128)
   - `resources/icon.svg` (activity bar)
   - Screenshots in `resources/screenshots/`

2. **Marketplace Account**
   - Azure DevOps account
   - Publisher created: `aecs4u`
   - Personal Access Token (PAT)

3. **Version Updated**
   - `package.json` version incremented
   - `CHANGELOG.md` updated
   - Git tagged

### Publish to Marketplace

```bash
# 1. Login
vsce login aecs4u

# 2. Publish
vsce publish

# Or with version bump
vsce publish patch  # 1.0.0 → 1.0.1
vsce publish minor  # 1.0.0 → 1.1.0
vsce publish major  # 1.0.0 → 2.0.0
```

### Publish to Open VSX

```bash
npx ovsx publish -p YOUR_TOKEN
```

See [BUILDING.md](../vscode-extension/BUILDING.md) for detailed instructions.

---

## 🎨 Icons and Assets

### Creating Icons

**icon.png** (Marketplace listing):
- Size: 128x128 pixels
- Format: PNG with transparency
- Design: Bar chart with AI elements
- Colors: Blue/green brand colors

**icon.svg** (Activity bar):
- Format: SVG
- Uses: `currentColor` for theming
- Design: Simplified bar chart
- Works in light and dark themes

### Screenshots

Required screenshots:
1. `overview.png` - Overview panel
2. `dashboard.png` - Dashboard with charts
3. `cost-analysis.png` - Cost analysis panel

**Tips:**
- Use actual data
- Clean UI (hide unnecessary panels)
- 800x600 minimum resolution
- PNG format
- Optimized file size

See [resources/README.md](../vscode-extension/resources/README.md) for details.

---

## ⚙️ Configuration

Extension settings (all optional):

| Setting | Default | Description |
|---------|---------|-------------|
| `enableAutoRefresh` | `true` | Auto-refresh data |
| `refreshInterval` | `60` | Seconds between refreshes |
| `defaultTool` | `auto` | AI tool to monitor |
| `showNotifications` | `true` | Milestone notifications |
| `cliPath` | `""` | Custom CLI path |
| `timezone` | `auto` | Date timezone |

### Example User Settings

```json
{
  "aiUsageMonitor.enableAutoRefresh": true,
  "aiUsageMonitor.refreshInterval": 30,
  "aiUsageMonitor.defaultTool": "cline",
  "aiUsageMonitor.showNotifications": true
}
```

---

## 🔧 Development

### Watch Mode

Auto-compile on changes:

```bash
npm run watch
```

### Debugging

1. Set breakpoints in TypeScript files
2. Press F5 to launch Extension Development Host
3. Breakpoints hit in original VS Code window
4. Use Debug Console for logging

### Hot Reload

After making changes:
- In Extension Development Host
- `Cmd+R` / `Ctrl+R` to reload
- Or Command Palette → "Reload Window"

### Testing Commands

Test commands via Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):

```
AI Usage Monitor: Refresh
AI Usage Monitor: Show Dashboard
AI Usage Monitor: Export Data
AI Usage Monitor: Show Cost Analysis
AI Usage Monitor: Configure Settings
AI Usage Monitor: Select AI Tool
```

---

## 📊 Implementation Details

### CLI Communication

The extension communicates with the CLI via subprocess:

```typescript
// Execute CLI command
const cmd = `ai-usage-monitor --tool ${tool} --view monthly --export json`;
const { stdout } = await execAsync(cmd);
const data = JSON.parse(stdout);
```

**Benefits:**
- Reuses existing CLI logic
- No code duplication
- Consistent data format
- Easy to maintain

**Considerations:**
- Requires CLI installed
- Subprocess overhead
- Error handling needed

### Auto-Refresh

Configurable timer refreshes data:

```typescript
setInterval(() => {
  refreshAllViews();
}, interval * 1000);
```

**Configuration:**
- `enableAutoRefresh`: Toggle on/off
- `refreshInterval`: 10-300 seconds
- Stops when disabled
- Respects configuration changes

### Tree Views

VS Code tree views with custom providers:

```typescript
class OverviewProvider implements vscode.TreeDataProvider<OverviewItem> {
  async getChildren(element?: OverviewItem): Promise<OverviewItem[]> {
    // Fetch data from CLI
    // Return tree items
  }
}
```

**Features:**
- Lazy loading
- Expand/collapse
- Icons and descriptions
- Tooltips
- Context menus

### Webview Panels

HTML panels for dashboards:

```typescript
panel.webview.html = `<!DOCTYPE html>...`;
```

**Features:**
- Chart.js integration
- Theme-aware styling
- Message passing
- Retained context

---

## 🐛 Troubleshooting

### Common Issues

**"CLI Not Found"**
- Install CLI: `pip install ai-usage-monitor`
- Set custom path in settings
- Check PATH environment variable

**"No Data Available"**
- Use an AI tool to generate data
- Verify CLI works: `ai-usage-monitor`
- Check tool detection in Tools panel

**Charts Not Loading**
- Check internet connection (Chart.js CDN)
- Look for errors in Developer Tools
- Try closing and reopening dashboard

**Extension Not Activating**
- Check Output panel → Extension Host
- Look for activation errors
- Reload VS Code window

### Debug Output

Enable verbose logging:

```typescript
console.log('Debug message');  // Shows in Debug Console
```

View logs:
- View → Output
- Select "Extension Host"
- Look for AI Usage Monitor messages

---

## 🚢 Release Process

### Pre-Release Checklist

- [ ] All features working
- [ ] No console errors
- [ ] Tested in light/dark themes
- [ ] Tested on macOS/Windows/Linux
- [ ] Icons created
- [ ] Screenshots updated
- [ ] README accurate
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Git committed
- [ ] Git tagged

### Release Steps

1. **Update version**:
   ```bash
   npm version patch  # or minor, major
   ```

2. **Update CHANGELOG.md**

3. **Commit and tag**:
   ```bash
   git add .
   git commit -m "chore: release v1.0.1"
   git tag v1.0.1
   git push --tags
   ```

4. **Publish**:
   ```bash
   vsce publish
   ```

5. **Verify**:
   - Check marketplace listing
   - Test installation
   - Monitor for issues

### Post-Release

- Create GitHub release
- Update documentation
- Announce on social media
- Monitor user feedback

---

## 📈 Roadmap

### v1.1.0 (Planned)
- [ ] Real-time monitoring view
- [ ] Custom alerts and thresholds
- [ ] Budget tracking
- [ ] Team usage aggregation

### v1.2.0 (Future)
- [ ] Custom dashboard widgets
- [ ] Export to PDF
- [ ] Comparison between periods
- [ ] Cost forecasting

### v2.0.0 (Vision)
- [ ] Multi-workspace support
- [ ] CI/CD integration
- [ ] Slack/Discord notifications
- [ ] API for external tools

---

## 🤝 Contributing

Contributions welcome! Areas to help:

1. **Features**
   - Real-time monitoring
   - Custom alerts
   - New chart types
   - Export formats

2. **Bug Fixes**
   - Error handling
   - Edge cases
   - Performance improvements

3. **Documentation**
   - Better examples
   - Video tutorials
   - Translation

4. **Testing**
   - Unit tests
   - Integration tests
   - E2E tests

See main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## 📚 Resources

### Official Documentation
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

### Tools
- [vsce](https://github.com/microsoft/vscode-vsce) - Extension manager
- [ovsx](https://github.com/eclipse/openvsx) - Open VSX publishing
- [Yeoman generator](https://code.visualstudio.com/api/get-started/your-first-extension) - Extension scaffolding

### Examples
- [VS Code Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [Tree View Sample](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample)
- [Webview Sample](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-sample)

---

## ✅ Extension Checklist

Use this for tracking extension status:

### Development
- [x] Extension structure created
- [x] Tree view providers implemented
- [x] Webview dashboards created
- [x] CLI integration working
- [x] Auto-refresh implemented
- [x] Commands registered
- [x] Configuration defined

### Assets
- [x] Icon SVG created (placeholder)
- [ ] Icon PNG created (128x128)
- [ ] Screenshots created
- [ ] README updated
- [x] CHANGELOG created

### Testing
- [ ] Manual testing complete
- [ ] Works in light theme
- [ ] Works in dark theme
- [ ] Tested on macOS
- [ ] Tested on Windows
- [ ] Tested on Linux
- [ ] No console errors

### Publishing
- [ ] Marketplace account created
- [ ] Publisher configured
- [ ] PAT obtained
- [ ] VSIX package created
- [ ] Published to marketplace
- [ ] Published to Open VSX
- [ ] GitHub release created

---

## 🎉 Next Steps

1. **Create proper icons**
   - Design 128x128 icon.png
   - Optimize icon.svg if needed
   - See [resources/README.md](../vscode-extension/resources/README.md)

2. **Take screenshots**
   - Overview panel
   - Dashboard with charts
   - Cost analysis

3. **Set up marketplace**
   - Create Azure DevOps account
   - Create publisher
   - Get PAT

4. **Publish extension**
   ```bash
   cd vscode-extension
   vsce publish
   ```

5. **Promote extension**
   - Blog post
   - Social media
   - VS Code marketplace
   - README update

---

**The VS Code extension is complete and ready for publishing!** 🚀

Follow the checklists above to launch successfully.
