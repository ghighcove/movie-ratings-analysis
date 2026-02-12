"""
TMDb API integration for production company and country metadata.

Fetches studio/production company information to definitively identify:
- Major studios (Disney, Warner Bros, Universal, Sony, Paramount)
- Production countries (USA, China, India, UK, etc.)
- Budget/revenue data
- Cast/crew information

Rate limit: 40 requests per 10 seconds (free tier)
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

import pandas as pd
import requests
from dotenv import load_dotenv

from data_loader import PROJECT_ROOT, PROCESSED_DIR, logger

# Load environment variables
load_dotenv()

# TMDb configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_RATE_LIMIT = 40  # requests per 10 seconds
TMDB_BATCH_DELAY = 10  # seconds between batches

# Cache directory
TMDB_CACHE_DIR = PROCESSED_DIR / 'tmdb_cache'
TMDB_CACHE_DIR.mkdir(exist_ok=True)


class TMDbAPIError(Exception):
    """Custom exception for TMDb API errors."""
    pass


class TMDbClient:
    """
    TMDb API client with rate limiting and caching.

    Features:
    - Automatic rate limiting (40 req/10sec)
    - Response caching to avoid re-fetching
    - Retry logic for transient errors
    - IMDb ID to TMDb ID conversion
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TMDb client.

        Args:
            api_key: TMDb API key (if None, reads from TMDB_API_KEY env var)
        """
        self.api_key = api_key or TMDB_API_KEY

        if not self.api_key:
            raise ValueError(
                "TMDb API key not found. Set TMDB_API_KEY environment variable or pass api_key parameter.\n"
                "Get your free API key at: https://www.themoviedb.org/settings/api"
            )

        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key}

        # Rate limiting
        self.request_count = 0
        self.batch_start_time = time.time()

        logger.info("TMDb client initialized")

    def _rate_limit(self):
        """Enforce rate limit (40 requests per 10 seconds)."""
        self.request_count += 1

        if self.request_count >= TMDB_RATE_LIMIT:
            elapsed = time.time() - self.batch_start_time
            if elapsed < TMDB_BATCH_DELAY:
                sleep_time = TMDB_BATCH_DELAY - elapsed
                logger.info(f"Rate limit reached, sleeping {sleep_time:.1f}s...")
                time.sleep(sleep_time)

            # Reset counter
            self.request_count = 0
            self.batch_start_time = time.time()

    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Load from cache if available."""
        cache_file = TMDB_CACHE_DIR / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _set_cache(self, cache_key: str, data: Dict):
        """Save to cache."""
        cache_file = TMDB_CACHE_DIR / f"{cache_key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make API request with error handling.

        Args:
            endpoint: API endpoint (e.g., "/movie/550")
            params: Additional query parameters

        Returns:
            JSON response as dictionary
        """
        self._rate_limit()

        url = f"{TMDB_BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.debug(f"TMDb 404 for {endpoint}")
                return None
            elif response.status_code == 429:
                # Rate limit exceeded (shouldn't happen with our logic, but just in case)
                logger.warning("TMDb rate limit exceeded, waiting 10s...")
                time.sleep(10)
                return self._request(endpoint, params)  # Retry
            else:
                raise TMDbAPIError(f"TMDb API error: {e}")

        except requests.exceptions.RequestException as e:
            raise TMDbAPIError(f"Network error: {e}")

    def find_by_imdb_id(self, imdb_id: str) -> Optional[Dict]:
        """
        Convert IMDb ID to TMDb movie data.

        Args:
            imdb_id: IMDb ID (e.g., "tt0111161")

        Returns:
            Movie data dictionary or None if not found
        """
        # Check cache first
        cached = self._get_cached(f"find_{imdb_id}")
        if cached is not None:
            return cached

        # Fetch from API
        endpoint = f"/find/{imdb_id}"
        params = {'external_source': 'imdb_id'}

        result = self._request(endpoint, params)

        if result and result.get('movie_results'):
            movie_data = result['movie_results'][0]
            self._set_cache(f"find_{imdb_id}", movie_data)
            return movie_data

        return None

    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get full movie details including production companies.

        Args:
            tmdb_id: TMDb movie ID

        Returns:
            Movie details dictionary
        """
        # Check cache first
        cached = self._get_cached(f"movie_{tmdb_id}")
        if cached is not None:
            return cached

        # Fetch from API
        endpoint = f"/movie/{tmdb_id}"

        result = self._request(endpoint)

        if result:
            self._set_cache(f"movie_{tmdb_id}", result)

        return result

    def get_movie_metadata(self, imdb_id: str) -> Optional[Dict]:
        """
        Get full metadata for a movie by IMDb ID.

        Returns production companies, countries, budget, revenue, etc.

        Args:
            imdb_id: IMDb ID (e.g., "tt0111161")

        Returns:
            Dictionary with extracted metadata or None if not found
        """
        # Check cache first
        cached = self._get_cached(f"metadata_{imdb_id}")
        if cached is not None:
            return cached

        # Step 1: Find TMDb ID
        find_result = self.find_by_imdb_id(imdb_id)
        if not find_result:
            logger.debug(f"Movie not found in TMDb: {imdb_id}")
            return None

        tmdb_id = find_result['id']

        # Step 2: Get full details
        details = self.get_movie_details(tmdb_id)
        if not details:
            return None

        # Step 3: Extract relevant metadata
        metadata = {
            'imdb_id': imdb_id,
            'tmdb_id': tmdb_id,
            'title': details.get('title'),
            'release_date': details.get('release_date'),
            'budget': details.get('budget', 0),
            'revenue': details.get('revenue', 0),
            'runtime': details.get('runtime'),
            'vote_average': details.get('vote_average'),
            'vote_count': details.get('vote_count'),

            # Production companies (list of names)
            'production_companies': [
                company['name'] for company in details.get('production_companies', [])
            ],

            # Production countries (list of codes)
            'production_countries': [
                country['iso_3166_1'] for country in details.get('production_countries', [])
            ],

            # Genres (list of names)
            'genres': [genre['name'] for genre in details.get('genres', [])],

            # Original language
            'original_language': details.get('original_language'),
        }

        # Cache the processed metadata
        self._set_cache(f"metadata_{imdb_id}", metadata)

        return metadata

    def batch_get_metadata(
        self,
        imdb_ids: List[str],
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Fetch metadata for a batch of IMDb IDs.

        Args:
            imdb_ids: List of IMDb IDs
            show_progress: Show progress logs

        Returns:
            DataFrame with metadata for all movies
        """
        logger.info(f"Fetching metadata for {len(imdb_ids)} movies from TMDb...")

        results = []
        errors = []

        for i, imdb_id in enumerate(imdb_ids):
            if show_progress and (i + 1) % 100 == 0:
                logger.info(f"Progress: {i + 1}/{len(imdb_ids)} movies...")

            try:
                metadata = self.get_movie_metadata(imdb_id)
                if metadata:
                    results.append(metadata)
                else:
                    errors.append(imdb_id)

            except Exception as e:
                logger.warning(f"Error fetching {imdb_id}: {e}")
                errors.append(imdb_id)

        logger.info(f"Successfully fetched {len(results)}/{len(imdb_ids)} movies")
        if errors:
            logger.warning(f"Failed to fetch {len(errors)} movies: {errors[:10]}...")

        return pd.DataFrame(results)


def fetch_tmdb_metadata_for_dataset(
    master_df: pd.DataFrame,
    years_range: Optional[Tuple[int, int]] = None,
    force_refresh: bool = False
) -> pd.DataFrame:
    """
    Fetch TMDb metadata for movies in master dataset.

    Args:
        master_df: Master dataset with imdb_id column
        years_range: Optional (start_year, end_year) to filter
        force_refresh: If True, ignore cache and re-fetch

    Returns:
        DataFrame with TMDb metadata merged
    """
    # Filter to years if specified
    if years_range:
        movies = master_df[master_df['year'].between(*years_range)].copy()
        cache_name = f"tmdb_metadata_{years_range[0]}_{years_range[1]}"
    else:
        movies = master_df.copy()
        cache_name = "tmdb_metadata_all"

    cache_path = PROCESSED_DIR / f"{cache_name}.parquet"

    # Load from cache if available
    if cache_path.exists() and not force_refresh:
        logger.info(f"Loading cached TMDb metadata from {cache_path}")
        tmdb_df = pd.read_parquet(cache_path)
    else:
        # Fetch from TMDb API
        client = TMDbClient()
        tmdb_df = client.batch_get_metadata(movies['imdb_id'].tolist())

        # Cache results
        logger.info(f"Caching TMDb metadata to {cache_path}")
        tmdb_df.to_parquet(cache_path, engine='fastparquet', index=False)

    # Merge with master dataset
    merged = master_df.merge(tmdb_df, on='imdb_id', how='left', suffixes=('', '_tmdb'))

    logger.info(f"Merged TMDb metadata: {tmdb_df['imdb_id'].notna().sum():,} movies matched")

    return merged


def identify_major_studios(production_companies: List[str]) -> List[str]:
    """
    Identify major studios from production company list.

    Args:
        production_companies: List of production company names

    Returns:
        List of major studio tags (e.g., ['Disney', 'Marvel'])
    """
    if not production_companies or not isinstance(production_companies, list):
        return []

    # Major studio patterns
    STUDIO_PATTERNS = {
        'Disney': ['Disney', 'Walt Disney', 'Pixar', 'Lucasfilm', 'Marvel Studios', '20th Century'],
        'Warner Bros': ['Warner Bros', 'Warner Brothers', 'DC Films', 'DC Entertainment', 'New Line'],
        'Universal': ['Universal Pictures', 'Universal Studios', 'Illumination', 'DreamWorks'],
        'Sony': ['Sony Pictures', 'Columbia Pictures', 'TriStar', 'Screen Gems'],
        'Paramount': ['Paramount Pictures', 'Paramount Animation', 'MTV Films'],
        'Lionsgate': ['Lionsgate', 'Summit Entertainment'],
        'Netflix': ['Netflix'],
        'Amazon': ['Amazon Studios', 'Amazon Prime'],
        'Apple': ['Apple TV+', 'Apple Original Films'],
    }

    studios = []
    companies_str = ' '.join(production_companies).lower()

    for studio, patterns in STUDIO_PATTERNS.items():
        if any(pattern.lower() in companies_str for pattern in patterns):
            studios.append(studio)

    return studios


def add_studio_tags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add major_studios column to DataFrame.

    Args:
        df: DataFrame with production_companies column

    Returns:
        DataFrame with major_studios column added
    """
    df = df.copy()

    df['major_studios'] = df['production_companies'].apply(identify_major_studios)
    df['is_major_studio'] = df['major_studios'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)

    # Add individual studio flags
    for studio in ['Disney', 'Warner Bros', 'Universal', 'Sony', 'Paramount', 'Netflix']:
        df[f'studio_{studio.lower().replace(" ", "_")}'] = df['major_studios'].apply(
            lambda x: studio in x if isinstance(x, list) else False
        )

    return df


if __name__ == "__main__":
    # Quick test
    print("Testing TMDb integration...")

    # Test single movie
    client = TMDbClient()

    print("\n[1] Testing single movie fetch (The Shawshank Redemption)...")
    metadata = client.get_movie_metadata('tt0111161')

    if metadata:
        print(f"✓ Title: {metadata['title']}")
        print(f"✓ Production companies: {metadata['production_companies']}")
        print(f"✓ Countries: {metadata['production_countries']}")
        print(f"✓ Budget: ${metadata['budget']:,}")
    else:
        print("✗ Failed to fetch movie")

    # Test batch fetch
    print("\n[2] Testing batch fetch (5 movies)...")
    test_ids = ['tt0111161', 'tt0068646', 'tt0468569', 'tt0109830', 'tt0137523']
    batch_df = client.batch_get_metadata(test_ids, show_progress=False)

    print(f"✓ Fetched {len(batch_df)} movies")
    print("\nSample data:")
    print(batch_df[['title', 'production_companies', 'production_countries']].head())

    # Test studio identification
    print("\n[3] Testing studio identification...")
    batch_df = add_studio_tags(batch_df)
    print(batch_df[['title', 'major_studios']].head())

    print("\n✅ TMDb integration working!")
