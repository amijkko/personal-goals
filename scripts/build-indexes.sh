#!/bin/bash
# Build people and project indexes for the goal system
# Runs daily via cron, outputs to goals/index-people.md and goals/index-projects.md

GOALS_DIR="$HOME/goals"
PEOPLE_INDEX="$GOALS_DIR/index-people.md"
PROJECTS_INDEX="$GOALS_DIR/index-projects.md"
TODAY=$(date +%Y-%m-%d)
NOW=$(date "+%Y-%m-%d %H:%M")

# ============================================
# 1. PEOPLE INDEX
# ============================================

# Extract names from CRM files (format: ### Name — Company)
extract_names() {
    grep -h '^### ' "$GOALS_DIR"/crm*.md 2>/dev/null \
        | sed 's/^### //' \
        | sed 's/ — .*//' \
        | sort -u
}

# Find all mentions of a person across goals/
find_mentions() {
    local name="$1"
    # Use first word as search key (handles "Алексей Курочкин" and just "Беленов")
    local first_word=$(echo "$name" | awk '{print $1}')

    local results=""

    # Search in CRM files
    local crm_hits=$(grep -l "$first_word" "$GOALS_DIR"/crm*.md 2>/dev/null | while read f; do
        basename "$f" .md
    done | tr '\n' ', ' | sed 's/,$//')

    # Search in backlog
    local backlog_lines=$(grep "$first_word" "$GOALS_DIR/backlog.md" 2>/dev/null | wc -l | tr -d ' ')

    # Search in daily/weekly/monthly
    local daily_hits=$(grep "$first_word" "$GOALS_DIR/daily.md" 2>/dev/null | wc -l | tr -d ' ')
    local weekly_hits=$(grep "$first_word" "$GOALS_DIR/weekly.md" 2>/dev/null | wc -l | tr -d ' ')

    # Search in meetings
    local meeting_files=$(grep -rl "$first_word" "$GOALS_DIR/meetings/" 2>/dev/null | while read f; do
        basename "$f"
    done | tr '\n' ', ' | sed 's/,$//')

    # Search in KB
    local kb_files=$(grep -rl "$first_word" "$GOALS_DIR/kb/" 2>/dev/null | while read f; do
        # Show relative path from kb/
        echo "$f" | sed "s|$GOALS_DIR/kb/||"
    done | tr '\n' ', ' | sed 's/,$//')

    # Search in journal
    local journal_files=$(grep -rl "$first_word" "$GOALS_DIR/journal/" 2>/dev/null | while read f; do
        basename "$f"
    done | tr '\n' ', ' | sed 's/,$//')

    # Build output
    echo "### $name"
    [ -n "$crm_hits" ] && echo "- **CRM:** $crm_hits"
    [ "$backlog_lines" -gt 0 ] && echo "- **Backlog:** $backlog_lines mention(s)"
    [ "$daily_hits" -gt 0 ] && echo "- **Daily:** $daily_hits mention(s)"
    [ "$weekly_hits" -gt 0 ] && echo "- **Weekly:** $weekly_hits mention(s)"
    [ -n "$meeting_files" ] && echo "- **Meetings:** $meeting_files"
    [ -n "$kb_files" ] && echo "- **KB:** $kb_files"
    [ -n "$journal_files" ] && echo "- **Journal:** $journal_files"

    # Show next action from CRM
    local next_action=$(grep -A5 "$first_word" "$GOALS_DIR"/crm*.md 2>/dev/null \
        | grep "Следующее действие" | head -1 | sed 's/.*Следующее действие:\*\* //')
    [ -n "$next_action" ] && echo "- **Next:** $next_action"

    # Show ping date from CRM
    local ping_date=$(grep -A8 "$first_word" "$GOALS_DIR"/crm*.md 2>/dev/null \
        | grep "Пингануть:" | head -1 | sed 's/.*Пингануть:\*\* //')
    [ -n "$ping_date" ] && echo "- **Ping:** $ping_date"

    echo ""
}

# Generate people index
{
    echo "# People Index"
    echo ""
    echo "> Auto-generated: $NOW. Do not edit manually."
    echo ""

    extract_names | while read name; do
        [ -n "$name" ] && find_mentions "$name"
    done
} > "$PEOPLE_INDEX"


# ============================================
# 2. PROJECTS INDEX
# ============================================

PROJECTS=("custody" "opinion-market" "sber" "reksoft" "personal")
PROJECT_LABELS=("Custody" "Opinion Market" "Sber" "Reksoft" "Personal")

{
    echo "# Projects Index"
    echo ""
    echo "> Auto-generated: $NOW. Do not edit manually."
    echo ""

    for i in "${!PROJECTS[@]}"; do
        project="${PROJECTS[$i]}"
        label="${PROJECT_LABELS[$i]}"

        echo "## $label"
        echo ""

        # KB docs count
        kb_count=$(find "$GOALS_DIR/kb/$project" -name "*.md" 2>/dev/null | grep -v index.md | wc -l | tr -d ' ')
        echo "- **KB docs:** $kb_count"

        # Meetings count
        meeting_count=$(grep -rl -i "$project\|$label" "$GOALS_DIR/meetings/" 2>/dev/null | wc -l | tr -d ' ')
        echo "- **Meetings:** $meeting_count"

        # CRM contacts — search for project name in CRM headers context
        if [ "$project" = "opinion-market" ] && [ -f "$GOALS_DIR/crm-blind-bets.md" ]; then
            crm_count=$(grep -c '^### ' "$GOALS_DIR/crm-blind-bets.md" 2>/dev/null || echo 0)
            echo "- **CRM contacts:** $crm_count (crm-blind-bets.md)"
        else
            crm_count=$(grep -c '^### ' "$GOALS_DIR/crm.md" 2>/dev/null || echo 0)
            echo "- **CRM contacts:** $crm_count (crm.md)"
        fi

        # Open tasks in backlog
        backlog_tasks=$(grep -i "$project\|$label" "$GOALS_DIR/backlog.md" 2>/dev/null | grep '^\- \[ \]' | wc -l | tr -d ' ')
        echo "- **Open backlog tasks:** $backlog_tasks"

        # Weekly tasks
        weekly_tasks=$(grep -i "$project\|$label" "$GOALS_DIR/weekly.md" 2>/dev/null | grep '^\- \[' | wc -l | tr -d ' ')
        echo "- **Weekly tasks:** $weekly_tasks"

        # Monthly goals
        monthly_refs=$(grep -i "$project\|$label" "$GOALS_DIR/monthly.md" 2>/dev/null | wc -l | tr -d ' ')
        echo "- **Monthly refs:** $monthly_refs"

        # KB index file (if exists)
        if [ -f "$GOALS_DIR/kb/$project/index.md" ]; then
            echo "- **KB index:** kb/$project/index.md"
        fi

        # List KB docs
        if [ "$kb_count" -gt 0 ]; then
            echo "- **Docs:**"
            find "$GOALS_DIR/kb/$project" -name "*.md" 2>/dev/null | grep -v index.md | sort | while read f; do
                fname=$(basename "$f" .md)
                relpath=$(echo "$f" | sed "s|$GOALS_DIR/||")
                echo "  - [$fname]($relpath)"
            done
        fi

        echo ""
    done

    # Uncategorized — tasks not matching any project
    echo "## Uncategorized"
    echo ""
    uncategorized=$(grep '^\- \[ \]' "$GOALS_DIR/backlog.md" 2>/dev/null | grep -iv 'custody\|blind.bets\|opinion.market\|sber\|reksoft\|collider\|кастоди\|кастос' | head -20)
    if [ -n "$uncategorized" ]; then
        echo "$uncategorized"
    else
        echo "No uncategorized tasks."
    fi
    echo ""

} > "$PROJECTS_INDEX"

echo "Indexes built: $NOW"
echo "  $PEOPLE_INDEX"
echo "  $PROJECTS_INDEX"

# ============================================
# 3. CRM ENRICHMENT (if DATABASE_URL is set)
# ============================================
if [ -n "$DATABASE_URL" ] || [ -n "$CRM_DATABASE_URL" ]; then
    python3 "$GOALS_DIR/scripts/enrich-crm.py" 2>&1
fi
