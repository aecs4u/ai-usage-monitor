# Demo Recording Guide

Complete guide for creating terminal demos of AI Usage Monitor using asciinema.

---

## Quick Start

### Automated Recording

The easiest way to create a demo:

```bash
# Make scripts executable
chmod +x scripts/record-demo.sh scripts/demo-script.sh

# Run the recording script
./scripts/record-demo.sh
```

This will:
1. Check dependencies (asciinema, ai-usage-monitor)
2. Let you choose demo type (quick/standard/full/export)
3. Record with optimal terminal settings (120x30)
4. Save to `.cast` file
5. Provide upload/conversion instructions

---

## Manual Recording

### 1. Install asciinema

```bash
pip install asciinema
```

Or via package manager:
```bash
# macOS
brew install asciinema

# Ubuntu/Debian
apt install asciinema

# Arch Linux
pacman -S asciinema
```

### 2. Set Terminal Size

For consistency, set terminal to **120 columns x 30 rows**:

```bash
# macOS/Linux
resize -s 30 120

# Or set in terminal preferences
```

### 3. Choose a Recording Script

We provide 4 demo types:

#### Quick Demo (30 seconds)
Shows monthly view only - perfect for README/social media
```bash
asciinema rec --cols 120 --rows 30 --title "AI Usage Monitor" demo-quick.cast
ai-usage-monitor
# Wait 5 seconds, then Ctrl+D
```

#### Standard Demo (60 seconds)
Shows monthly + daily views - good for documentation
```bash
asciinema rec --cols 120 --rows 30 demo-standard.cast
ai-usage-monitor                              # Monthly view
ai-usage-monitor --view daily                 # Daily view
ai-usage-monitor --tool claude-code --view daily  # Filtered
# Ctrl+D to finish
```

#### Full Demo (90 seconds)
Shows all features including realtime - comprehensive showcase
```bash
asciinema rec --cols 120 --rows 30 demo-full.cast
ai-usage-monitor                              # Monthly
ai-usage-monitor --view daily                 # Daily
ai-usage-monitor --view realtime              # Realtime (15 sec, then Ctrl+C)
ai-usage-monitor --tool all --view monthly    # Multi-tool
# Ctrl+D to finish
```

#### Export Demo (45 seconds)
Shows export functionality - for advanced users
```bash
asciinema rec --cols 120 --rows 30 demo-export.cast
ai-usage-monitor --export json --export-path usage.json
head -20 usage.json
ai-usage-monitor --view daily --export csv --export-path usage.csv
head -10 usage.csv
# Ctrl+D to finish
```

---

## Recording Tips

### Before Recording

- [ ] Clear your terminal history: `clear`
- [ ] Set terminal size: `resize -s 30 120`
- [ ] Use a clean, high-contrast theme (dark background recommended)
- [ ] Close unnecessary applications
- [ ] Test commands beforehand
- [ ] Have a script ready (use `scripts/demo-script.sh`)

### During Recording

- [ ] Type slowly and deliberately
- [ ] Pause 2-3 seconds between commands
- [ ] Let output fully render before continuing
- [ ] For realtime view: Let it run 10-15 seconds before Ctrl+C
- [ ] Exit cleanly (Ctrl+D or exit command)

### After Recording

- [ ] Review the recording: `asciinema play demo.cast`
- [ ] Re-record if there are mistakes (it's quick!)
- [ ] Upload or convert to desired format

---

## Publishing the Demo

### Option 1: Upload to asciinema.org (Recommended)

**Pros:** Embeddable, shareable, lightweight
**Cons:** Requires external hosting

```bash
# Upload
asciinema upload demo.cast

# You'll get a URL like: https://asciinema.org/a/xxxxx

# Embed in README
[![asciicast](https://asciinema.org/a/xxxxx.svg)](https://asciinema.org/a/xxxxx)
```

### Option 2: Convert to Animated GIF

**Pros:** Self-hosted, works everywhere
**Cons:** Large file size (~2-5 MB)

Using [agg](https://github.com/asciinema/agg):
```bash
# Install agg
cargo install --git https://github.com/asciinema/agg

# Convert
agg demo.cast demo.gif

# Optimize (optional)
gifsicle -O3 demo.gif -o demo-optimized.gif
```

Using [svg-term-cli](https://github.com/marionebl/svg-term-cli):
```bash
npm install -g svg-term-cli

# Convert to SVG (smaller, animated)
svg-term --in demo.cast --out demo.svg --window --width 120 --height 30
```

### Option 3: Convert to MP4 Video

**Pros:** High quality, widely supported
**Cons:** Requires additional tools

Using [asciinema-gif-generator](https://github.com/SeleniumHQ/docker-selenium):
```bash
docker run --rm -v $PWD:/data asciinema/asciicast2gif \
  -s 2 demo.cast demo.gif

# Then convert GIF to MP4
ffmpeg -i demo.gif -movflags faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" demo.mp4
```

---

## Adding Demo to README

### For asciinema.org

```markdown
## 🎬 Demo

See AI Usage Monitor in action:

[![asciicast](https://asciinema.org/a/xxxxx.svg)](https://asciinema.org/a/xxxxx)

*60-second demo showing monthly, daily, and realtime views*
```

### For GIF

```markdown
## 🎬 Demo

![AI Usage Monitor Demo](docs/images/demo.gif)

*60-second demo showing monthly, daily, and realtime views*
```

### For Video

```markdown
## 🎬 Demo

https://user-images.githubusercontent.com/xxxxx/demo.mp4

*60-second demo showing monthly, daily, and realtime views*
```

---

## Demo Checklist

Use this checklist when creating demos:

### Pre-Recording
- [ ] asciinema installed
- [ ] ai-usage-monitor installed and working
- [ ] Terminal size set to 120x30
- [ ] Clean terminal (clear screen)
- [ ] High-contrast theme
- [ ] Script prepared

### Recording
- [ ] Demo type selected (quick/standard/full/export)
- [ ] Recording started with correct parameters
- [ ] Commands typed slowly
- [ ] Pauses between commands
- [ ] Clean exit

### Post-Recording
- [ ] Reviewed playback
- [ ] No errors or typos
- [ ] Good timing and pacing
- [ ] Uploaded/converted
- [ ] Added to README

### Quality Check
- [ ] Demo is under 90 seconds
- [ ] Text is readable
- [ ] Output renders completely
- [ ] No sensitive information shown
- [ ] URL/link works

---

## Troubleshooting

### Terminal Size Issues

**Problem:** Demo looks cramped or cut off

**Solution:** Explicitly set terminal size
```bash
asciinema rec --cols 120 --rows 30 demo.cast
```

### Recording Too Long

**Problem:** Demo exceeds 90 seconds

**Solution:** Use timeout to auto-exit realtime view
```bash
timeout 15 ai-usage-monitor --view realtime
```

### No Data to Display

**Problem:** Tool shows "No data available"

**Solution:** Use the tool first to generate data
```bash
# Generate sample data by using Claude Code, Cline, etc.
# Or use test data if available
```

### Upload Fails

**Problem:** asciinema upload fails

**Solution:** Authenticate first
```bash
asciinema auth
# Follow the URL to link your account
asciinema upload demo.cast
```

### Large GIF File Size

**Problem:** GIF is >5 MB

**Solution:** Optimize with gifsicle
```bash
gifsicle -O3 --colors 256 demo.gif -o demo-optimized.gif
```

Or use SVG instead:
```bash
svg-term --in demo.cast --out demo.svg
```

---

## Examples

### Example 1: Quick README Demo

**Goal:** Show monthly view in 15 seconds for README

**Script:**
```bash
clear
echo "# AI Usage Monitor - Track your AI tool usage"
sleep 2
ai-usage-monitor
sleep 8
echo "Install: pip install ai-usage-monitor"
sleep 3
```

**Recording:**
```bash
asciinema rec --cols 120 --rows 30 -c "bash quick-demo.sh" demo-quick.cast
asciinema upload demo-quick.cast
```

### Example 2: Social Media GIF

**Goal:** 30-second eye-catching demo for Twitter/LinkedIn

**Script:**
```bash
clear
echo "🚀 AI Usage Monitor"
sleep 1
ai-usage-monitor --view daily
sleep 5
ai-usage-monitor --tool all --view monthly
sleep 5
echo "✨ pip install ai-usage-monitor"
sleep 3
```

**Recording:**
```bash
asciinema rec --cols 120 --rows 30 demo-social.cast
agg demo-social.cast demo-social.gif
gifsicle -O3 demo-social.gif -o demo-social-opt.gif
```

### Example 3: Documentation Video

**Goal:** Comprehensive feature showcase for docs

**Script:**
```bash
# Use scripts/demo-script.sh with type 3 (full demo)
asciinema rec --cols 120 --rows 30 \
  --title "AI Usage Monitor - Full Feature Demo" \
  --command "bash scripts/demo-script.sh 3" \
  demo-full.cast
```

---

## Best Practices

1. **Keep it short** - Aim for 30-60 seconds
2. **Show real data** - Use actual usage data, not mocks
3. **Highlight key features** - Focus on 2-3 main features
4. **Add context** - Brief text intro/outro
5. **Test before publishing** - Watch the playback
6. **Optimize file size** - Compress GIFs, use SVG when possible
7. **Update regularly** - Re-record when UI changes significantly
8. **Multiple versions** - Create demos for different audiences

---

## Resources

- **asciinema**: https://asciinema.org/
- **agg (GIF converter)**: https://github.com/asciinema/agg
- **svg-term-cli**: https://github.com/marionebl/svg-term-cli
- **gifsicle (optimizer)**: https://www.lcdf.org/gifsicle/
- **Terminal themes**: https://github.com/mbadolato/iTerm2-Color-Schemes

---

## Need Help?

- Open an issue: https://github.com/aecs4u/ai-usage-monitor/issues
- Discussions: https://github.com/aecs4u/ai-usage-monitor/discussions
- Ask in comments on existing demos

Happy recording! 🎬
