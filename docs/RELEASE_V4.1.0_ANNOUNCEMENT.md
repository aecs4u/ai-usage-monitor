# AI Usage Monitor v4.1.0 Release Announcement

## 🎉 What's New

We're excited to announce **v4.1.0** of AI Usage Monitor, bringing significant performance improvements, observability features, and better multi-tool support!

### 🚀 Key Features

#### 1. Optional Logfire Telemetry Integration
- **Opt-in observability** for monitoring application performance
- Track adapter instantiation, data loading times, and cache effectiveness
- **Privacy-first**: Disabled by default, no sensitive data logged
- Configure via `~/.ai-usage-monitor.toml`:
  ```toml
  [telemetry]
  enabled = true
  token = "your_logfire_token"
  ```

#### 2. Incremental Loading (50%+ Performance Boost)
- **Smart file tracking** - only reads new/changed files during monitoring
- Reduces I/O by monitoring file modification times and byte offsets
- Automatic fallback to full load on errors
- Particularly effective during real-time monitoring refreshes

#### 3. Dynamic Table Titles
- Tables now show the actual tool name instead of generic "Claude Code"
- Multi-tool mode displays "AI Usage" for aggregated reports
- Better clarity when switching between tools

#### 4. Multi-Tool Pipeline Improvements
- Unified data loading through adapter pattern
- Consistent behavior across realtime, daily, and monthly views
- Better error messages for unsupported operations

### 🐛 Bug Fixes

- Fixed timezone handling in UsageAggregator (no more hardcoded Europe/Warsaw!)
- Corrected default timezone fallback to UTC instead of Warsaw
- Fixed multi-tool realtime error message clarity
- Updated test assertions for new Tools column in tables

### ⚡ Performance Improvements

- **50%+ faster** monitoring refreshes with incremental loading
- Reduced memory usage during long monitoring sessions
- Optimized file state tracking for minimal overhead

### 📊 Statistics

- **23 new tests** for incremental loading
- **89% code coverage** for FileStateTracker
- **0 breaking changes** - fully backward compatible

## 📦 Installation

### New Installation
```bash
pip install ai-usage-monitor
# or
uv tool install ai-usage-monitor
```

### Upgrade from v4.0.x
```bash
pip install --upgrade ai-usage-monitor
# or
uv tool install --upgrade ai-usage-monitor
```

## 🔧 Migration Guide

### Config File Location
If you're upgrading from pre-v4.0, your config will automatically migrate:
- Old: `~/.claude/config/` → New: `~/.ai-usage-monitor/`
- Old: `~/.claude-monitor/` → New: `~/.ai-usage-monitor/`

### Enabling Telemetry (Optional)
Create or edit `~/.ai-usage-monitor.toml`:
```toml
[telemetry]
enabled = true
token = "your_logfire_token_here"  # Get from logfire.pydantic.dev
sample_rate = 1.0  # 1.0 = 100% of events
```

### Incremental Loading
Automatically enabled for legacy readers. No configuration needed!

## 📖 Documentation

- **Full Changelog**: [CHANGELOG.md](https://github.com/aecs4u/ai-usage-monitor/blob/main/CHANGELOG.md)
- **Contributing**: [CONTRIBUTING.md](https://github.com/aecs4u/ai-usage-monitor/blob/main/CONTRIBUTING.md)
- **Issues**: [GitHub Issues](https://github.com/aecs4u/ai-usage-monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aecs4u/ai-usage-monitor/discussions)

## 🙏 Acknowledgments

Special thanks to:
- All contributors who reported issues and suggested improvements
- The Anthropic team for Claude and excellent API documentation
- The Python community for amazing tools like `uv`, `logfire`, and `rich`

## 🤝 Contributing

Want to help make AI Usage Monitor even better? We'd love your contributions!

- 🌟 **Star the repo** if you find it useful
- 🐛 **Report bugs** via [GitHub Issues](https://github.com/aecs4u/ai-usage-monitor/issues)
- 💡 **Request features** in [Discussions](https://github.com/aecs4u/ai-usage-monitor/discussions)
- 🔧 **Submit PRs** for bug fixes or new features
- 📝 **Improve docs** - documentation is always welcome!

Check out our [`good first issue`](https://github.com/aecs4u/ai-usage-monitor/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label for beginner-friendly contributions.

## 📱 Share Your Experience

We'd love to hear how you're using AI Usage Monitor:
- Twitter/X: Tag us @aecs4u
- Show HN: Share on Hacker News
- Reddit: Post in r/Python, r/ClaudeAI, r/commandline
- Blog: Write about your experience and tag us!

## 🔮 What's Next (v4.2.0 Preview)

- Export functionality (JSON/CSV)
- Enhanced cost projection algorithms
- Additional AI tool adapters
- Web dashboard (experimental)

Stay tuned!

---

**Full release notes**: https://github.com/aecs4u/ai-usage-monitor/releases/tag/v4.1.0

**PyPI**: https://pypi.org/project/ai-usage-monitor/

**Need help?** Join the discussion at https://github.com/aecs4u/ai-usage-monitor/discussions
