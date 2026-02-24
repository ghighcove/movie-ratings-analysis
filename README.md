# Movie Ratings Manipulation Analysis

Testing the hypothesis that movie ratings became manipulated or untethered from objective quality metrics after a certain point in time.

## Hypothesis

Movie ratings systems (IMDb, Rotten Tomatoes, etc.) experienced a regime change where ratings became inflated or manipulated, disconnecting from objective quality indicators like critical acclaim, historical significance, and technical excellence.

## Approach

Adapt the NFL value-scoring framework where:
- **Objective Quality** = Weighted composite of critical acclaim (40%), historical legacy (35%), and technical quality (25%)
- **Current Rating** = User ratings from IMDb/RT (what audiences "pay")
- **Value Score** = Quality - Rating
  - Negative = Overrated (high rating, low quality)
  - Positive = Underrated (low rating, high quality)

## Candidate Cutoff Years

1. **1999 → 2000**: Digital revolution (CGI dominance)
2. **2007 → 2008**: Franchise era (MCU launch)
3. **2011 → 2012**: Social media weaponization
4. **2017 → 2018**: Platform gaming (RT scandal)
5. **2019 → 2020**: Streaming shift (pandemic)

## Data Sources

- **IMDb Official Datasets**: 64,000+ films with ratings and metadata
- **TMDb API**: Supplementary metadata (budgets, genres, runtime)
- **Historical Lists**: Sight & Sound (1952-2022), AFI Top 100 (1997, 2007), IMDb Top 250 archives

## Project Structure

```
movie-ratings-analysis/
├── data/
│   ├── raw/           # IMDb TSV files, list archives
│   ├── processed/     # Parquet files (master dataset, quality metrics)
│   └── cache/         # TMDb API responses
├── notebooks/
│   ├── 01_data_acquisition.ipynb
│   ├── 02_quality_metrics.ipynb
│   ├── 03_cutoff_analysis.ipynb
│   ├── 04_list_composition.ipynb
│   └── 05_final_visualizations.ipynb
├── src/
│   ├── data_loader.py    # IMDb/TMDb data pipeline
│   ├── quality_score.py  # Quality metrics computation
│   ├── cutoff_tests.py   # Statistical regime change tests
│   └── viz.py            # Visualization library
├── tasks/
│   ├── todo.md           # Implementation tracker
│   └── lessons.md        # Patterns and corrections
├── requirements.txt
├── CLAUDE.md            # Project-specific instructions
└── README.md
```

## Installation

```bash
cd movie-ratings-analysis
pip install -r requirements.txt
```

## Quick Start

```python
from src.data_loader import load_imdb_datasets, merge_master_dataset

# Load IMDb data (cached after first download)
basics, ratings = load_imdb_datasets()

# Create master dataset
master = merge_master_dataset(basics, ratings)

# Explore
print(f"Total films: {len(master):,}")
print(f"Films with 10k+ votes: {(master['num_votes'] >= 10000).sum():,}")
```

## Key Outputs

1. **Statistical Evidence**: Which cutoff year has strongest support (p-values, effect sizes)
2. **Rating Inflation Trends**: Time series showing residuals (actual - expected ratings)
3. **List Composition**: How "greatest films" lists have evolved over time
4. **Overrated/Underrated Films**: Top 20 in each category with value scores
5. **Visualizations**: 7 publication-quality figures (scatter, time series, heatmaps, box plots)

## Reference

This project adapts the methodology from [NFL Player Value Analysis](https://github.com/ghighcove/nfl-salary-analysis), applying value-scoring concepts to film ratings.

## Status

🔬 **Phase 1 Complete** - Major findings discovered!

- [x] Project structure created
- [x] Requirements defined
- [x] IMDb data loader implemented (737,654 movies loaded)
- [x] Master dataset merged and validated (338,940 with ratings)
- [x] Rating trend analysis with statistical testing
- [x] **Cutoff year identified: 2008 (strongest evidence, p<10⁻⁴⁶)**
- [ ] TMDb API integration (deprioritized - IMDb data sufficient)
- [ ] Historical lists parser (Wayback snapshots incomplete)

## 🎯 Key Findings

**The Hypothesis Was Backwards:** Rating inflation happened ~2000, then **corrected** post-2008.

### Timeline Discovered

1. **Pre-2000 (Baseline)**: Mean rating 6.03
2. **2000-2010 (Inflation Era)**: Mean rating 6.22 (+0.19 jump)
3. **Post-2010 (Correction)**: Mean rating 6.07-6.17 (stabilization)

### Evidence for 2008 as Cutoff Year

- **Mean difference**: -0.18 (ratings dropped after 2008)
- **Effect size**: Cohen's d = -0.152 (small-medium effect)
- **Statistical significance**:
  - t-test: p = 9.86×10⁻⁴⁶
  - K-S test: p = 1.55×10⁻³¹
- **Rank**: #1 of 5 candidate years tested

### High-Rated Movies Explosion

Movies rated ≥8.0 with 10k+ votes:
- 1950s-1980s: ~50-60 per decade
- 2010s: **184** (3x historical rate)
- But with **far fewer votes**: 110k median (2020s) vs. 580k (1990s)

## License

Data sources used under their respective licenses:
- IMDb datasets: Non-commercial use only
- TMDb API: Attribution required
