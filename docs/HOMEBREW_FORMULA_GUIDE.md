# Homebrew Formula Guide

Complete guide for creating and publishing a Homebrew formula for AI Usage Monitor.

---

## 📦 Overview

Homebrew is the most popular package manager for macOS (and Linux). Creating a formula allows users to install with:

```bash
brew install ai-usage-monitor
```

This is much simpler than `pip install` for many users.

---

## 🚀 Quick Start

### Option 1: Homebrew Tap (Recommended)

Create your own tap for easy maintenance:

```bash
# 1. Create tap repository
gh repo create homebrew-tap --public --description "Homebrew formulas for aecs4u projects"

# 2. Clone it
git clone https://github.com/aecs4u/homebrew-tap.git
cd homebrew-tap

# 3. Copy formula
cp ../Claude-Code-Usage-Monitor/homebrew/ai-usage-monitor.rb Formula/ai-usage-monitor.rb

# 4. Update SHA256 (see below)

# 5. Commit and push
git add Formula/ai-usage-monitor.rb
git commit -m "Add ai-usage-monitor formula"
git push

# Users install via:
# brew install aecs4u/tap/ai-usage-monitor
```

### Option 2: Submit to homebrew-core (Advanced)

More exposure but stricter requirements:

```bash
# Requirements:
# - 75+ GitHub stars (or 30 days old + 20 forks)
# - Stable, documented API
# - Active maintenance

# See "Submit to homebrew-core" section below
```

---

## 📝 Update SHA256 Hash

After publishing to PyPI, get the SHA256:

```bash
# Download the tarball
curl -L -o ai-usage-monitor-4.1.0.tar.gz \
  https://files.pythonhosted.org/packages/source/a/ai-usage-monitor/ai-usage-monitor-4.1.0.tar.gz

# Calculate SHA256
sha256sum ai-usage-monitor-4.1.0.tar.gz

# macOS
shasum -a 256 ai-usage-monitor-4.1.0.tar.gz

# Copy the hash and update the formula
```

Or use Python:

```python
import hashlib
import urllib.request

url = "https://files.pythonhosted.org/packages/source/a/ai-usage-monitor/ai-usage-monitor-4.1.0.tar.gz"
response = urllib.request.urlopen(url)
sha256 = hashlib.sha256(response.read()).hexdigest()
print(f"sha256: {sha256}")
```

Update `homebrew/ai-usage-monitor.rb`:

```ruby
sha256 "REPLACE_WITH_ACTUAL_SHA256"  # ← Replace this
```

---

## 🏗️ Formula Structure

Our formula (`homebrew/ai-usage-monitor.rb`) explained:

```ruby
class AiUsageMonitor < Formula
  include Language::Python::Virtualenv  # Use Python virtualenv

  desc "Monitor AI coding assistant usage with real-time dashboards"
  homepage "https://github.com/aecs4u/ai-usage-monitor"
  url "https://files.pythonhosted.org/packages/source/a/ai-usage-monitor/ai-usage-monitor-4.1.0.tar.gz"
  sha256 "..."  # SHA256 of the tarball
  license "MIT"

  depends_on "python@3.12"  # Python dependency

  # Resource blocks define Python dependencies
  resource "click" do
    url "..."
    sha256 "..."
  end

  def install
    virtualenv_install_with_resources  # Install with virtualenv
  end

  test do
    # Tests run during `brew test ai-usage-monitor`
    assert_match "AI Usage Monitor", shell_output("#{bin}/ai-usage-monitor --help")
  end
end
```

---

## 🔧 Testing the Formula

### Local Testing

```bash
# Install locally
brew install --build-from-source homebrew/ai-usage-monitor.rb

# Test it works
ai-usage-monitor --help

# Run tests
brew test ai-usage-monitor

# Audit the formula
brew audit --strict --online ai-usage-monitor

# Uninstall
brew uninstall ai-usage-monitor
```

### Fix Common Issues

**Issue: Dependencies not found**
```bash
# Add resource blocks for missing dependencies
# Get dependency info from PyPI
```

**Issue: Command not found**
```bash
# Check that entry_points in pyproject.toml is correct
# Verify console_scripts section
```

**Issue: Import errors**
```bash
# Ensure all dependencies are listed as resources
# Check dependency versions match pyproject.toml
```

---

## 📤 Publishing

### Create Your Own Tap

1. **Create tap repository**
```bash
gh repo create homebrew-tap --public --clone
cd homebrew-tap
mkdir Formula
```

2. **Copy and update formula**
```bash
cp ../Claude-Code-Usage-Monitor/homebrew/ai-usage-monitor.rb Formula/

# Update SHA256 (see above)
# Edit Formula/ai-usage-monitor.rb
```

3. **Commit and push**
```bash
git add Formula/ai-usage-monitor.rb
git commit -m "Add ai-usage-monitor v4.1.0"
git push
```

4. **Test installation**
```bash
brew tap aecs4u/tap
brew install ai-usage-monitor
ai-usage-monitor --help
```

5. **Add to README**
```markdown
## Installation

### Homebrew (macOS/Linux)

```bash
brew tap aecs4u/tap
brew install ai-usage-monitor
```

### PyPI

```bash
pip install ai-usage-monitor
```
```

---

## 🌟 Submit to homebrew-core (Optional)

For maximum exposure, submit to the main Homebrew repository.

### Requirements

**Must have:**
- ✅ 75+ GitHub stars OR (30 days old + 20 forks)
- ✅ Stable release (not beta/alpha)
- ✅ Versioned releases with changelog
- ✅ Good documentation
- ✅ Active maintenance
- ✅ No security issues
- ✅ Works on latest macOS

**Should have:**
- 100+ stars (preferred)
- Multiple contributors
- CI/CD setup
- Test coverage

### Submission Process

1. **Check eligibility**
```bash
# Stars check
gh repo view aecs4u/ai-usage-monitor --json stargazerCount

# Need 75+ stars or meet alternative criteria
```

2. **Fork homebrew-core**
```bash
gh repo fork Homebrew/homebrew-core --clone
cd homebrew-core
```

3. **Create branch**
```bash
git checkout -b ai-usage-monitor
```

4. **Add formula**
```bash
cp ../Claude-Code-Usage-Monitor/homebrew/ai-usage-monitor.rb Formula/ai-usage-monitor.rb

# Update SHA256 and test thoroughly
```

5. **Test extensively**
```bash
brew install --build-from-source Formula/ai-usage-monitor.rb
brew test ai-usage-monitor
brew audit --strict --online ai-usage-monitor

# Test on clean system
brew uninstall ai-usage-monitor
brew install ai-usage-monitor
```

6. **Create PR**
```bash
git add Formula/ai-usage-monitor.rb
git commit -m "ai-usage-monitor 4.1.0 (new formula)"
git push origin ai-usage-monitor

gh pr create --title "ai-usage-monitor 4.1.0 (new formula)" \
  --body "Adds ai-usage-monitor, a CLI tool for monitoring AI coding assistant usage.

**Description:**
Track token usage, costs, and patterns across 9 different AI coding tools (Claude Code, Cline, GitHub Copilot, etc.) with real-time dashboards.

**Features:**
- Real-time monitoring with beautiful TUI
- Multi-tool support (9 AI assistants)
- Cost tracking and optimization
- Export to JSON/CSV
- Privacy-first (all offline)

**Project stats:**
- Stars: 100+
- License: MIT
- PyPI: https://pypi.org/project/ai-usage-monitor/
- Active development
- Good documentation

**Testing:**
\`\`\`bash
brew install --build-from-source Formula/ai-usage-monitor.rb
brew test ai-usage-monitor
brew audit --strict --online ai-usage-monitor
\`\`\`

All tests pass ✅"
```

7. **Wait for review**
- Homebrew maintainers review PRs
- They may request changes
- Respond promptly to feedback
- Typical review time: 1-2 weeks

### Homebrew-core Requirements

**Formula must:**
- Use stable release URL (not git)
- Include all dependencies as resources
- Pass `brew audit --strict --online`
- Pass `brew test`
- Work on latest macOS
- Follow Homebrew conventions

**Common rejection reasons:**
- Insufficient stars/users
- Duplicate functionality
- Not stable enough
- Poor documentation
- Failing tests
- License issues

---

## 🔄 Updating the Formula

When releasing a new version:

### For Your Tap

```bash
cd homebrew-tap

# 1. Update version and SHA256 in Formula/ai-usage-monitor.rb
# 2. Update dependency versions if needed

# Get new SHA256
curl -L https://files.pythonhosted.org/packages/source/a/ai-usage-monitor/ai-usage-monitor-4.2.0.tar.gz | shasum -a 256

# 3. Test
brew reinstall --build-from-source Formula/ai-usage-monitor.rb
brew test ai-usage-monitor

# 4. Commit
git add Formula/ai-usage-monitor.rb
git commit -m "ai-usage-monitor: update to 4.2.0"
git push
```

### For homebrew-core

```bash
# After your formula is in homebrew-core

cd homebrew-core
git checkout -b ai-usage-monitor-4.2.0

# Update Formula/ai-usage-monitor.rb
# - version in url
# - sha256
# - any dependency changes

brew reinstall --build-from-source Formula/ai-usage-monitor.rb
brew test ai-usage-monitor
brew audit --strict --online ai-usage-monitor

git add Formula/ai-usage-monitor.rb
git commit -m "ai-usage-monitor 4.2.0"
git push origin ai-usage-monitor-4.2.0

gh pr create --title "ai-usage-monitor 4.2.0" \
  --body "Updates ai-usage-monitor to version 4.2.0.

**Changes:**
- [List key changes from CHANGELOG]

**Testing:**
\`\`\`bash
brew reinstall --build-from-source Formula/ai-usage-monitor.rb
brew test ai-usage-monitor
\`\`\`

All tests pass ✅"
```

---

## 🧪 Advanced Formula Features

### Add Tests

```ruby
test do
  # Basic help test
  assert_match "AI Usage Monitor", shell_output("#{bin}/ai-usage-monitor --help")

  # Version test
  assert_match version.to_s, shell_output("#{bin}/ai-usage-monitor --version")

  # Test actual functionality
  output = shell_output("#{bin}/ai-usage-monitor --tool auto --export json 2>&1", 0)
  assert_match "format", output

  # Test configuration
  (testpath/".ai-usage-monitor.toml").write <<~EOS
    [tools.claude-code]
    enabled = true
  EOS

  system bin/"ai-usage-monitor", "--help"
end
```

### Add Service (Background Monitoring)

```ruby
def plist
  <<~EOS
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>Label</key>
      <string>#{plist_name}</string>
      <key>ProgramArguments</key>
      <array>
        <string>#{opt_bin}/ai-usage-monitor</string>
        <string>--view</string>
        <string>realtime</string>
      </array>
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
    </dict>
    </plist>
  EOS
end
```

Users can then:
```bash
brew services start ai-usage-monitor
```

---

## 📊 Metrics

Track Homebrew adoption:

### Check Install Stats

```bash
# Install count (if in homebrew-core)
brew info ai-usage-monitor --json | jq '.[].analytics.install_on_request'

# Monthly installs
brew info ai-usage-monitor --json | jq '.[].analytics.install_on_request_30d'
```

### Monitor Issues

```bash
# Check for issues mentioning your formula
gh issue list --repo Homebrew/homebrew-core --search "ai-usage-monitor"
```

---

## 🎯 Success Metrics

**Week 1 (Own Tap):**
- Tap created and published
- Installation works on macOS
- Installation works on Linux (if applicable)
- Documentation updated

**Month 1:**
- 10+ installs via your tap
- No installation issues reported
- Updated to latest version

**Month 3 (homebrew-core):**
- Eligible for homebrew-core (75+ stars)
- PR submitted
- PR merged (if accepted)

**Month 6:**
- 50+ installs/month
- Featured in homebrew search results
- Recognized installation method

---

## 📝 Checklist

### Create Your Tap
- [ ] Create homebrew-tap repository
- [ ] Copy formula to Formula/
- [ ] Update SHA256 hash
- [ ] Test installation locally
- [ ] Commit and push
- [ ] Test from tap: `brew tap aecs4u/tap && brew install ai-usage-monitor`
- [ ] Update README with installation instructions
- [ ] Announce on social media

### Submit to homebrew-core (Later)
- [ ] Verify 75+ stars OR 30 days + 20 forks
- [ ] Fork homebrew-core
- [ ] Add formula
- [ ] Test extensively (install, test, audit)
- [ ] Create PR
- [ ] Respond to maintainer feedback
- [ ] Celebrate merge! 🎉

---

## 🔗 Resources

- **Homebrew Documentation:** https://docs.brew.sh/Formula-Cookbook
- **Python Formula Guide:** https://docs.brew.sh/Python-for-Formula-Authors
- **Acceptable Formulae:** https://docs.brew.sh/Acceptable-Formulae
- **Formula Style Guide:** https://docs.brew.sh/Formula-Cookbook#style-guide
- **Homebrew Core:** https://github.com/Homebrew/homebrew-core

---

## 💡 Tips

1. **Start with your own tap**
   - Easier to publish and maintain
   - Test with real users first
   - Build confidence before submitting to homebrew-core

2. **Test on clean machines**
   - Use Docker or VMs
   - Ensure it works without existing Python setup

3. **Keep dependencies minimal**
   - Only include necessary dependencies
   - Use latest stable versions

4. **Respond to issues quickly**
   - Users will report installation issues
   - Fix them promptly
   - Update formula

5. **Document everything**
   - Clear installation instructions
   - Troubleshooting guide
   - Known issues

---

**Ready to brew!** 🍺

Start with your own tap, then submit to homebrew-core when you have enough traction.
