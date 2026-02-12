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
G:/ai/entertainment_metrics/ratings/
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
cd G:/ai/entertainment_metrics/ratings
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

This project adapts the methodology from [NFL Player Value Analysis](G:/ai/nfl/), applying value-scoring concepts to film ratings.

## Status

🚧 **In Development** - Phase 1: Data Foundation (Week 1)

- [x] Project structure created
- [x] Requirements defined
- [x] IMDb data loader implemented (737,654 movies loaded)
- [x] Master dataset merged and validated (47,765 movies with ≥1,000 votes)
- [x] Initial visualizations (rating distribution, movie count by year)
- [ ] TMDb API integration
- [ ] Historical lists parser (Sight & Sound, AFI, Top 250 archives)

## License

Data sources used under their respective licenses:
- IMDb datasets: Non-commercial use only
- TMDb API: Attribution required
