# Movie Ratings Manipulation Analysis - Session Context

## Last Updated: 2026-02-12

## Current State
- Analysis and article writing phase complete (2026-02-11 session)
- Medium publishing workflow fully functional with table-as-PNG fix (2026-02-12 morning)
- **Centralized Medium standards repository created and pushed to GitHub** (2026-02-12 afternoon)
- **First article successfully imported to Medium** (`rating_inflation_20260212_1130_991e9cf8.html`)
- Git repo: https://github.com/ghighcove/movie-ratings-analysis (GitHub Pages deployed)
- **New repo**: https://github.com/ghighcove/medium-publishing-standards (single source of truth for all Medium rules)
- Export script fully functional with markdown library + table-as-PNG support
- **Portfolio inventory complete**: 7 total articles across 3 projects (3 published, 4 ready/in-draft)

## Active Work
- **Completed (2026-02-12 morning)**: Medium export/import workflow for article 1 (rating inflation analysis)
- **Completed (2026-02-12 afternoon)**: Created medium-publishing-standards repository with archival tooling, updated global and project CLAUDE.md to reference centralized standards, completed portfolio inventory
- **Status**: Medium submission limit reached for today — cannot test further imports until tomorrow
- **Ready for archival**: 3 published articles awaiting Medium URLs from user to run archive_article.py

## Key Design Decisions

### Medium Publishing Standards Centralization (2026-02-12 afternoon)
- **Architecture**: Single source of truth repository (`medium-publishing-standards`) prevents rule duplication drift across projects
- **Repository structure**:
  - `STANDARDS.md` - Canonical Medium platform rules (~974 lines)
  - `templates/export_for_medium.py` - Reference implementation for export scripts
  - `tools/archive_article.py` - Archive published articles (PDF + source + metadata)
  - `tools/update_index.py` - Regenerate INDEX.md from metadata.json files
  - `published/` - PDF snapshots, source markdown, figures, metadata
- **Global CLAUDE.md**: References standards repo (lines 157-169) instead of duplicating rules
- **Project CLAUDE.md**: References standards repo with quick reference section (lines 241-264)
- **Rationale**: Proven Medium rules across NFL + ratings projects should be maintained once, applied everywhere

### Medium Publishing Architecture (2026-02-12 morning)
- **Export format**: Full HTML document with DOCTYPE, html, head, body tags
- **Markdown conversion**: Python `markdown` library v3.4.3 with `tables` and `fenced_code` extensions (NOT regex)
- **Table handling**: Render tables as PNG images using matplotlib, embed as `<img>` tags (Medium does NOT render HTML `<table>` tags properly)
- **Image URLs**: GitHub Pages absolute URLs (`https://ghighcove.github.io/movie-ratings-analysis/figures/*.png`)
- **Cache busting**: Unique timestamped filenames with content hash (`{name}_{YYYYMMDD}_{HHMM}_{hash}.html`)
- **Deployment**: Git push → GitHub Pages rebuild (30sec) → import to Medium via `https://medium.com/p/import`

### Process Improvements (2026-02-12)
- **Three safeguards added to prevent cross-project lesson misses**:
  1. Global CLAUDE.md: Mandatory cross-project scan rule (read referenced projects' CLAUDE.md + lessons.md before planning)
  2. Global CLAUDE.md: Medium pre-flight checklist (grep all projects for Medium rules, confirm tables/images/filenames)
  3. Ratings CLAUDE.md: Complete NFL Medium rules duplicated locally (no dependency on cross-project reads) — NOW REPLACED with reference to standards repo
- **Root cause**: During initial Medium export planning, failed to read NFL project's documented lessons about table-as-PNG requirement, resulting in HTML `<table>` tags that Medium couldn't render

### Data and Analysis (from 2026-02-11)
- **TMDb API rate limiting**: 40 requests per 10 seconds with comprehensive caching (parquet + JSON)
- **Studio identification**: Tag major studios from production companies
- **Franchise detection**: Manual keyword mapping (73 films tagged)
- **Historical comparison**: 2010-2018 vs 2019-2024
- **Cutoff year finding**: 2008 marks correction/stabilization (not inflation start)

## Recent Changes (2026-02-12 session)

### Afternoon Work: Medium Standards Repository
- **Created repository**: `G:\ai\medium-publishing-standards\`
  - `STANDARDS.md` (974 lines) - Complete Medium platform rules, export workflow, troubleshooting guide
  - `README.md` - Repository purpose, quick start, structure
  - `templates/export_for_medium.py` - Reference implementation (176 lines)
  - `tools/archive_article.py` (231 lines) - Archive workflow with PDF generation, metadata, INDEX update
  - `tools/update_index.py` (76 lines) - Regenerate INDEX from all metadata.json files
  - `published/INDEX.md` - Portfolio index (empty, awaiting archival)
- **Pushed to GitHub**: https://github.com/ghighcove/medium-publishing-standards
- **Updated CLAUDE.md files**:
  - `C:\Users\ghigh\.claude\CLAUDE.md` - Lines 157-169 reference standards repo
  - `G:\ai\entertainment_metrics\ratings\CLAUDE.md` - Lines 241-264 reference standards repo with quick reference
- **Portfolio inventory**: Scanned NFL project, found 7 total articles:
  - 3 published (Player Value, Super Bowl Seats, Rating Inflation)
  - 2 in Medium drafts (Draft ROI GEO 99/100, TE Market GEO 97/100)
  - 2 ready to import (QB Deep Dive GEO 97/100, RB Economics GEO 95/100)

### Morning Work: Medium Export Debugging
- `scripts/export_for_medium.py` (175 lines) - Medium export with unique timestamped filenames, markdown library conversion
- `article/rating_inflation_20260212_1130_991e9cf8.html` (13,608 bytes) - Successfully imported to Medium
- `figures/table_high_rated_movies_by_era.png` - Table rendered as styled PNG (5 rows, highlighting 2010s)
- `article/medium_draft.md` - Replaced markdown table with PNG image reference
- Previous exports: `rating_inflation_20260212_1056_2aa104f6.html`, `rating_inflation_20260212_1123_84e7de76.html` (debugging iterations)

### Commits Pushed (2026-02-12)
**Ratings project:**
- `d882fc8` - Add Medium publishing workflow with cache-busting
- `30a5fdd` - Fix Medium export: replace regex converter with markdown library
- `e4e640f` - Fix Medium table: render as PNG image instead of HTML table
- `13c0c12` - Add Medium table-as-PNG rule to CLAUDE.md
- `4477e78` - Add complete Medium platform rules duplicated from NFL project

**Medium-publishing-standards project:**
- `c5c0d88` - Initial commit: STANDARDS.md, templates, tools, published/ structure
- `9ce2ded` - Update global and project CLAUDE.md to reference standards repo

## Blockers / Open Questions
- **Medium submission limit**: Reached daily import limit, cannot test further imports until tomorrow
- **Article 2 (manipulation)**: Not yet exported for Medium — use same workflow when ready
- **Archival pending**: 3 published articles need Medium URLs to run archive_article.py:
  1. NFL Player Value Analysis
  2. Super Bowl Ticket Price Analysis
  3. The Great Movie Rating Inflation (this project)

## Next Steps
1. **Archival**: Get Medium URLs for 3 published articles, run archive_article.py to create PDF snapshots and update published/INDEX.md
2. **NFL publishing schedule**: Decide on publication timing for 4 ready articles (2 in Medium drafts, 2 ready to import)
3. **Article 2 (manipulation)**: Export for Medium using same workflow when ready to publish
4. **Optional**: Test browser automation plugin for Medium import (if desired)

## Environment
- **Platform**: Windows 10 Home 10.0.19045
- **Python**: 3.8.x (32-bit) with pandas, numpy, scipy, matplotlib, seaborn, fastparquet, markdown (v3.4.3)
- **Working directory**: `G:\ai\entertainment_metrics\ratings`
- **Git repos**:
  - Analysis: https://github.com/ghighcove/movie-ratings-analysis (branch: main)
  - Standards: https://github.com/ghighcove/medium-publishing-standards (branch: main)
- **GitHub Pages**: https://ghighcove.github.io/movie-ratings-analysis/
- **TMDb API**: Free tier (40 req/10sec), key in .env file
- **Data cache**: Parquet files in `data/processed/`, TMDb responses in `data/processed/tmdb_cache/`

### Git Status (uncommitted)
- **Modified**: `.claude/settings.local.json` (1 file)
- **Untracked**: 11 files (old HTML exports, helper scripts, CSV files, tmdb_cache/, nul file, tasks/context.md)
- **Note**: Main work is committed and pushed across both repositories; uncommitted files are experimental/temporary
- **Age**: Modified within last few hours (no stale changes)

## Quick Reference
- **Project CLAUDE.md**: `G:\ai\entertainment_metrics\ratings\CLAUDE.md` (references standards repo)
- **Global CLAUDE.md**: `C:\Users\ghigh\.claude\CLAUDE.md` (references standards repo)
- **Medium standards**: `G:\ai\medium-publishing-standards\STANDARDS.md` (single source of truth)
- **Export script**: `scripts/export_for_medium.py`
- **Archive tool**: `G:\ai\medium-publishing-standards\tools\archive_article.py`
- **Article 1 (published)**: `article/medium_draft.md` → `article/rating_inflation_20260212_1130_991e9cf8.html`
- **Article 2 (draft)**: `article/manipulation_article_draft.md` (not yet exported for Medium)
- **Visualizations**: `visualizations/manipulation_*.png` (5 files from article 2)
- **Table images**: `figures/table_high_rated_movies_by_era.png`
- **GitHub repos**:
  - https://github.com/ghighcove/movie-ratings-analysis
  - https://github.com/ghighcove/medium-publishing-standards

## Portfolio Summary (All Projects)
**Total: 7 articles across 3 projects**

### Published (3)
1. **NFL Player Value Analysis** - NFL project (published to Medium, pending archival)
2. **Super Bowl Ticket Price Analysis** - NFL project (published to Medium, pending archival)
3. **The Great Movie Rating Inflation** - Ratings project (published 2026-02-12, pending archival)

### Ready/In-Draft (4)
1. **NFL Draft ROI** - NFL project (Medium draft, GEO 99/100, pending publication)
2. **NFL TE Market Inefficiency** - NFL project (Medium draft, GEO 97/100, pending schedule + SEO description)
3. **NFL QB Deep Dive** - NFL project (ready to import, GEO 97/100, deferred 3-5 days)
4. **NFL RB Economics** - NFL project (ready to import, GEO 95/100, deferred 3-5 days)

## Key Findings Summary (from analysis phase)

### Rating Inflation Investigation
- **Cutoff year**: 2008 (strongest statistical evidence)
- **Counter-intuitive finding**: Ratings DECREASED after 2008 (correction/stabilization, not inflation)
- **Timeline**: Pre-2000 mean 6.03 → 2000-2010 mean 6.22 (+0.19 inflation) → Post-2010 mean 6.07-6.17 (correction)
- **High-rated explosion**: 2010s had 184 movies ≥8.0 (3× more than 1950s-1980s), but with far fewer votes (110k median in 2020s vs 580k in 1990s)

### Manipulation Detection (article 2 draft)
- **Disney advantage**: +0.32 rating vs indies (6.40 vs 6.07) — LARGEST BOOST
- **Franchise coordination**: Action +0.93, Adventure +0.54 vs standalones
- **Benford's Law**: Vote count distribution trending toward violation (p=0.168→0.056)
- **Stability finding**: Manipulation is persistent since 2010, NOT escalating (contrary to initial hypothesis)
- **Evidence count**: 4/6 manipulation signatures detected

## Lessons Learned (Medium Publishing)

### What Worked
- Unique timestamped filenames with content hash → Medium cache bypass
- Python `markdown` library → correct HTML `<ul>`, `<li>` conversion
- Full HTML document structure (DOCTYPE, html, head, body) → Medium acceptance
- GitHub Pages URLs for images → reliable serving
- matplotlib table rendering → professional appearance, Medium compatibility
- **Centralized standards repository** → prevents rule drift, maintains consistency

### What Failed (and why)
- HTML `<table>` tags → Medium doesn't render them properly (columns run together)
- Regex-based markdown conversion → missed lists, tables, complex structures
- Reusing filenames → Medium serves stale cached content
- raw.githubusercontent.com for article import → Medium rejects (images work, articles don't)
- **Duplicating rules across projects** → drift, missed lessons, wasted debugging time

### Process Failures
- **Root cause of table issue**: Did not read NFL project's CLAUDE.md/lessons.md during planning despite explicit instruction and reference
- **Pattern**: Substituted thoroughness in execution for thoroughness in investigation — focused on making chosen approach work well instead of validating approach against documented lessons
- **Fix**: Three safeguards implemented (cross-project scan rule, pre-flight checklist, centralized standards repo) to prevent recurrence
