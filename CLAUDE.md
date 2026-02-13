# Movie Ratings Manipulation Analysis - Project Instructions

## Project Overview

This project tests the hypothesis that movie ratings became manipulated or untethered from objective quality metrics after a certain point in time. We adapt the NFL value-scoring framework where **Value Score = Objective Quality - Current Rating** (negative = overrated, positive = underrated).

## Data Architecture Constraints

### IMDb Dataset Format
- **Source**: https://datasets.imdbws.com/ (VERIFIED: Do NOT use imdbcdn.com - that domain doesn't exist)
- **Format**: Tab-separated values (TSV), gzip compressed
- **Key files**:
  - `title.basics.tsv.gz` - Movie metadata (tconst, titleType, primaryTitle, startYear, runtimeMinutes, genres)
  - `title.ratings.tsv.gz` - User ratings (tconst, averageRating, numVotes)
- **Caching**: Always cache to parquet after first download, never re-download unless `force_refresh=True`
- **ID format**: IMDb IDs are strings like "tt0111161" (keep as strings, not integers)

### TMDb API Constraints
- **Rate limit**: 40 requests per 10 seconds (free tier)
- **Batch strategy**: Fetch in batches of 40 with 10-second delays between batches
- **Caching**: Cache all API responses to avoid re-fetching
- **API key**: Load from environment variable `TMDB_API_KEY` or `.env` file

### Historical Lists Sources
- **Sight & Sound**: Available via web scraping (Wikipedia lists or BFI site)
- **AFI Top 100**: Available via Wikipedia or AFI site
- **IMDb Top 250 Archives**: Use Wayback Machine API to fetch historical snapshots

## Quality Metrics Design

### Component Weights (Genre-Specific)
- **Drama**: 45% critical acclaim, 40% legacy, 15% technical
- **Action**: 30% critical acclaim, 25% legacy, 45% technical
- **Documentary**: 50% critical acclaim, 35% legacy, 15% technical
- **Comedy**: 40% critical acclaim, 35% legacy, 25% technical
- **Horror**: 35% critical acclaim, 30% legacy, 35% technical

### Normalization Rules
- **Always normalize within cohorts**: Decade × Genre (minimum 10 films per group)
- **Z-score formula**: `(value - group_mean) / group_std`
- **Handle outliers**: Winsorize at ±3σ before computing composites
- **Missing data**: If <2 components available, mark quality as NaN (don't compute from partial data)

## Verified Workflows

### HTML Report Generation
**CRITICAL RULE**: HTML reports MUST include embedded visualizations, not just text.

When creating HTML reports for user review:
- Use base64 encoding to embed images directly in HTML (makes files self-contained)
- OR use relative paths to image files if keeping images separate
- NEVER create text-only HTML reports - they're incomplete and not useful
- Each visualization should have a caption explaining what it shows

**Pattern:**
```python
import base64

def embed_image(img_path):
    with open(img_path, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{img_data}"

# In HTML template:
html += f'<img src="{embed_image("figures/chart.png")}" alt="Chart description">'
```

### Data Loading Pattern (Adapted from NFL Project)
```python
def _load_or_fetch(name: str, fetch_fn, force_refresh=False):
    path = DATA_DIR / f"{name}.parquet"
    if path.exists() and not force_refresh:
        logger.info(f"Loading cached {name} from {path}")
        return pd.read_parquet(path)
    logger.info(f"Fetching {name} from source...")
    df = fetch_fn()
    df.to_parquet(path, engine='fastparquet', index=False)
    logger.info(f"Cached {name} to {path}")
    return df
```

### Value Score Computation (Critical Pattern)
```python
# From NFL project - proven approach
value_score = objective_quality_zscore - current_rating_zscore
# Interpretation:
#   Negative = Overrated (high rating relative to quality)
#   Positive = Underrated (low rating relative to quality)
```

## Statistical Test Requirements

### Minimum Sample Sizes
- **t-test**: Minimum 30 films per group (before/after cutoff)
- **Chi-square**: Expected count ≥5 in each cell
- **Regression**: Minimum 100 observations for reliable residuals

### Significance Levels
- **Primary tests**: α = 0.01 (strict threshold for main claims)
- **Exploratory tests**: α = 0.05 (for supplementary analysis)
- **Effect size reporting**: Always report Cohen's d or η² alongside p-values

## Visualization Standards

### Color Schemes
- **Overrated/Underrated**: RdYlGn diverging colormap (red = overrated, green = underrated)
- **Time series**: Viridis or plasma for sequential data
- **Categorical**: Tab10 or Set3 for genres

### Export Standards
- **Static figures**: 300 DPI PNG/PDF for publication
- **Interactive**: HTML with Plotly for notebooks
- **Size**: 10x6 inches for standard plots, 12x8 for complex multi-panel

## Failed Approaches to Avoid

### Data Processing
- **DON'T** use `pd.read_csv()` without chunking for IMDb files - title.basics.tsv.gz is ~207 MB compressed, ~1+ GB uncompressed, causing memory errors on 32-bit Python. ALWAYS use `chunksize=100000` and filter during read.
- **DON'T** load entire dataset into memory then filter - filter for movies (`titleType == 'movie'`) DURING chunked reading to stay within memory limits.
- **DON'T** merge datasets without checking for duplicate IDs - IMDb has re-used IDs in rare cases.
- **DON'T** assume all IMDb years are integers - some are ranges like "2020-2023" (TV series).

### Statistical Analysis
- **DON'T** compare ratings across decades without normalization - rating distributions have changed over time.
- **DON'T** use raw vote counts as quality proxies - blockbusters have inflated counts.
- **DON'T** run tests without checking assumptions (normality, equal variance, independence).

## Verification Protocols

### Data Integrity Checks
1. Load master dataset, confirm >50,000 films with non-null ratings
2. Verify IMDb ID format: all start with "tt", 7-8 digits following
3. Check for duplicates: `assert df['imdb_id'].is_unique`
4. Validate year range: all years between 1900 and current year + 1

### Quality Metrics Validation
1. **Spot-check classics**: Citizen Kane (1941), The Godfather (1972) should score >90th percentile
2. **Spot-check flops**: Gigli (2003), Battlefield Earth (2000) should score <10th percentile
3. **Distribution check**: quality_composite should be approximately normal (Shapiro-Wilk test, p > 0.05)

### Statistical Test Validation
1. Verify p-values are in [0, 1] range
2. Check test statistics match expected sign (e.g., t > 0 if mean1 > mean2)
3. Confirm effect sizes align with p-values (large effect → small p-value)

## Reference Projects

### NFL Value Scoring (Primary Template)
- **Location**: `G:/ai/nfl/`
- **Key modules to adapt**:
  - `src/data_loader.py` - Caching pattern
  - `src/value_score.py` - Scoring methodology
  - `src/viz.py` - Visualization templates
- **Patterns to reuse**:
  - Parquet caching with `_load_or_fetch()`
  - Z-score normalization within position groups
  - Value score = Performance - Cost (inverted: negative = overrated)

## Known Limitations

1. **Historical rating snapshots**: Not available for most platforms - focus on list composition instead
2. **Western-centric lists**: S&S and AFI heavily favor English-language films - document bias
3. **Recency bias**: Recent films have fewer votes - apply minimum threshold (10k votes)
4. **Genre evolution**: Superhero genre didn't exist pre-2000 - handle missing cohorts gracefully
5. **Changing demographics**: IMDb user base has evolved - compare multiple platforms if possible

## Development Workflow

1. **Start with quick wins**: Day 1-3 goals are designed for immediate validation
2. **Use notebooks for exploration**: Notebooks 01-05 are sequential, build on each other
3. **Modularize reusable code**: Move validated notebook code to `src/` modules
4. **Verify before proceeding**: Each phase has verification steps - don't skip them
5. **Document surprises**: If findings contradict expectations, document in `tasks/lessons.md`

## Quality Consistency Rules

### Multiple Similar Outputs
**CRITICAL**: When creating multiple similar outputs (2+ articles, reports, analyses), you MUST maintain consistent quality across ALL outputs.

- If you find yourself taking shortcuts on the 2nd+ item because:
  - "I'm tired"
  - "This one is longer"
  - "I already did one well"
  - "Technically this meets the requirement"

  **STOP. Ask the user**: "I notice [item 2] is [longer/more complex/etc]. Should I apply the same detailed approach as [item 1], or is a simpler format acceptable?"

### The "Would I Read This?" Test
Before delivering HTML reports or any user-facing documents, ask yourself:

- Would I want to read this document myself?
- Would I find the visualization placement helpful or frustrating?
- Am I optimizing for task completion or user value?

If the answer to any is "no" or "unsure," **ask the user** before delivering.

### No Shortcuts Without Permission
If you're tempted to take a shortcut that reduces quality (even if technically meeting requirements):

1. **Recognize the temptation** - "I could do X the quick way..."
2. **Ask explicitly**: "For [task], I could do [full approach] or [shortcut]. The shortcut would [specific tradeoff]. Which do you prefer?"
3. **Never assume shortcuts are acceptable** just because they technically work

### Task Completion ≠ Task Done Right
"Done" means:
- ✅ Meets technical requirements
- ✅ Serves user's actual needs
- ✅ Maintains quality standards across all deliverables
- ✅ You'd be proud to show it

If all 4 aren't true, it's not done. Don't optimize for your efficiency at the expense of user value.

## Major Findings (2026-02-11)

### Cutoff Year: 2008 (Strongest Statistical Evidence)

**Counter-Intuitive Result:** Ratings **decreased** after 2008, not increased. The inflation happened BEFORE 2000, and 2008 marks a **correction/stabilization** period.

**Timeline:**
- **Pre-2000**: Mean 6.03 (baseline era)
- **2000-2010**: Mean 6.22 (inflation era, +0.19 jump)
- **Post-2010**: Mean 6.07-6.17 (correction era)

**Statistical Evidence for 2008:**
- Mean difference: -0.18 (p < 10⁻⁴⁶, Cohen's d = -0.152)
- Ranked #1 of 5 candidate years (2000/2008/2012/2018/2020)
- Both t-test and K-S test show extremely significant regime change

**High-Rated Movies (≥8.0):**
- Historical: 50-60 per decade (1950s-1980s)
- 2010s: 184 (3x increase)
- But with far fewer votes: 110k median (2020s) vs. 580k (1990s)
- **Interpretation**: More movies achieving high ratings with less scrutiny = quality dilution

**Implication:** The manipulation was the 2000-2010 inflation, likely driven by:
- Broader internet access (more casual voters)
- Review bombing/coordination campaigns emerging
- Platform changes encouraging higher ratings
- Digital revolution democratizing access (more voters, less discriminating)

## Medium Publishing Workflow

**MANDATORY**: Read `G:\ai\medium-publishing-standards\STANDARDS.md` before any Medium work.

That document is the **single source of truth** for all Medium platform rules. This section provides project-specific quick reference only.

### Complete Automated Workflow (this project)

**1. Export**:
```bash
python scripts/export_for_medium.py article/manipulation_article_draft.md
```
- Extracts title from markdown H1 (no hardcoded titles)
- Converts markdown to HTML with proper list formatting (no blank lines between numbered items)
- Generates unique timestamped filename for cache-busting
- Converts figure URLs to GitHub Pages URLs

**2. Push to GitHub** (triggers GitHub Pages rebuild):
```bash
git add article/{unique_filename}.html figures/ article/*.md scripts/
git commit -m "Add Medium export: {article_name}"
git push origin main
```

**3. Verify GitHub Pages** (wait 30-45 seconds):
```bash
curl -I https://ghighcove.github.io/movie-ratings-analysis/article/{unique_filename}.html
```
Expected: HTTP 200, content-type: text/html

**4. Import to Medium via Browser Automation**:
- Navigate to `https://medium.com/p/import`
- Enter GitHub Pages URL
- Click Import
- Wait for import to complete (~5-10 seconds)
- Verify: title/attribution separated, figures render, numbered lists display correctly

**5. Complete SEO Fields**:
- **Tags** (5 max): Data Analysis, Movies, IMDb, Statistics, Film Analysis
- **Preview Image**: Verify figure from article displays (or upload custom)
- **Subtitle**: Auto-populated from attribution block (verify under 140 chars)

**6. Prompt User for Schedule Date**:
**IMPORTANT**: Always ask: *"What date would you like to schedule this article for?"*
- Do NOT assume a date
- Accept format: MM/DD, MM/DD/YYYY, or "publish now"

**7. Schedule Article**:
- Click "Schedule for later"
- Select user-specified date in calendar
- Choose time (default or user preference)
- Click "Schedule to publish"
- Verify: Article shows as "Scheduled" in drafts

**8. After publication, archive for portfolio**:
```bash
python G:/ai/medium-publishing-standards/tools/archive_article.py \
  --source="G:/ai/entertainment_metrics/ratings/article/{article_file}.md" \
  --medium-url="https://medium.com/@ghighcove/{slug}" \
  --project="ratings" \
  --title="{Article Title}" \
  --geo-score="98"
```

### Common Issues & Fixes

**Numbered lists showing blank bullets:**
- **Cause**: Blank lines between numbered list items cause markdown parser to wrap each in `<p>` tags
- **Fix**: Remove blank lines between `1. `, `2. `, `3. ` items in source markdown

**Title mixed with attribution:**
- **Cause**: Export script using hardcoded title instead of extracting from H1
- **Fix**: Ensure `export_for_medium.py` extracts title with `re.search(r'^# (.+)$', markdown_content, re.MULTILINE)`

**Figures not rendering:**
- **Cause**: Using `raw.githubusercontent.com` (returns text/plain) instead of GitHub Pages
- **Fix**: Always use `ghighcove.github.io/movie-ratings-analysis/` URLs

### Critical Rules (see STANDARDS.md for full details)

- ✅ Tables = PNG images (not HTML `<table>` tags)
- ✅ Unique timestamped filenames (bypass Medium caching)
- ✅ GitHub Pages URLs (not raw.githubusercontent.com)
- ✅ Full HTML document structure (DOCTYPE, html, head, body)
- ✅ Python `markdown` library (not regex)

## Success Metrics

- [ ] Master dataset with >50k films and complete ratings
- [ ] Quality metrics validated (classics high, flops low)
- [ ] Statistical tests identify strongest cutoff candidate (p < 0.01)
- [ ] 7 key visualizations generated without errors
- [ ] Top 20 overrated/underrated films list published
- [ ] Reproducible pipeline (all notebooks run cleanly)
