#!/bin/bash
#
# Start monthly repository improvement cycle
#
# This script orchestrates the improvement data collection,
# security scanning, and track creation process.
#
# Usage:
#   ./scripts/start_improvement_cycle.sh [--dry-run] [--skip-security]
#
# Examples:
#   ./scripts/start_improvement_cycle.sh
#   ./scripts/start_improvement_cycle.sh --dry-run
#   ./scripts/start_improvement_cycle.sh --skip-security
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
SKIP_SECURITY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-security)
            SKIP_SECURITY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--skip-security]"
            echo ""
            echo "Options:"
            echo "  --dry-run      Show what would be done without executing"
            echo "  --skip-security  Skip security scanning"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$ROOT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Monthly Repository Improvement Cycle                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "Repository: $(basename "$ROOT_DIR")"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    exit 1
fi

# Check if running in dry-run mode
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Step 1: Collect improvement data
echo -e "${GREEN}Step 1: Collecting improvement data...${NC}"
if [ "$DRY_RUN" = true ]; then
    echo "  Would run: python3 scripts/collect_improvement_data.py"
else
    if python3 scripts/collect_improvement_data.py; then
        echo -e "  ${GREEN}✅ Data collection complete${NC}"
    else
        echo -e "  ${RED}❌ Data collection failed${NC}"
        exit 1
    fi
fi
echo ""

# Step 2: Run security scan
if [ "$SKIP_SECURITY" = false ]; then
    echo -e "${GREEN}Step 2: Running security scan...${NC}"
    if [ "$DRY_RUN" = true ]; then
        echo "  Would run: python3 scripts/security_scan.py"
    else
        if python3 scripts/security_scan.py --format markdown --output .conductor/security-report.md; then
            echo -e "  ${GREEN}✅ Security scan complete - No vulnerabilities found${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Security scan complete - Vulnerabilities detected${NC}"
            echo -e "     Review: .conductor/security-report.md"
        fi
    fi
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping security scan (--skip-security)${NC}"
    echo ""
fi

# Step 3: Create improvement track
echo -e "${GREEN}Step 3: Creating improvement track...${NC}"
if [ "$DRY_RUN" = true ]; then
    echo "  Would run: python3 scripts/create_improvement_track.py"
else
    if python3 scripts/create_improvement_track.py; then
        echo -e "  ${GREEN}✅ Track created${NC}"
    else
        echo -e "  ${RED}❌ Track creation failed${NC}"
        exit 1
    fi
fi
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Improvement Cycle Started Successfully              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Next Steps:${NC}"
echo ""
echo "   1. Review collected data:"
echo "      cd .conductor/improvement-data/"
echo "      cat SUMMARY.md"
echo ""
echo "   2. Review security report:"
echo "      cat .conductor/security-report.md"
echo ""
echo "   3. Start implementing the track:"
echo "      /conductor:implement"
echo ""
echo "   4. Or review the track first:"
echo "      /conductor:review improvement_$(date +%Y%m%d)"
echo ""
echo -e "For more information, see: ${BLUE}conductor/improvement_workflow.md${NC}"
echo ""
