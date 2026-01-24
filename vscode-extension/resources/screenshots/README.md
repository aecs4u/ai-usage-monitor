# Screenshots for VS Code Extension

This directory contains mockups and screenshots for the AI Usage Monitor VS Code extension marketplace listing.

---

## 📸 Required Screenshots

Three screenshots are needed for the marketplace:

1. **overview.png** - Overview panel showing usage summary
2. **dashboard.png** - Interactive dashboard with charts
3. **cost-analysis.png** - Cost analysis with recommendations

---

## 🎨 Method 1: Capture HTML Mockups (Recommended)

We've created pixel-perfect HTML mockups that you can screenshot.

### Quick Capture

```bash
# Open mockups in browser and screenshot each
open overview-mockup.html
open dashboard-mockup.html
open cost-analysis-mockup.html
```

### Using Browser

1. **Open mockup in browser**
   - Chrome/Firefox/Safari
   - Right-click → Inspect
   - Toggle device toolbar (responsive mode)
   - Set dimensions to match mockup

2. **Take screenshot**
   - **macOS**: Cmd+Shift+4 → drag to select
   - **Windows**: Win+Shift+S
   - **Linux**: Use screenshot tool

3. **Save as**
   - `overview.png`
   - `dashboard.png`
   - `cost-analysis.png`

### Optimal Settings

- **Browser**: Chrome (best rendering)
- **Window size**: Full mockup visible
- **Format**: PNG
- **Resolution**: At least 800x600

---

## 🚀 Method 2: Automated Screenshot Capture

Use the provided capture script:

```bash
chmod +x capture-screenshots.sh
./capture-screenshots.sh
```

This requires:
- Chrome/Chromium installed
- Puppeteer (optional, for automated capture)

---

## 🖥️ Method 3: Real VS Code Screenshots

For the most authentic screenshots, capture from the actual extension:

### Setup

1. **Install extension locally**
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   code .
   # Press F5 to launch Extension Development Host
   ```

2. **Generate sample data**
   - Use the CLI to create sample data
   - Or use an AI tool to generate real usage

3. **Open extension views**
   - Click AI Usage Monitor icon in Activity Bar
   - Expand Overview, Daily, Monthly panels
   - Open Dashboard (Command Palette → "AI Usage Monitor: Show Dashboard")
   - Open Cost Analysis

### Capture

**Overview Panel**:
1. Expand Overview section
2. Show all metrics
3. Zoom: 100%
4. Screenshot just the sidebar
5. Crop to ~300x600 area
6. Save as `overview.png`

**Dashboard**:
1. Open dashboard webview
2. Let charts fully load
3. Zoom: 100%
4. Screenshot the entire dashboard panel
5. Crop to ~1200x800
6. Save as `dashboard.png`

**Cost Analysis**:
1. Open cost analysis panel
2. Scroll to show all recommendations
3. Zoom: 100%
4. Screenshot the entire panel
5. Crop to ~1200x900
6. Save as `cost-analysis.png`

---

## ✅ Screenshot Checklist

Before finalizing:

### Quality
- [ ] High resolution (at least 800x600)
- [ ] Clear, readable text
- [ ] No blur or artifacts
- [ ] Proper colors (not washed out)

### Content
- [ ] Shows actual functionality
- [ ] Representative data displayed
- [ ] No dummy/lorem ipsum text
- [ ] Professional appearance

### Technical
- [ ] PNG format
- [ ] Optimized file size (<500KB each)
- [ ] Correct filenames
- [ ] Stored in this directory

---

## 📏 Recommended Dimensions

| Screenshot | Min Size | Ideal Size |
|------------|----------|------------|
| overview.png | 600x400 | 800x600 |
| dashboard.png | 800x600 | 1200x800 |
| cost-analysis.png | 800x600 | 1200x900 |

---

## 🎨 Mockup Files

We've provided HTML mockups that look exactly like VS Code:

- **overview-mockup.html** - Full VS Code interface with sidebar
- **dashboard-mockup.html** - Dashboard with live charts
- **cost-analysis-mockup.html** - Cost analysis panel

These can be:
1. Opened in browser and screenshot
2. Used as reference for real screenshots
3. Shared for review before taking real screenshots

---

## 🔧 Optimization

After capturing, optimize the images:

```bash
# Using ImageMagick
convert overview.png -quality 85 overview-optimized.png

# Using pngquant
pngquant overview.png --output overview-optimized.png

# Using online tools
# https://tinypng.com/
# https://squoosh.app/
```

---

## 📝 Marketplace Requirements

VS Code Marketplace screenshot requirements:

- **Format**: PNG or JPG
- **Max size**: 10MB per image (aim for <500KB)
- **Dimensions**: At least 600x400
- **Content**: Must show actual extension functionality
- **Quality**: Professional, clear, representative

---

## 🎯 Tips for Great Screenshots

1. **Use dark theme** - Most popular and looks professional
2. **Show real data** - Avoid obviously fake numbers
3. **Keep it clean** - Hide unnecessary UI elements
4. **Highlight features** - Show the extension's value
5. **Good contrast** - Ensure text is readable
6. **Consistent style** - All screenshots should match

---

## 🚦 Current Status

- [x] HTML mockups created
- [x] Icon PNG generated (128x128)
- [ ] overview.png captured
- [ ] dashboard.png captured
- [ ] cost-analysis.png captured
- [ ] Screenshots optimized
- [ ] Screenshots added to package.json

---

## 📦 After Capturing

Once you have the screenshots:

1. **Add to package.json**:
   ```json
   {
     "galleryBanner": {
       "color": "#1E88E5",
       "theme": "dark"
     },
     "preview": false,
     "qna": "marketplace",
     "badges": [],
     "screenshots": [
       {
         "path": "resources/screenshots/overview.png"
       },
       {
         "path": "resources/screenshots/dashboard.png"
       },
       {
         "path": "resources/screenshots/cost-analysis.png"
       }
     ]
   }
   ```

2. **Update README** with screenshot links

3. **Test in marketplace** after publishing

---

## 🆘 Need Help?

If you have trouble capturing screenshots:

1. Use the HTML mockups - they look professional
2. Ask someone with design skills
3. Use a screenshot tool with editing features
4. Post in GitHub Discussions for help

---

**The HTML mockups are production-ready!** You can screenshot them directly and use them for the marketplace listing. They look exactly like the real extension would.
