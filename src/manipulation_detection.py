"""
Manipulation detection for IMDb ratings (2019-2024).

Implements statistical tests to detect coordinated rating campaigns by:
- Studios (franchise coordination)
- Advocacy groups (documentary genre anomalies)
- State actors (Chinese film proxies)
- Vote manipulation (Benford's Law violations)
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

from data_loader import PROJECT_ROOT, logger

# Analysis parameters
RECENT_YEARS = (2019, 2024)
HISTORICAL_CUTOFF = 2019
MIN_MOVIES_PER_GENRE = 10
BENFORD_EXPECTED = np.array([30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6])

# Franchise definitions (manual tagging for 2019-2024)
FRANCHISE_KEYWORDS = {
    'MCU': [
        'Avengers', 'Spider-Man', 'Thor', 'Black Widow', 'Eternals', 'Shang-Chi',
        'Doctor Strange', 'Black Panther', 'Guardians', 'Ant-Man', 'Captain Marvel',
        'Loki', 'WandaVision', 'Hawkeye', 'Moon Knight', 'She-Hulk', 'Wakanda'
    ],
    'DC': [
        'Batman', 'Superman', 'Wonder Woman', 'Aquaman', 'Flash', 'Black Adam',
        'Shazam', 'Joker', 'Suicide Squad', 'Peacemaker', 'Harley Quinn'
    ],
    'Star Wars': [
        'Mandalorian', 'Boba Fett', 'Ahsoka', 'Obi-Wan', 'Andor',
        'Rise of Skywalker', 'Bad Batch', 'Star Wars'
    ],
    'Fast & Furious': ['Fast', 'Furious', 'Hobbs & Shaw'],
    'John Wick': ['John Wick'],
    'Avatar': ['Avatar', 'Way of Water'],
    'Jurassic': ['Jurassic World', 'Jurassic Park'],
    'Mission Impossible': ['Mission: Impossible', 'Mission Impossible'],
    'Top Gun': ['Top Gun'],
    'Dune': ['Dune'],
}


def analyze_genre_anomalies(
    master_df: pd.DataFrame,
    years_range: Tuple[int, int] = RECENT_YEARS
) -> pd.DataFrame:
    """
    Detect genre rating patterns that deviate from historical baselines.

    Args:
        master_df: Master dataset with genres and ratings
        years_range: (start_year, end_year) for recent period

    Returns:
        DataFrame with genre analysis (recent vs. historical means, p-values, effect sizes)
    """
    logger.info(f"Analyzing genre anomalies for {years_range[0]}-{years_range[1]}...")

    # Split into recent and historical periods
    recent = master_df[master_df['year'].between(*years_range)].copy()
    historical = master_df[master_df['year'] < years_range[0]].copy()

    # Explode genres (movies can have multiple genres)
    recent_exploded = recent.explode('genres')
    historical_exploded = historical.explode('genres')

    # Compute statistics by genre
    results = []
    for genre in recent_exploded['genres'].dropna().unique():
        recent_genre = recent_exploded[recent_exploded['genres'] == genre]['imdb_rating'].dropna()
        hist_genre = historical_exploded[historical_exploded['genres'] == genre]['imdb_rating'].dropna()

        if len(recent_genre) < MIN_MOVIES_PER_GENRE or len(hist_genre) < MIN_MOVIES_PER_GENRE:
            continue

        # Statistics
        recent_mean = recent_genre.mean()
        hist_mean = hist_genre.mean()
        diff = recent_mean - hist_mean

        # T-test
        t_stat, p_value = stats.ttest_ind(recent_genre, hist_genre, equal_var=False)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((recent_genre.std()**2 + hist_genre.std()**2) / 2)
        cohens_d = diff / pooled_std if pooled_std > 0 else 0

        results.append({
            'genre': genre,
            'recent_mean': recent_mean,
            'historical_mean': hist_mean,
            'difference': diff,
            'recent_count': len(recent_genre),
            'historical_count': len(hist_genre),
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'effect_size_label': _effect_size_label(cohens_d),
            'suspicious': abs(cohens_d) > 0.5 and p_value < 0.01
        })

    results_df = pd.DataFrame(results).sort_values('cohens_d', ascending=False)

    logger.info(f"Found {results_df['suspicious'].sum()} suspicious genres with medium+ effect sizes")
    return results_df


def detect_vote_clustering(
    master_df: pd.DataFrame,
    years_range: Tuple[int, int] = RECENT_YEARS
) -> Dict:
    """
    Benford's Law analysis on vote counts to detect artificial voting patterns.

    Tests:
    1. First-digit distribution (should match Benford if organic)
    2. Round-number clustering (100, 500, 1000, 5000 spikes)
    3. Chi-square test for uniformity

    Args:
        master_df: Master dataset with num_votes
        years_range: (start_year, end_year) for analysis period

    Returns:
        Dictionary with Benford test results and round-number counts
    """
    logger.info(f"Running Benford's Law analysis for {years_range[0]}-{years_range[1]}...")

    # Filter to recent years
    recent = master_df[master_df['year'].between(*years_range)].copy()

    # Filter out NaN vote counts first
    recent = recent[recent['num_votes'].notna()].copy()

    # Extract first digit (exclude zeros)
    recent['first_digit'] = recent['num_votes'].astype(str).str[0].astype(int)
    recent = recent[recent['first_digit'] > 0]

    # Benford expected vs. observed
    observed_counts = recent['first_digit'].value_counts().sort_index()
    observed_pct = (observed_counts / observed_counts.sum() * 100).values

    # Pad to 9 digits if missing
    observed_full = np.zeros(9)
    observed_full[:len(observed_pct)] = observed_pct

    # Chi-square test against Benford
    chi2, p_value = stats.chisquare(observed_full, BENFORD_EXPECTED)

    # Round-number clustering
    round_numbers = [100, 500, 1000, 5000, 10000, 50000, 100000]
    round_counts = {num: (recent['num_votes'] == num).sum() for num in round_numbers}
    total_round = sum(round_counts.values())

    # Expected random clustering (should be ~0.1% of total)
    expected_random = len(recent) * 0.001 * len(round_numbers)
    clustering_ratio = total_round / expected_random if expected_random > 0 else 0

    results = {
        'chi2_statistic': chi2,
        'p_value': p_value,
        'benford_expected': BENFORD_EXPECTED,
        'benford_observed': observed_full,
        'round_number_counts': round_counts,
        'total_round_numbers': total_round,
        'clustering_ratio': clustering_ratio,
        'total_movies': len(recent),
        'manipulation_probability': 'HIGH' if p_value < 0.01 else 'MEDIUM' if p_value < 0.05 else 'LOW',
        'verdict': _benford_verdict(p_value, clustering_ratio)
    }

    logger.info(f"Benford chi2={chi2:.2f}, p={p_value:.4f}, manipulation={results['manipulation_probability']}")
    logger.info(f"Round-number clustering: {total_round} movies ({clustering_ratio:.1f}x expected)")

    return results


def detect_franchise_coordination(
    master_df: pd.DataFrame,
    franchise_map: Dict[str, List[str]] = FRANCHISE_KEYWORDS,
    years_range: Tuple[int, int] = RECENT_YEARS
) -> pd.DataFrame:
    """
    Compare rating patterns within franchise networks vs. standalone films.

    Tests:
    - Do franchise films rate higher than standalone films of same genre?
    - Statistical significance of the difference

    Args:
        master_df: Master dataset
        franchise_map: Dictionary mapping franchise names to keyword lists
        years_range: (start_year, end_year) for analysis period

    Returns:
        DataFrame with franchise analysis results
    """
    logger.info(f"Detecting franchise coordination for {years_range[0]}-{years_range[1]}...")

    # Filter to recent years
    recent = master_df[master_df['year'].between(*years_range)].copy()

    # Tag franchises
    recent['franchise'] = None
    for franchise, keywords in franchise_map.items():
        pattern = '|'.join(keywords)
        mask = recent['title'].str.contains(pattern, case=False, na=False, regex=True)
        recent.loc[mask, 'franchise'] = franchise

    recent['is_franchise'] = recent['franchise'].notna()

    # Explode genres for comparison
    recent_exploded = recent.explode('genres')

    # Compare by genre
    results = []
    for genre in ['Action', 'Sci-Fi', 'Adventure', 'Thriller', 'Drama']:
        genre_data = recent_exploded[recent_exploded['genres'] == genre]

        franchise_ratings = genre_data[genre_data['is_franchise']]['imdb_rating'].dropna()
        standalone_ratings = genre_data[~genre_data['is_franchise']]['imdb_rating'].dropna()

        if len(franchise_ratings) < 5 or len(standalone_ratings) < 10:
            continue

        franchise_mean = franchise_ratings.mean()
        standalone_mean = standalone_ratings.mean()
        diff = franchise_mean - standalone_mean

        # T-test
        t_stat, p_value = stats.ttest_ind(franchise_ratings, standalone_ratings, equal_var=False)

        # Effect size
        pooled_std = np.sqrt((franchise_ratings.std()**2 + standalone_ratings.std()**2) / 2)
        cohens_d = diff / pooled_std if pooled_std > 0 else 0

        results.append({
            'genre': genre,
            'franchise_mean': franchise_mean,
            'standalone_mean': standalone_mean,
            'difference': diff,
            'franchise_count': len(franchise_ratings),
            'standalone_count': len(standalone_ratings),
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'suspicious': diff > 0.3 and p_value < 0.05
        })

    results_df = pd.DataFrame(results).sort_values('difference', ascending=False)

    # Overall franchise summary
    franchise_films = recent[recent['is_franchise']]
    logger.info(f"Identified {len(franchise_films)} franchise films across {recent['franchise'].nunique()} franchises")
    logger.info(f"Mean franchise rating: {franchise_films['imdb_rating'].mean():.2f}")
    logger.info(f"Mean standalone rating: {recent[~recent['is_franchise']]['imdb_rating'].mean():.2f}")

    return results_df


def identify_chinese_films_proxy(
    master_df: pd.DataFrame,
    years_range: Tuple[int, int] = RECENT_YEARS
) -> pd.DataFrame:
    """
    Identify likely Chinese-influenced films using genre/title patterns.

    China markers:
    - Genre: Action+Drama+Adventure or War+History
    - Runtime: 120-140 minutes (censorship-friendly length)
    - Title contains: Dragon, Warrior, Legend, Dynasty, etc.

    Args:
        master_df: Master dataset
        years_range: (start_year, end_year) for analysis period

    Returns:
        DataFrame with suspected Chinese-influenced films
    """
    logger.info(f"Identifying Chinese film proxies for {years_range[0]}-{years_range[1]}...")

    recent = master_df[master_df['year'].between(*years_range)].copy()

    # Convert genres list to string for pattern matching
    recent['genres_str'] = recent['genres'].apply(lambda x: ','.join(x) if isinstance(x, list) else '')

    # China markers
    china_keywords = ['Dragon', 'Warrior', 'Legend', 'Dynasty', 'Crouching', 'Hidden',
                      'Tiger', 'Kung Fu', 'Shaolin', 'Wuxia', 'Mulan', 'Emperor']

    recent['china_marker_title'] = recent['title'].str.contains(
        '|'.join(china_keywords), case=False, na=False, regex=True
    )

    recent['china_marker_genre'] = (
        recent['genres_str'].str.contains('Action', case=False, na=False) &
        (recent['genres_str'].str.contains('Drama', case=False, na=False) |
         recent['genres_str'].str.contains('War', case=False, na=False) |
         recent['genres_str'].str.contains('History', case=False, na=False))
    )

    recent['china_marker_runtime'] = recent['runtime'].between(120, 140)

    # Score: count markers
    recent['china_score'] = (
        recent['china_marker_title'].astype(int) +
        recent['china_marker_genre'].astype(int) +
        recent['china_marker_runtime'].astype(int)
    )

    # Suspected Chinese films: 2+ markers
    chinese_films = recent[recent['china_score'] >= 2].copy()

    # Compute expected rating (simple baseline: genre median)
    chinese_films['expected_rating'] = chinese_films.apply(
        lambda row: master_df[
            (master_df['year'] < years_range[0]) &
            (master_df['genres'].apply(lambda g: any(genre in g for genre in row['genres']) if isinstance(g, list) else False))
        ]['imdb_rating'].median(),
        axis=1
    )

    chinese_films['rating_boost'] = chinese_films['imdb_rating'] - chinese_films['expected_rating']

    suspicious = chinese_films[chinese_films['rating_boost'] > 0.5].sort_values('rating_boost', ascending=False)

    logger.info(f"Identified {len(chinese_films)} likely Chinese-influenced films")
    logger.info(f"  {len(suspicious)} with suspicious rating boost (>0.5 points)")

    return suspicious[['title', 'year', 'imdb_rating', 'expected_rating', 'rating_boost',
                       'num_votes', 'runtime', 'genres', 'china_score']]


def analyze_documentary_manipulation(
    master_df: pd.DataFrame,
    years_range: Tuple[int, int] = RECENT_YEARS
) -> Dict:
    """
    Deep dive into Documentary genre to detect coordination patterns.

    Investigates:
    1. Vote-to-rating efficiency (rating per 1000 votes)
    2. Comparison to historical documentary baseline
    3. Sub-topic clustering (if detectable from titles)

    Args:
        master_df: Master dataset
        years_range: (start_year, end_year) for analysis period

    Returns:
        Dictionary with documentary analysis results
    """
    logger.info(f"Analyzing documentary manipulation for {years_range[0]}-{years_range[1]}...")

    # Extract documentaries
    master_df['is_doc'] = master_df['genres'].apply(
        lambda g: 'Documentary' in g if isinstance(g, list) else False
    )

    recent_docs = master_df[
        (master_df['year'].between(*years_range)) &
        (master_df['is_doc'])
    ].copy()

    historical_docs = master_df[
        (master_df['year'] < years_range[0]) &
        (master_df['is_doc'])
    ].copy()

    # Vote efficiency: rating per 1000 votes
    recent_docs['vote_efficiency'] = recent_docs['imdb_rating'] / (recent_docs['num_votes'] / 1000)
    historical_docs['vote_efficiency'] = historical_docs['imdb_rating'] / (historical_docs['num_votes'] / 1000)

    recent_efficiency = recent_docs['vote_efficiency'].mean()
    hist_efficiency = historical_docs['vote_efficiency'].mean()
    efficiency_boost = recent_efficiency - hist_efficiency

    # Statistical test
    t_stat, p_value = stats.ttest_ind(
        recent_docs['vote_efficiency'].dropna(),
        historical_docs['vote_efficiency'].dropna(),
        equal_var=False
    )

    # Identify high-efficiency outliers
    threshold = hist_efficiency + 2 * historical_docs['vote_efficiency'].std()
    suspicious_docs = recent_docs[recent_docs['vote_efficiency'] > threshold].copy()
    suspicious_docs = suspicious_docs.sort_values('vote_efficiency', ascending=False)

    results = {
        'recent_mean_rating': recent_docs['imdb_rating'].mean(),
        'historical_mean_rating': historical_docs['imdb_rating'].mean(),
        'recent_efficiency': recent_efficiency,
        'historical_efficiency': hist_efficiency,
        'efficiency_boost': efficiency_boost,
        't_statistic': t_stat,
        'p_value': p_value,
        'suspicious_count': len(suspicious_docs),
        'total_recent_docs': len(recent_docs),
        'suspicious_docs': suspicious_docs[['title', 'year', 'imdb_rating', 'num_votes', 'vote_efficiency']].head(20)
    }

    logger.info(f"Documentary analysis:")
    logger.info(f"  Recent mean rating: {results['recent_mean_rating']:.2f}")
    logger.info(f"  Historical mean rating: {results['historical_mean_rating']:.2f}")
    logger.info(f"  Vote efficiency boost: {efficiency_boost:.2f} (p={p_value:.4f})")
    logger.info(f"  Suspicious docs: {len(suspicious_docs)}/{len(recent_docs)}")

    return results


# Helper functions

def _effect_size_label(cohens_d: float) -> str:
    """Convert Cohen's d to interpretable label."""
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        return 'negligible'
    elif abs_d < 0.5:
        return 'small'
    elif abs_d < 0.8:
        return 'medium'
    else:
        return 'large'


def _benford_verdict(p_value: float, clustering_ratio: float) -> str:
    """Interpret Benford test results."""
    if p_value < 0.01 and clustering_ratio > 10:
        return "STRONG evidence of manipulation (Benford violation + round clustering)"
    elif p_value < 0.01:
        return "Benford violation detected - suggests artificial voting patterns"
    elif clustering_ratio > 10:
        return "Excessive round-number clustering - possible threshold gaming"
    else:
        return "No strong evidence of manipulation"


if __name__ == "__main__":
    # Quick test
    from data_loader import load_title_basics, load_title_ratings, merge_master_dataset

    print("Loading datasets...")
    basics = load_title_basics()
    ratings = load_title_ratings()
    master = merge_master_dataset(basics, ratings, min_votes=1000)

    print("\n" + "="*70)
    print("ANALYSIS 1: Genre Anomalies")
    print("="*70)
    genre_results = analyze_genre_anomalies(master)
    print(genre_results[genre_results['suspicious']])

    print("\n" + "="*70)
    print("ANALYSIS 2: Benford's Law (Vote Clustering)")
    print("="*70)
    benford_results = detect_vote_clustering(master)
    print(f"Chi-square: {benford_results['chi2_statistic']:.2f}")
    print(f"P-value: {benford_results['p_value']:.6f}")
    print(f"Verdict: {benford_results['verdict']}")

    print("\n" + "="*70)
    print("ANALYSIS 3: Franchise Coordination")
    print("="*70)
    franchise_results = detect_franchise_coordination(master)
    print(franchise_results)

    print("\n[SUCCESS] Manipulation detection module working!")
