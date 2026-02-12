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

## Success Metrics

- [ ] Master dataset with >50k films and complete ratings
- [ ] Quality metrics validated (classics high, flops low)
- [ ] Statistical tests identify strongest cutoff candidate (p < 0.01)
- [ ] 7 key visualizations generated without errors
- [ ] Top 20 overrated/underrated films list published
- [ ] Reproducible pipeline (all notebooks run cleanly)
