#!/bin/bash
# Demo script to showcase AI Usage Monitor features
# This script is executed during asciinema recording

# Get demo type from argument
DEMO_TYPE=${1:-2}

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to type command slowly (for visual effect)
type_command() {
    local cmd="$1"
    echo -ne "${GREEN}\$ ${NC}"
    for ((i=0; i<${#cmd}; i++)); do
        echo -n "${cmd:$i:1}"
        sleep 0.05
    done
    echo ""
    sleep 0.5
    eval "$cmd"
}

# Function to show comment
comment() {
    echo ""
    echo -e "${BLUE}# $1${NC}"
    sleep 1
}

# Clear screen
clear

# Banner
echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║          AI Usage Monitor - Terminal Demo                         ║${NC}"
echo -e "${YELLOW}║  Track AI coding assistant usage with beautiful dashboards        ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
sleep 2

case $DEMO_TYPE in
    1)
        # Quick demo - Monthly view only
        comment "Show monthly usage summary (default view)"
        type_command "ai-usage-monitor"
        sleep 5

        comment "That's it! Install with: pip install ai-usage-monitor"
        sleep 3
        ;;

    2)
        # Standard demo - Monthly + Daily views
        comment "Show monthly usage summary (default view)"
        type_command "ai-usage-monitor"
        sleep 4

        comment "Show daily usage breakdown"
        type_command "ai-usage-monitor --view daily"
        sleep 4

        comment "Filter to specific tool"
        type_command "ai-usage-monitor --tool claude-code --view daily"
        sleep 4

        comment "Installation: pip install ai-usage-monitor"
        sleep 3
        ;;

    3)
        # Full demo - All views
        comment "Show monthly usage summary"
        type_command "ai-usage-monitor"
        sleep 3

        comment "Show daily usage breakdown"
        type_command "ai-usage-monitor --view daily"
        sleep 3

        comment "Start realtime monitoring (Ctrl+C to exit)"
        echo -e "${GREEN}\$ ${NC}ai-usage-monitor --view realtime"
        sleep 1

        # Run realtime for 15 seconds then auto-exit
        timeout 15 ai-usage-monitor --view realtime || true

        comment "Track multiple AI tools simultaneously"
        type_command "ai-usage-monitor --tool all --view monthly"
        sleep 4

        comment "9 tools supported: Claude Code, Cline, Codex CLI, and more!"
        sleep 3
        ;;

    4)
        # Export demo
        comment "Export monthly data to JSON"
        type_command "ai-usage-monitor --export json --export-path usage.json"
        sleep 3

        comment "View exported file"
        type_command "head -20 usage.json"
        sleep 3

        comment "Export daily data to CSV"
        type_command "ai-usage-monitor --view daily --export csv --export-path usage.csv"
        sleep 3

        comment "CSV is perfect for Excel/spreadsheet analysis"
        type_command "head -10 usage.csv"
        sleep 3

        comment "Cleanup"
        rm -f usage.json usage.csv
        sleep 2
        ;;
esac

echo ""
echo -e "${GREEN}✨ Learn more: https://github.com/aecs4u/ai-usage-monitor${NC}"
echo ""
sleep 2
