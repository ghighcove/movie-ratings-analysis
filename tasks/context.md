# Movie Ratings Manipulation Analysis - Session Context

## Last Updated: 2026-02-13

## Current State
- **Article 1 (Rating Inflation)**: Published to Medium (2026-02-12), pending archival
- **Article 2 (Manipulation)**: Exported and saved as Medium draft (2026-02-13), pending tags + scheduling
- Medium publishing workflow fully functional with automated export, import, and SEO
- Git repo: https://github.com/ghighcove/movie-ratings-analysis (GitHub Pages deployed)
- Medium standards repo: https://github.com/ghighcove/medium-publishing-standards
- Export script enhanced with dynamic title extraction and article name mapping

## Active Work
- **Completed (2026-02-13)**: Published Article 2 ("Who's Gaming IMDb? The Hidden Manipulation of Movie Ratings (2019-2024)") to Medium as draft
- **Article 2 status**:
  - Export: `article/manipulation_20260213_1015_ee2049fe.html` (successful)
  - Medium draft: https://medium.com/p/319dc8219795/edit
  - Figures: All 4 images (fig7, fig8, fig9, fig11) rendering correctly
  - Formatting: Title/attribution separated, numbered lists correct, preview image set
  - SEO: Preview image verified (fig11), tags require manual addition (browser automation limitation)
- **Workflow enhancement**: Complete 8-step automated workflow documented in CLAUDE.md (lines 247-293)

## Key Design Decisions

### Medium Publishing Workflow Enhancements (2026-02-13)
- **Complete automation documented**: Export → Git push → GitHub Pages verification → Medium import → SEO setup → Scheduling
- **User prompt for schedule date**: Always ask "What date would you like to schedule this article for?" — never assume
- **Title extraction**: Export script now extracts title from markdown H1 using regex instead of hardcoded titles
- **Article name mapping**: Added `manipulation_article_draft` → `manipulation` clean naming in export script (line 132)
- **Tag automation limitation**: Medium's custom tag interface doesn't respond to Tab/Enter/comma keyboard automation — requires manual addition (30 seconds)

### Formatting Fixes (2026-02-13)
- **Numbered list bug fix**: Blank lines between numbered list items cause markdown parser to wrap items in `<p>` tags, which Medium renders as blank bullets
  - **Solution**: Remove all blank lines between `1.`, `2.`, `3.` items in source markdown
  - **Applied to**: 5 locations in manipulation_article_draft.md (lines 74-78, 272-273, 295-296, 437-438, 476-477)
- **Title separation bug fix**: Export script was using hardcoded title "Rating Inflation" instead of extracting from H1
  - **Solution**: Use `re.search(r'^# (.+)$', markdown_content, re.MULTILINE)` to dynamically extract title
  - **Result**: Title and attribution now properly separated in Medium import

### Figure Integration (2026-02-13)
- **Article 2 figures**: Inserted 4 figure references at strategic locations
  - fig11 (summary) after line 60, before "The Evidence: Five Smoking Guns"
  - fig9 (franchise coordination) after line 89, end of "Smoking Gun #1"
  - fig7 (genre anomalies) after line 119, end of "Smoking Gun #2"
  - fig8 (Benford violations) around line 230, in "Smoking Gun #5"
- **Placement strategy**: Figures positioned near supporting text for logical reading flow

### Previous Decisions (2026-02-12)
- Medium Publishing Architecture: Full HTML, GitHub Pages URLs, unique timestamped filenames, table-as-PNG
- Centralized standards repository: Single source of truth for all Medium rules
- TMDb API rate limiting, studio identification, franchise detection (from 2026-02-11)

## Recent Changes (2026-02-13 session)

### Article 2 Publishing Workflow
- **Modified files**:
  - `article/manipulation_article_draft.md` - Added 4 figure references, removed blank lines from numbered lists (5 locations)
  - `scripts/export_for_medium.py` - Fixed title extraction (line 114-115), added manipulation article naming (line 137-138)
  - `CLAUDE.md` - Updated Medium workflow section (lines 241-318) with complete 8-step automated workflow, SEO setup, scheduling guidance, common issues & fixes
- **Created files**:
  - `article/manipulation_20260213_1006_6cc11af3.html` (first export, had formatting issues)
  - `article/manipulation_20260213_1015_ee2049fe.html` (final export, all fixes applied)
- **Medium imports**:
  - First import: Had numbered list blank bullets, title mixed with attribution
  - Second import: Successful, all formatting correct

### Commits Pushed (2026-02-13)
- `[hash]` - Add Medium export: Who's Gaming IMDb manipulation article (figures, formatting fixes, export script updates)

## Blockers / Open Questions
- **Article 2 tags**: Require manual addition in Medium editor (30 seconds: Data Analysis, Movies, IMDb, Statistics, Film Analysis)
- **Article 2 scheduling**: User to decide publication date when ready
- **Archival pending**: 3 published articles + Article 2 (after publication) need archival with archive_article.py

## Next Steps
1. **Article 2 - Manual completion** (when user is ready):
   - Add 5 tags in Medium editor
   - Schedule for publication date (user to specify)
   - Run archive_article.py after publication
2. **Article 1 archival**: Get Medium URL, run archive_article.py
3. **NFL articles**: Review 4 ready articles for publication scheduling

## Environment
- **Platform**: Windows 10 Home 10.0.19045
- **Python**: 3.8.x (32-bit) with pandas, numpy, scipy, matplotlib, seaborn, fastparquet, markdown (v3.4.3)
- **Working directory**: `G:\ai\entertainment_metrics\ratings`
- **Git repos**:
  - Analysis: https://github.com/ghighcove/movie-ratings-analysis (branch: main)
  - Standards: https://github.com/ghighcove/medium-publishing-standards (branch: main)
- **GitHub Pages**: https://ghighcove.github.io/movie-ratings-analysis/
- **TMDb API**: Free tier (40 req/10sec), key in .env file
- **Claude in Chrome**: Browser automation tools available for Medium import/scheduling

### Git Status (current session)
- **Status**: Clean working directory (all changes committed and pushed)
- **Last commit**: Article 2 Medium export with figure references and formatting fixes

## Quick Reference
- **Project CLAUDE.md**: `G:\ai\entertainment_metrics\ratings\CLAUDE.md` (lines 241-318 for Medium workflow)
- **Global CLAUDE.md**: `C:\Users\ghigh\.claude\CLAUDE.md` (references standards repo)
- **Medium standards**: `G:\ai\medium-publishing-standards\STANDARDS.md` (single source of truth)
- **Export script**: `scripts/export_for_medium.py`
- **Archive tool**: `G:\ai\medium-publishing-standards\tools\archive_article.py`
- **Article 1 (published)**: `article/medium_draft.md` → Medium (pending archival)
- **Article 2 (draft)**: `article/manipulation_article_draft.md` → https://medium.com/p/319dc8219795/edit (pending tags + scheduling)
- **Article 2 figures**: fig7_genre_anomalies.png, fig8_benford_violations.png, fig9_franchise_coordination.png, fig11_manipulation_summary.png
- **GitHub repos**:
  - https://github.com/ghighcove/movie-ratings-analysis
  - https://github.com/ghighcove/medium-publishing-standards

## Portfolio Summary (All Projects)
**Total: 7 articles across 3 projects**

### Published (3)
1. **NFL Player Value Analysis** - NFL project (published to Medium, pending archival)
2. **Super Bowl Ticket Price Analysis** - NFL project (published to Medium, pending archival)
3. **The Great Movie Rating Inflation** - Ratings project (published 2026-02-12, pending archival)

### In-Draft / Ready (4 + Article 2)
1. **Who's Gaming IMDb? (Article 2)** - Ratings project (Medium draft 2026-02-13, pending tags + scheduling)
2. **NFL Draft ROI** - NFL project (Medium draft, GEO 99/100, pending publication)
3. **NFL TE Market Inefficiency** - NFL project (Medium draft, GEO 97/100, pending schedule + SEO description)
4. **NFL QB Deep Dive** - NFL project (ready to import, GEO 97/100, deferred 3-5 days)
5. **NFL RB Economics** - NFL project (ready to import, GEO 95/100, deferred 3-5 days)

## Lessons Learned (Medium Publishing - Updated)

### What Worked (2026-02-13 additions)
- **Dynamic title extraction**: Regex-based H1 extraction prevents hardcoded title issues
- **Browser automation for import**: Claude in Chrome tools successfully navigate Medium import flow
- **Figure placement strategy**: Positioning visualizations near supporting text improves readability
- **Removing blank lines from lists**: Markdown parser requires no blank lines between numbered items for proper Medium rendering

### What Failed (2026-02-13 additions)
- **Numbered list formatting**: Blank lines between items cause `<p>` wrapping → blank bullets in Medium
- **Hardcoded titles**: Export script using hardcoded title caused title/attribution mixing
- **Tag automation**: Medium's custom tag interface doesn't respond to standard keyboard automation (Tab, Enter, comma)
  - **Workaround**: Manual addition (30 seconds for 5 tags)

### Process Improvements (2026-02-13)
- **Complete workflow documentation**: 8-step automated workflow in CLAUDE.md serves as runbook for future articles
- **Common issues & fixes section**: Documents numbered list formatting, title extraction, figure rendering for troubleshooting
- **User prompt for schedule date**: Prevents assumption errors, ensures user control over publication timing
