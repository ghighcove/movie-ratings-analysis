"""
Data loading and caching for IMDb datasets, TMDb API, and historical lists.

Adapted from G:/ai/nfl/src/data_loader.py caching pattern.
"""

import gzip
import logging
from pathlib import Path
from typing import Optional, Callable, Tuple
import urllib.request

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
for dir_path in [RAW_DIR, PROCESSED_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# IMDb dataset URLs
IMDB_BASE_URL = "https://datasets.imdbws.com/"
IMDB_DATASETS = {
    "title_basics": "title.basics.tsv.gz",
    "title_ratings": "title.ratings.tsv.gz",
    "title_crew": "title.crew.tsv.gz",
    "name_basics": "name.basics.tsv.gz"
}


def _load_or_fetch(name: str, fetch_fn: Callable, force_refresh: bool = False) -> pd.DataFrame:
    """
    Load data from cache or fetch from source.

    Args:
        name: Dataset name (used for cache filename)
        fetch_fn: Function that fetches and returns DataFrame
        force_refresh: If True, ignore cache and re-fetch

    Returns:
        DataFrame with requested data
    """
    cache_path = PROCESSED_DIR / f"{name}.parquet"

    if cache_path.exists() and not force_refresh:
        logger.info(f"Loading cached {name} from {cache_path}")
        return pd.read_parquet(cache_path)

    logger.info(f"Fetching {name} from source...")
    df = fetch_fn()

    logger.info(f"Caching {name} to {cache_path}")
    df.to_parquet(cache_path, engine='fastparquet', index=False)

    return df


def _download_imdb_file(filename: str) -> Path:
    """
    Download IMDb dataset file if not already present.

    Args:
        filename: Name of the IMDb dataset file (e.g., "title.basics.tsv.gz")

    Returns:
        Path to downloaded file
    """
    url = IMDB_BASE_URL + filename
    local_path = RAW_DIR / filename

    if local_path.exists():
        logger.info(f"IMDb file already exists: {local_path}")
        return local_path

    logger.info(f"Downloading {filename} from {url}")
    urllib.request.urlretrieve(url, local_path)
    logger.info(f"Downloaded to {local_path}")

    return local_path


def _read_imdb_tsv(filepath: Path, columns: Optional[list] = None, chunksize: int = 100000) -> pd.DataFrame:
    """
    Read IMDb TSV file (gzip compressed) in chunks to handle large files.

    Args:
        filepath: Path to .tsv.gz file
        columns: Optional list of columns to keep (None = keep all)
        chunksize: Number of rows to read at a time

    Returns:
        DataFrame with IMDb data
    """
    logger.info(f"Reading {filepath.name} in chunks of {chunksize:,}...")

    # IMDb uses '\N' for null values
    chunks = []
    total_rows = 0

    for chunk in pd.read_csv(
        filepath,
        sep='\t',
        na_values=['\\N'],
        low_memory=False,
        usecols=columns,
        chunksize=chunksize
    ):
        chunks.append(chunk)
        total_rows += len(chunk)
        if total_rows % 500000 == 0:
            logger.info(f"  Processed {total_rows:,} rows...")

    df = pd.concat(chunks, ignore_index=True)
    logger.info(f"Loaded {len(df):,} rows from {filepath.name}")
    return df


def load_title_basics(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load IMDb title basics (metadata for all titles).

    Columns: tconst, titleType, primaryTitle, originalTitle, isAdult,
             startYear, endYear, runtimeMinutes, genres

    Args:
        force_refresh: If True, re-download and re-process

    Returns:
        DataFrame with title metadata
    """
    def fetch():
        filepath = _download_imdb_file(IMDB_DATASETS["title_basics"])

        # Read in chunks and filter for movies only to save memory
        logger.info("Reading and filtering for movies only...")
        chunks = []
        total_rows = 0
        movie_rows = 0

        for chunk in pd.read_csv(
            filepath,
            sep='\t',
            na_values=['\\N'],
            low_memory=False,
            chunksize=100000
        ):
            # Filter to movies only immediately
            chunk = chunk[chunk['titleType'] == 'movie'].copy()
            if len(chunk) > 0:
                chunks.append(chunk)
                movie_rows += len(chunk)

            total_rows += len(chunk)
            if total_rows % 500000 == 0:
                logger.info(f"  Processed {total_rows:,} rows, found {movie_rows:,} movies...")

        df = pd.concat(chunks, ignore_index=True)
        logger.info(f"Filtered to {len(df):,} movies from {total_rows:,} total titles")

        # Convert year to numeric (some are ranges like "2020-2023")
        df['startYear'] = pd.to_numeric(df['startYear'], errors='coerce')

        # Convert runtime to numeric
        df['runtimeMinutes'] = pd.to_numeric(df['runtimeMinutes'], errors='coerce')

        # Keep adult content flag as boolean
        df['isAdult'] = df['isAdult'] == '1'

        # Split genres into list
        df['genres'] = df['genres'].str.split(',')

        # Drop columns we don't need
        df = df.drop(columns=['titleType', 'originalTitle', 'endYear'], errors='ignore')

        # Rename for clarity
        df = df.rename(columns={
            'tconst': 'imdb_id',
            'primaryTitle': 'title',
            'startYear': 'year',
            'runtimeMinutes': 'runtime',
            'isAdult': 'adult'
        })

        return df

    return _load_or_fetch("title_basics", fetch, force_refresh)


def load_title_ratings(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load IMDb ratings (averageRating and numVotes).

    Columns: tconst, averageRating, numVotes

    Args:
        force_refresh: If True, re-download and re-process

    Returns:
        DataFrame with ratings
    """
    def fetch():
        filepath = _download_imdb_file(IMDB_DATASETS["title_ratings"])
        df = _read_imdb_tsv(filepath)

        # Rename for clarity
        df = df.rename(columns={
            'tconst': 'imdb_id',
            'averageRating': 'imdb_rating',
            'numVotes': 'num_votes'
        })

        return df

    return _load_or_fetch("title_ratings", fetch, force_refresh)


def load_title_crew(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load IMDb crew information (directors and writers).

    Columns: tconst, directors, writers

    Args:
        force_refresh: If True, re-download and re-process

    Returns:
        DataFrame with crew IDs
    """
    def fetch():
        filepath = _download_imdb_file(IMDB_DATASETS["title_crew"])
        df = _read_imdb_tsv(filepath)

        # Split director/writer IDs into lists
        df['directors'] = df['directors'].str.split(',')
        df['writers'] = df['writers'].str.split(',')

        # Rename for clarity
        df = df.rename(columns={'tconst': 'imdb_id'})

        return df

    return _load_or_fetch("title_crew", fetch, force_refresh)


def load_imdb_datasets(force_refresh: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load both title basics and ratings.

    Args:
        force_refresh: If True, re-download all datasets

    Returns:
        Tuple of (basics_df, ratings_df)
    """
    basics = load_title_basics(force_refresh)
    ratings = load_title_ratings(force_refresh)

    return basics, ratings


def merge_master_dataset(
    basics: pd.DataFrame,
    ratings: pd.DataFrame,
    crew: Optional[pd.DataFrame] = None,
    min_votes: int = 0
) -> pd.DataFrame:
    """
    Merge IMDb datasets into master movie dataset.

    Args:
        basics: Title basics DataFrame
        ratings: Title ratings DataFrame
        crew: Optional crew DataFrame
        min_votes: Minimum vote threshold (default: 0, no filtering)

    Returns:
        Master DataFrame with all movie data
    """
    logger.info("Merging IMDb datasets...")

    # Start with basics
    master = basics.copy()

    # Merge ratings
    master = master.merge(ratings, on='imdb_id', how='left')

    # Merge crew if provided
    if crew is not None:
        master = master.merge(crew, on='imdb_id', how='left')

    # Apply vote threshold
    if min_votes > 0:
        before = len(master)
        master = master[master['num_votes'] >= min_votes].copy()
        logger.info(f"Filtered to {len(master):,} movies with ≥{min_votes:,} votes (removed {before - len(master):,})")

    # Sort by year and votes
    master = master.sort_values(['year', 'num_votes'], ascending=[False, False])

    logger.info(f"Master dataset: {len(master):,} movies")
    logger.info(f"Year range: {master['year'].min():.0f} - {master['year'].max():.0f}")
    logger.info(f"Movies with ratings: {master['imdb_rating'].notna().sum():,}")

    return master


def validate_master_dataset(df: pd.DataFrame) -> dict:
    """
    Validate master dataset quality and return summary stats.

    Args:
        df: Master dataset DataFrame

    Returns:
        Dictionary with validation results
    """
    results = {
        'total_movies': len(df),
        'with_ratings': df['imdb_rating'].notna().sum(),
        'with_runtime': df['runtime'].notna().sum(),
        'year_range': (df['year'].min(), df['year'].max()),
        'duplicate_ids': df['imdb_id'].duplicated().sum(),
        'rating_range': (df['imdb_rating'].min(), df['imdb_rating'].max()),
        'avg_votes': df['num_votes'].mean(),
        'median_year': df['year'].median()
    }

    # Check IMDb ID format
    valid_ids = df['imdb_id'].str.match(r'^tt\d{7,8}$')
    results['invalid_ids'] = (~valid_ids).sum()

    logger.info("Dataset validation:")
    for key, value in results.items():
        logger.info(f"  {key}: {value}")

    # Assertions
    assert results['duplicate_ids'] == 0, "Found duplicate IMDb IDs!"
    assert results['invalid_ids'] == 0, "Found invalid IMDb ID formats!"
    assert results['total_movies'] > 40000, "Dataset suspiciously small!"

    return results


if __name__ == "__main__":
    # Quick test
    print("Loading IMDb datasets...")
    basics, ratings = load_imdb_datasets()

    print("\nMerging into master dataset...")
    master = merge_master_dataset(basics, ratings, min_votes=1000)

    print("\nValidating...")
    validate_master_dataset(master)

    print("\nSample records:")
    print(master.head())

    print("\n[SUCCESS] Data loader module working!")
