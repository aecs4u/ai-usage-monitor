#!/bin/bash
# Script to help capture screenshots from HTML mockups

set -e

echo "📸 AI Usage Monitor - Screenshot Capture Helper"
echo ""

# Check if we're in the right directory
if [ ! -f "overview-mockup.html" ]; then
    echo "❌ Error: Run this script from the screenshots directory"
    echo "   cd vscode-extension/resources/screenshots"
    exit 1
fi

echo "This script will help you capture screenshots for the VS Code extension."
echo ""
echo "Options:"
echo "  1. Open mockups in browser (manual screenshot)"
echo "  2. Instructions for manual capture"
echo "  3. Check current screenshots"
echo ""
read -p "Select option (1-3): " option

case $option in
    1)
        echo ""
        echo "Opening HTML mockups in browser..."
        echo "For each mockup:"
        echo "  1. Wait for it to load completely"
        echo "  2. Take a screenshot (Cmd+Shift+4 on macOS)"
        echo "  3. Save with the correct name"
        echo ""
        read -p "Press Enter to open Overview mockup..."

        # Open overview mockup
        if command -v open &> /dev/null; then
            open overview-mockup.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open overview-mockup.html
        else
            echo "Please open overview-mockup.html in your browser"
        fi

        echo ""
        echo "📸 Take screenshot and save as: overview.png"
        read -p "Press Enter when done and ready for next mockup..."

        # Open dashboard mockup
        if command -v open &> /dev/null; then
            open dashboard-mockup.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open dashboard-mockup.html
        else
            echo "Please open dashboard-mockup.html in your browser"
        fi

        echo ""
        echo "📸 Take screenshot and save as: dashboard.png"
        read -p "Press Enter when done and ready for next mockup..."

        # Open cost analysis mockup
        if command -v open &> /dev/null; then
            open cost-analysis-mockup.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open cost-analysis-mockup.html
        else
            echo "Please open cost-analysis-mockup.html in your browser"
        fi

        echo ""
        echo "📸 Take screenshot and save as: cost-analysis.png"
        read -p "Press Enter when done..."

        echo ""
        echo "✅ All mockups opened!"
        echo ""
        echo "Next steps:"
        echo "  1. Verify all 3 screenshots are saved"
        echo "  2. Optimize images (optional):"
        echo "     pngquant *.png"
        echo "  3. Check with: ls -lh *.png"
        ;;

    2)
        echo ""
        echo "📋 Manual Screenshot Instructions"
        echo ""
        echo "Overview Screenshot (overview.png):"
        echo "  1. Open overview-mockup.html in Chrome"
        echo "  2. Set window size to 1200x800"
        echo "  3. Screenshot entire window"
        echo "  4. Crop to sidebar area (left 300px)"
        echo "  5. Save as overview.png"
        echo ""
        echo "Dashboard Screenshot (dashboard.png):"
        echo "  1. Open dashboard-mockup.html in Chrome"
        echo "  2. Wait for all charts to load"
        echo "  3. Screenshot entire dashboard area"
        echo "  4. Crop to content (remove browser chrome)"
        echo "  5. Save as dashboard.png"
        echo ""
        echo "Cost Analysis Screenshot (cost-analysis.png):"
        echo "  1. Open cost-analysis-mockup.html in Chrome"
        echo "  2. Scroll to show all content"
        echo "  3. Screenshot entire analysis panel"
        echo "  4. Crop to content area"
        echo "  5. Save as cost-analysis.png"
        echo ""
        echo "Screenshot Tips:"
        echo "  • Use Chrome for best rendering"
        echo "  • PNG format only"
        echo "  • At least 800x600 resolution"
        echo "  • No browser UI in screenshots"
        echo ""
        ;;

    3)
        echo ""
        echo "📊 Current Screenshots Status"
        echo ""

        if [ -f "overview.png" ]; then
            size=$(wc -c < "overview.png" | awk '{print int($1/1024)}')
            dimensions=$(file overview.png | grep -oP '\d+\s*x\s*\d+' || echo "unknown")
            echo "✅ overview.png - ${size}KB - ${dimensions}"
        else
            echo "❌ overview.png - NOT FOUND"
        fi

        if [ -f "dashboard.png" ]; then
            size=$(wc -c < "dashboard.png" | awk '{print int($1/1024)}')
            dimensions=$(file dashboard.png | grep -oP '\d+\s*x\s*\d+' || echo "unknown")
            echo "✅ dashboard.png - ${size}KB - ${dimensions}"
        else
            echo "❌ dashboard.png - NOT FOUND"
        fi

        if [ -f "cost-analysis.png" ]; then
            size=$(wc -c < "cost-analysis.png" | awk '{print int($1/1024)}')
            dimensions=$(file cost-analysis.png | grep -oP '\d+\s*x\s*\d+' || echo "unknown")
            echo "✅ cost-analysis.png - ${size}KB - ${dimensions}"
        else
            echo "❌ cost-analysis.png - NOT FOUND"
        fi

        echo ""

        missing_count=0
        [ ! -f "overview.png" ] && ((missing_count++))
        [ ! -f "dashboard.png" ] && ((missing_count++))
        [ ! -f "cost-analysis.png" ] && ((missing_count++))

        if [ $missing_count -eq 0 ]; then
            echo "🎉 All screenshots present!"
            echo ""
            echo "Next steps:"
            echo "  1. Review each screenshot"
            echo "  2. Optimize if needed: pngquant *.png"
            echo "  3. Ready to publish!"
        else
            echo "⚠️  Missing ${missing_count} screenshot(s)"
            echo ""
            echo "Run this script again with option 1 to capture missing screenshots"
        fi
        ;;

    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📚 For more details, see: README.md"
