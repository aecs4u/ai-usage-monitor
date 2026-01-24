#!/bin/bash
# Script to record asciinema demo of AI Usage Monitor
# Requires: asciinema (pip install asciinema)

set -e

echo "🎬 AI Usage Monitor Demo Recording Setup"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if asciinema is installed
if ! command -v asciinema &> /dev/null; then
    echo "❌ asciinema is not installed. Installing now..."
    pip install asciinema
fi

# Check if ai-usage-monitor is installed
if ! command -v ai-usage-monitor &> /dev/null; then
    echo "❌ ai-usage-monitor is not installed. Please install it first:"
    echo "   pip install ai-usage-monitor"
    exit 1
fi

echo "${BLUE}Demo Recording Configuration:${NC}"
echo "  Terminal size: 120 columns x 30 rows"
echo "  Duration: ~60 seconds"
echo "  Features shown:"
echo "    - Monthly view (default)"
echo "    - Daily view with filtering"
echo "    - Realtime monitoring"
echo "    - Export to JSON"
echo ""

# Prompt for demo type
echo "${YELLOW}Which demo would you like to record?${NC}"
echo "  1. Quick demo (30 seconds) - Monthly view only"
echo "  2. Standard demo (60 seconds) - Monthly + Daily views"
echo "  3. Full demo (90 seconds) - All views including realtime"
echo "  4. Export demo (45 seconds) - Export functionality"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        demo_file="demo-quick.cast"
        demo_desc="Quick 30-second demo showing monthly view"
        ;;
    2)
        demo_file="demo-standard.cast"
        demo_desc="Standard 60-second demo showing monthly and daily views"
        ;;
    3)
        demo_file="demo-full.cast"
        demo_desc="Full 90-second demo showing all views"
        ;;
    4)
        demo_file="demo-export.cast"
        demo_desc="45-second export functionality demo"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "${GREEN}Recording: ${demo_desc}${NC}"
echo "${GREEN}Output: ${demo_file}${NC}"
echo ""
echo "${YELLOW}Recording tips:${NC}"
echo "  • Type slowly and deliberately"
echo "  • Pause 2-3 seconds between commands"
echo "  • Let output fully render before continuing"
echo "  • Exit cleanly with Ctrl+C for realtime view"
echo ""
echo "Press ENTER when ready to start recording..."
read

# Start recording
echo "${GREEN}🎥 Starting recording in 3 seconds...${NC}"
sleep 3

asciinema rec \
    --cols 120 \
    --rows 30 \
    --title "AI Usage Monitor Demo" \
    --command "bash scripts/demo-script.sh $choice" \
    "$demo_file"

echo ""
echo "${GREEN}✅ Recording complete!${NC}"
echo ""
echo "${BLUE}Next steps:${NC}"
echo "  1. Review the recording:"
echo "     asciinema play $demo_file"
echo ""
echo "  2. Upload to asciinema.org:"
echo "     asciinema upload $demo_file"
echo ""
echo "  3. Or convert to GIF (requires agg or svg-term):"
echo "     # Using agg (https://github.com/asciinema/agg)"
echo "     agg $demo_file demo.gif"
echo ""
echo "  4. Add link to README.md in 'Demo' section"
echo ""
