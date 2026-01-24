# Extension Resources

This directory contains visual assets for the AI Usage Monitor VS Code extension.

## Required Files

### icon.png
- **Size**: 128x128 pixels
- **Format**: PNG with transparency
- **Purpose**: Marketplace listing icon
- **Design**: Should represent AI monitoring/analytics

**Recommended design:**
- Bar chart or graph icon
- AI/circuit pattern
- Blue/green color scheme matching the brand
- Clean, modern, recognizable at small sizes

### icon.svg
- **Format**: SVG (Scalable Vector Graphics)
- **Purpose**: Activity bar icon (sidebar)
- **Design**: Simplified version of icon.png
- **Requirements**:
  - Should work in both light and dark themes
  - Use single color (will be themed by VS Code)
  - Simple, recognizable shape

## Creating Icons

### Option 1: Using Figma/Sketch

1. Create a 128x128 artboard
2. Design the icon (see recommendations above)
3. Export as PNG (icon.png) and SVG (icon.svg)

### Option 2: Using DALL-E / AI Image Generator

```
Prompt: "A minimalist icon for an AI usage monitoring tool.
Features a bar chart or analytics graph with circuit board patterns.
Blue and green colors. Simple, clean design suitable for a VS Code extension.
128x128 pixels, transparent background."
```

### Option 3: Using Online Icon Generators

Recommended sites:
- https://www.figma.com/
- https://www.canva.com/
- https://favicon.io/
- https://realfavicongenerator.net/

## Screenshots

Create screenshots for the marketplace listing:

### screenshots/overview.png
- Show the Overview panel in the sidebar
- Include some sample data
- Light or dark theme (whichever looks better)

### screenshots/dashboard.png
- Show the dashboard with all charts
- Include meaningful data
- Maximize the dashboard window

### screenshots/cost-analysis.png
- Show the cost analysis panel
- Include subscription recommendations
- Show the insights section

## Creating Screenshots

1. Use the extension with sample data
2. Set up VS Code window nicely:
   - Hide unnecessary panels
   - Use a clean theme
   - Zoom to appropriate level
3. Take screenshots:
   - macOS: Cmd+Shift+4
   - Windows: Win+Shift+S
   - Linux: Screenshot tool
4. Crop and optimize images
5. Name them as listed above

## Optimization

Optimize images before committing:

```bash
# PNG optimization
pngquant icon.png --output icon.png --force
optipng -o7 icon.png

# Or use online tools
# https://tinypng.com/
# https://squoosh.app/
```

## Image Specifications

| File | Size | Format | Purpose |
|------|------|--------|---------|
| icon.png | 128x128 | PNG | Marketplace icon |
| icon.svg | Any | SVG | Activity bar icon |
| screenshots/overview.png | ~800x600 | PNG | Marketplace screenshot |
| screenshots/dashboard.png | ~1200x800 | PNG | Marketplace screenshot |
| screenshots/cost-analysis.png | ~1200x800 | PNG | Marketplace screenshot |

## Placeholder Icons

Until you create proper icons, you can use placeholder SVG:

**icon.svg** (minimal placeholder):
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
  <path d="M3 13h2v8H3v-8zm4-6h2v14H7V7zm4-4h2v18h-2V3zm4 8h2v10h-2V11z"/>
</svg>
```

This creates a simple bar chart icon that works in any theme.

## Attribution

If using third-party icons or images, ensure:
- Compatible license (MIT, CC0, or commercial allowed)
- Proper attribution in package.json or README
- Follow license requirements

## Review Checklist

Before publishing:
- [ ] icon.png exists and is 128x128
- [ ] icon.svg exists and uses currentColor
- [ ] All screenshots are clear and representative
- [ ] Images are optimized for size
- [ ] No placeholder text visible in screenshots
- [ ] Screenshots show actual functionality
- [ ] Icons work in both light and dark themes

---

**Note**: The extension will work without these files during development, but they are **required** for publishing to the marketplace.
