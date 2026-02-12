"""
Rating trend analysis using IMDb master dataset.

Instead of relying on incomplete Wayback snapshots, analyze rating
distribution and trends over time using real IMDb data.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import numpy as np
from scipy import stats

from data_loader import PROCESSED_DIR, logger


def load_master_with_metadata() -> pd.DataFrame:
    """
    Load master dataset and add derived metadata.

    Returns:
        DataFrame with master data plus decade, era, and category fields
    """
    master_path = PROCESSED_DIR / "title_basics.parquet"
    ratings_path = PROCESSED_DIR / "title_ratings.parquet"

    if not master_path.exists() or not ratings_path.exists():
        raise FileNotFoundError(
            "Master datasets not found. Run data_loader.py first to download IMDb data."
        )

    logger.info("Loading master dataset...")
    basics = pd.read_parquet(master_path)
    ratings = pd.read_parquet(ratings_path)

    # Merge
    master = basics.merge(ratings, on='imdb_id', how='left')

    # Add derived fields
    master['decade'] = (master['year'] // 10) * 10
    master['era'] = pd.cut(
        master['year'],
        bins=[0, 1950, 1980, 2000, 2010, 2020, 3000],
        labels=['Pre-1950', '1950-1979', '1980-1999', '2000-2009', '2010-2019', '2020+']
    )

    # Categorize by rating (only for movies with sufficient votes)
    master['rating_category'] = 'Unknown'
    mask_rated = master['num_votes'] >= 1000

    master.loc[mask_rated & (master['imdb_rating'] >= 8.0), 'rating_category'] = 'Excellent (8.0+)'
    master.loc[mask_rated & (master['imdb_rating'] >= 7.0) & (master['imdb_rating'] < 8.0), 'rating_category'] = 'Good (7.0-7.9)'
    master.loc[mask_rated & (master['imdb_rating'] >= 6.0) & (master['imdb_rating'] < 7.0), 'rating_category'] = 'Average (6.0-6.9)'
    master.loc[mask_rated & (master['imdb_rating'] < 6.0), 'rating_category'] = 'Below Average (<6.0)'

    logger.info(f"Loaded {len(master):,} movies")
    logger.info(f"Movies with ratings: {master['imdb_rating'].notna().sum():,}")

    return master


def get_top_rated_by_era(master: pd.DataFrame, min_votes: int = 10000, n_top: int = 250) -> pd.DataFrame:
    """
    Get top-rated movies for each era with sufficient vote threshold.

    Args:
        master: Master dataset
        min_votes: Minimum votes required
        n_top: Number of top movies per era

    Returns:
        DataFrame with top movies by era
    """
    logger.info(f"Finding top {n_top} movies per era (min_votes={min_votes:,})...")

    results = []

    for era in master['era'].cat.categories:
        era_df = master[
            (master['era'] == era) &
            (master['num_votes'] >= min_votes) &
            (master['imdb_rating'].notna())
        ].copy()

        # Sort by rating (descending), then votes (descending) as tiebreaker
        era_df = era_df.sort_values(['imdb_rating', 'num_votes'], ascending=[False, False])

        top_era = era_df.head(n_top).copy()
        top_era['era_rank'] = range(1, len(top_era) + 1)

        results.append(top_era)

    combined = pd.concat(results, ignore_index=True)
    logger.info(f"Found {len(combined):,} top-rated movies across eras")

    return combined


def analyze_rating_inflation(master: pd.DataFrame, min_votes: int = 1000) -> pd.DataFrame:
    """
    Analyze rating trends over time to detect inflation.

    Args:
        master: Master dataset
        min_votes: Minimum votes threshold

    Returns:
        DataFrame with yearly statistics
    """
    logger.info("Analyzing rating inflation by year...")

    filtered = master[
        (master['num_votes'] >= min_votes) &
        (master['imdb_rating'].notna()) &
        (master['year'] >= 1950) &
        (master['year'] <= 2024)
    ].copy()

    yearly = filtered.groupby('year').agg({
        'imdb_rating': ['mean', 'median', 'std', 'count'],
        'num_votes': ['mean', 'median']
    }).reset_index()

    # Flatten column names
    yearly.columns = ['year', 'rating_mean', 'rating_median', 'rating_std', 'movie_count',
                      'votes_mean', 'votes_median']

    # Calculate z-score of mean rating (relative to overall mean)
    overall_mean = filtered['imdb_rating'].mean()
    overall_std = filtered['imdb_rating'].std()
    yearly['rating_zscore'] = (yearly['rating_mean'] - overall_mean) / overall_std

    logger.info(f"Analyzed {len(yearly)} years")

    return yearly


def test_cutoff_hypothesis(master: pd.DataFrame, cutoff_year: int, min_votes: int = 1000) -> dict:
    """
    Test regime change hypothesis for a specific cutoff year.

    Args:
        master: Master dataset
        cutoff_year: Year to test as cutoff
        min_votes: Minimum votes threshold

    Returns:
        Dictionary with test results
    """
    logger.info(f"Testing cutoff hypothesis for year {cutoff_year}...")

    filtered = master[
        (master['num_votes'] >= min_votes) &
        (master['imdb_rating'].notna()) &
        (master['year'] >= 1980) &
        (master['year'] <= 2024)
    ].copy()

    # Split into before/after cutoff
    before = filtered[filtered['year'] < cutoff_year]['imdb_rating']
    after = filtered[filtered['year'] >= cutoff_year]['imdb_rating']

    # T-test for mean difference
    t_stat, t_pvalue = stats.ttest_ind(before, after)

    # Levene's test for variance difference
    levene_stat, levene_pvalue = stats.levene(before, after)

    # Kolmogorov-Smirnov test for distribution difference
    ks_stat, ks_pvalue = stats.ks_2samp(before, after)

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((before.std()**2 + after.std()**2) / 2)
    cohens_d = (after.mean() - before.mean()) / pooled_std

    results = {
        'cutoff_year': cutoff_year,
        'n_before': len(before),
        'n_after': len(after),
        'mean_before': before.mean(),
        'mean_after': after.mean(),
        'mean_diff': after.mean() - before.mean(),
        'std_before': before.std(),
        'std_after': after.std(),
        't_statistic': t_stat,
        't_pvalue': t_pvalue,
        'levene_statistic': levene_stat,
        'levene_pvalue': levene_pvalue,
        'ks_statistic': ks_stat,
        'ks_pvalue': ks_pvalue,
        'cohens_d': cohens_d
    }

    logger.info(f"  Before {cutoff_year}: n={len(before):,}, mean={before.mean():.3f}")
    logger.info(f"  After {cutoff_year}: n={len(after):,}, mean={after.mean():.3f}")
    logger.info(f"  t-test: t={t_stat:.3f}, p={t_pvalue:.4f}")
    logger.info(f"  Cohen's d: {cohens_d:.3f}")

    return results


def compare_all_cutoffs(master: pd.DataFrame, min_votes: int = 1000) -> pd.DataFrame:
    """
    Test all candidate cutoff years and compare results.

    Args:
        master: Master dataset
        min_votes: Minimum votes threshold

    Returns:
        DataFrame with comparison of all cutoffs
    """
    cutoff_years = [2000, 2008, 2012, 2018, 2020]
    results = []

    for year in cutoff_years:
        logger.info(f"\n{'='*60}")
        result = test_cutoff_hypothesis(master, year, min_votes)
        results.append(result)

    df = pd.DataFrame(results)

    # Rank by multiple criteria
    df['t_rank'] = df['t_pvalue'].rank()
    df['levene_rank'] = df['levene_pvalue'].rank()
    df['ks_rank'] = df['ks_pvalue'].rank()
    df['combined_rank'] = (df['t_rank'] + df['levene_rank'] + df['ks_rank']) / 3

    df = df.sort_values('combined_rank')

    logger.info(f"\n{'='*60}")
    logger.info("Cutoff Comparison Summary:")
    logger.info(f"{'='*60}")
    for _, row in df.iterrows():
        logger.info(f"{row['cutoff_year']}: Combined Rank={row['combined_rank']:.2f}, "
                    f"Mean Diff={row['mean_diff']:+.3f}, Cohen's d={row['cohens_d']:+.3f}")

    return df


def analyze_high_rated_by_decade(master: pd.DataFrame, threshold: float = 8.0, min_votes: int = 10000) -> pd.DataFrame:
    """
    Count high-rated movies (≥threshold) by decade.

    Args:
        master: Master dataset
        threshold: Rating threshold (default: 8.0)
        min_votes: Minimum votes required

    Returns:
        DataFrame with counts by decade
    """
    logger.info(f"Analyzing movies with rating ≥{threshold} by decade...")

    filtered = master[
        (master['imdb_rating'] >= threshold) &
        (master['num_votes'] >= min_votes) &
        (master['decade'] >= 1950)
    ].copy()

    decade_counts = filtered.groupby('decade').agg({
        'imdb_id': 'count',
        'imdb_rating': ['mean', 'median'],
        'num_votes': ['mean', 'median']
    }).reset_index()

    decade_counts.columns = ['decade', 'count', 'rating_mean', 'rating_median',
                             'votes_mean', 'votes_median']

    logger.info(f"Found {len(filtered):,} high-rated movies across {len(decade_counts)} decades")

    return decade_counts


if __name__ == "__main__":
    print("Testing rating analysis module...\n")

    # Load data
    master = load_master_with_metadata()

    print("\n" + "="*60)
    print("1. Rating Distribution by Era")
    print("="*60)
    era_summary = master.groupby('era')['imdb_rating'].agg(['count', 'mean', 'median', 'std'])
    print(era_summary)

    print("\n" + "="*60)
    print("2. High-Rated Movies (>=8.0) by Decade")
    print("="*60)
    high_rated = analyze_high_rated_by_decade(master, threshold=8.0, min_votes=10000)
    print(high_rated)

    print("\n" + "="*60)
    print("3. Rating Inflation Analysis (1990-2024)")
    print("="*60)
    yearly = analyze_rating_inflation(master, min_votes=1000)
    recent = yearly[yearly['year'] >= 1990]
    print(recent[['year', 'movie_count', 'rating_mean', 'rating_zscore']].tail(10))

    print("\n" + "="*60)
    print("4. Testing Cutoff Hypothesis for 2012")
    print("="*60)
    result_2012 = test_cutoff_hypothesis(master, 2012, min_votes=1000)
    print(f"Mean difference: {result_2012['mean_diff']:+.3f}")
    print(f"t-test p-value: {result_2012['t_pvalue']:.4f}")
    print(f"Cohen's d: {result_2012['cohens_d']:+.3f}")

    print("\n[SUCCESS] Rating analysis module working!")
