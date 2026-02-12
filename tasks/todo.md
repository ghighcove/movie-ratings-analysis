# Implementation Tasks

## Phase 1: Data Foundation (Week 1)

### Quick Wins (Days 1-3)
- [x] Set up project structure (directories, requirements.txt, CLAUDE.md)
- [x] Create data loader module with IMDb integration
- [ ] Test data loader: download IMDb datasets, cache to parquet
- [ ] Generate basic visualizations: movie count by year, rating distribution
- [ ] Parse IMDb Top 250 current + 1996 archive, compute overlap

### Core Data Pipeline
- [ ] Implement TMDb API integration with rate limiting
- [ ] Create historical lists parser (Sight & Sound, AFI, Top 250 archives)
- [ ] Merge all data sources into master dataset
- [ ] Validate master dataset (>50k films, no duplicates, valid IDs)

## Phase 2: Quality Metrics (Week 2)

- [ ] Implement critical acclaim score (weighted average of critic scores)
- [ ] Implement legacy score (presence in historical lists)
- [ ] Implement technical quality score (budget, runtime, crew pedigree)
- [ ] Genre-weighted composite quality score
- [ ] Z-score normalization within decade × genre cohorts
- [ ] Validate: Citizen Kane high, Gigli low, distribution normal

## Phase 3: Cutoff Analysis (Week 2-3)

- [ ] Implement 5 statistical tests (t-test, variance, Chow, Mann-Kendall, K-S)
- [ ] Rating inflation measurement (regression residuals)
- [ ] Run tests for all 5 candidate cutoff years
- [ ] Generate test statistic table with p-values and effect sizes
- [ ] Identify strongest cutoff candidate

## Phase 4: List Composition Analysis (Week 3)

- [ ] Temporal decay analysis (median year, % recent films)
- [ ] Entry/exit flow tracking for Top 250 over time
- [ ] Chi-square test: observed vs. expected counts by era
- [ ] Compute survival rates for pre/post cutoff films

## Phase 5: Final Visualizations (Week 4)

- [ ] Scatter: Quality vs. Current Rating (by era)
- [ ] Time series: Rating inflation over time
- [ ] Bar chart: Top 20 overrated/underrated films
- [ ] Heatmap: List composition by era
- [ ] Box plot: Rating distributions pre/post cutoff
- [ ] Sankey: List entry/exit flow
- [ ] Small multiples: Genre-specific trends
- [ ] Export high-res static (300 DPI) and interactive HTML

## Verification

- [ ] Data integrity: >50k films, valid IDs, no duplicates
- [ ] Quality metrics: classics high, flops low, normal distribution
- [ ] Statistical tests: all 5 cutoffs tested, p-values valid
- [ ] Visualizations: all 7 figures generated without errors
- [ ] End-to-end: run notebooks 01-05 in sequence

## Documentation

- [ ] Complete README with findings
- [ ] Document strongest cutoff year with evidence
- [ ] List top 20 overrated/underrated films
- [ ] Create publication-ready report
