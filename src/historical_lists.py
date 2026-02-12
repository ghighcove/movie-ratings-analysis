"""
Historical movie lists parser for Wayback Machine snapshots and other sources.

Fetches IMDb Top 250 from different years to analyze list composition changes.
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

from data_loader import CACHE_DIR, PROCESSED_DIR, logger

# Wayback Machine API
WAYBACK_API = "http://archive.org/wayback/available"
WAYBACK_URL = "https://web.archive.org/web/{timestamp}/{url}"

# IMDb Top 250 URL
IMDB_TOP250_URL = "https://www.imdb.com/chart/top"

# Target years for historical snapshots
SNAPSHOT_YEARS = [1996, 2000, 2005, 2010, 2015, 2020, 2024]


def get_wayback_snapshot(url: str, year: int, month: int = 12, day: int = 31) -> Optional[str]:
    """
    Get Wayback Machine snapshot URL closest to specified date.

    Args:
        url: Original URL to find snapshot for
        year: Target year
        month: Target month (default: December)
        day: Target day (default: 31st)

    Returns:
        Wayback Machine snapshot URL, or None if not found
    """
    target_date = f"{year}{month:02d}{day:02d}"

    params = {
        'url': url,
        'timestamp': target_date
    }

    try:
        logger.info(f"Querying Wayback Machine for {url} around {year}...")
        response = requests.get(WAYBACK_API, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'archived_snapshots' in data and 'closest' in data['archived_snapshots']:
            snapshot = data['archived_snapshots']['closest']
            if snapshot['available']:
                timestamp = snapshot['timestamp']
                snapshot_url = snapshot['url']
                snapshot_date = datetime.strptime(timestamp, '%Y%m%d%H%M%S').date()
                logger.info(f"Found snapshot from {snapshot_date}: {snapshot_url}")
                return snapshot_url

        logger.warning(f"No snapshot found for {url} around {year}")
        return None

    except Exception as e:
        logger.error(f"Error fetching Wayback snapshot: {e}")
        return None


def fetch_snapshot_html(snapshot_url: str, cache_filename: str) -> Optional[str]:
    """
    Fetch HTML from Wayback Machine snapshot with caching.

    Args:
        snapshot_url: Wayback Machine URL
        cache_filename: Filename for cached HTML

    Returns:
        HTML content as string, or None if fetch failed
    """
    cache_path = CACHE_DIR / cache_filename

    # Check cache first
    if cache_path.exists():
        logger.info(f"Loading cached HTML from {cache_path}")
        return cache_path.read_text(encoding='utf-8')

    try:
        logger.info(f"Fetching HTML from {snapshot_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(snapshot_url, headers=headers, timeout=30)
        response.raise_for_status()

        html = response.text

        # Cache for future use
        logger.info(f"Caching HTML to {cache_path}")
        cache_path.write_text(html, encoding='utf-8')

        return html

    except Exception as e:
        logger.error(f"Error fetching snapshot HTML: {e}")
        return None


def parse_imdb_top250(html: str) -> List[Dict[str, str]]:
    """
    Parse IMDb Top 250 HTML to extract movie information.

    Args:
        html: HTML content from IMDb Top 250 page

    Returns:
        List of dicts with movie info (rank, imdb_id, title, year)
    """
    soup = BeautifulSoup(html, 'html.parser')
    movies = []

    # IMDb has changed their HTML structure over the years
    # Try multiple patterns to handle different formats

    # Modern format (2020+): <li> tags with data-testid
    modern_items = soup.find_all('li', {'class': re.compile(r'ipc-metadata-list-summary-item')})
    if modern_items:
        logger.info(f"Parsing modern format ({len(modern_items)} items found)")
        for idx, item in enumerate(modern_items, 1):
            try:
                # Extract title and year
                title_elem = item.find('h3', {'class': re.compile(r'ipc-title__text')})
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    # Format: "1. The Shawshank Redemption"
                    title_match = re.search(r'^\d+\.\s*(.+)$', title_text)
                    title = title_match.group(1) if title_match else title_text

                # Extract IMDb ID from link
                link = item.find('a', href=re.compile(r'/title/tt\d+'))
                imdb_id = None
                if link:
                    href = link['href']
                    id_match = re.search(r'/(tt\d+)/', href)
                    if id_match:
                        imdb_id = id_match.group(1)

                # Extract year
                year_elem = item.find('span', {'class': re.compile(r'sc-.*-year')})
                year = None
                if year_elem:
                    year_text = year_elem.get_text(strip=True)
                    year_match = re.search(r'\d{4}', year_text)
                    if year_match:
                        year = int(year_match.group(0))

                if imdb_id:
                    movies.append({
                        'rank': idx,
                        'imdb_id': imdb_id,
                        'title': title,
                        'year': year
                    })

            except Exception as e:
                logger.warning(f"Error parsing modern format item {idx}: {e}")
                continue

    # Legacy format (1996-2019): <tr> tags in table
    if not movies:
        legacy_items = soup.find_all('tr')
        logger.info(f"Parsing legacy format ({len(legacy_items)} rows found)")
        for item in legacy_items:
            try:
                # Find title cell
                title_cell = item.find('td', {'class': 'titleColumn'})
                if not title_cell:
                    continue

                # Extract rank
                rank_text = title_cell.get_text(strip=True).split('.')[0].strip()
                rank = int(rank_text) if rank_text.isdigit() else None

                # Extract title link
                link = title_cell.find('a')
                if not link:
                    continue

                title = link.get_text(strip=True)
                href = link.get('href', '')
                id_match = re.search(r'/(tt\d+)/', href)
                imdb_id = id_match.group(1) if id_match else None

                # Extract year
                year_span = title_cell.find('span', {'class': 'secondaryInfo'})
                year = None
                if year_span:
                    year_text = year_span.get_text(strip=True)
                    year_match = re.search(r'\d{4}', year_text)
                    if year_match:
                        year = int(year_match.group(0))

                if imdb_id and rank:
                    movies.append({
                        'rank': rank,
                        'imdb_id': imdb_id,
                        'title': title,
                        'year': year
                    })

            except Exception as e:
                logger.warning(f"Error parsing legacy format item: {e}")
                continue

    logger.info(f"Parsed {len(movies)} movies from HTML")
    return movies


def fetch_imdb_top250_snapshot(year: int, force_refresh: bool = False) -> Optional[pd.DataFrame]:
    """
    Fetch IMDb Top 250 for a specific year from Wayback Machine.

    Args:
        year: Target year (e.g., 1996, 2000, 2005)
        force_refresh: If True, ignore cache and re-fetch

    Returns:
        DataFrame with Top 250 movies from that year
    """
    cache_filename = f"imdb_top250_{year}.json"
    cache_path = PROCESSED_DIR / cache_filename

    # Check processed cache
    if cache_path.exists() and not force_refresh:
        logger.info(f"Loading cached Top 250 from {year}")
        df = pd.read_json(cache_path)
        return df

    # Get Wayback snapshot URL
    snapshot_url = get_wayback_snapshot(IMDB_TOP250_URL, year)
    if not snapshot_url:
        logger.error(f"Could not find Wayback snapshot for {year}")
        return None

    # Fetch HTML
    html_cache = f"imdb_top250_{year}.html"
    html = fetch_snapshot_html(snapshot_url, html_cache)
    if not html:
        logger.error(f"Could not fetch HTML for {year}")
        return None

    # Parse HTML
    movies = parse_imdb_top250(html)
    if not movies:
        logger.error(f"Could not parse movies from {year} HTML")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(movies)
    df['snapshot_year'] = year

    # Cache processed data
    logger.info(f"Caching processed Top 250 to {cache_path}")
    df.to_json(cache_path, orient='records', indent=2)

    logger.info(f"Fetched {len(df)} movies from Top 250 ({year})")
    return df


def fetch_all_top250_snapshots(years: Optional[List[int]] = None,
                                force_refresh: bool = False) -> Dict[int, pd.DataFrame]:
    """
    Fetch IMDb Top 250 for multiple years.

    Args:
        years: List of years to fetch (default: SNAPSHOT_YEARS)
        force_refresh: If True, re-fetch all snapshots

    Returns:
        Dictionary mapping year -> DataFrame
    """
    if years is None:
        years = SNAPSHOT_YEARS

    snapshots = {}

    for year in years:
        logger.info(f"\n{'='*60}")
        logger.info(f"Fetching Top 250 for {year}")
        logger.info(f"{'='*60}")

        df = fetch_imdb_top250_snapshot(year, force_refresh=force_refresh)
        if df is not None:
            snapshots[year] = df

        # Be nice to Wayback Machine API
        time.sleep(2)

    logger.info(f"\nSuccessfully fetched {len(snapshots)}/{len(years)} snapshots")
    return snapshots


def analyze_list_overlap(snapshots: Dict[int, pd.DataFrame]) -> pd.DataFrame:
    """
    Analyze overlap between Top 250 lists across years.

    Args:
        snapshots: Dictionary mapping year -> DataFrame

    Returns:
        DataFrame with overlap statistics
    """
    years = sorted(snapshots.keys())
    results = []

    for i, year1 in enumerate(years):
        for year2 in years[i+1:]:
            df1 = snapshots[year1]
            df2 = snapshots[year2]

            ids1 = set(df1['imdb_id'])
            ids2 = set(df2['imdb_id'])

            overlap = ids1 & ids2
            only_year1 = ids1 - ids2
            only_year2 = ids2 - ids1

            results.append({
                'year1': year1,
                'year2': year2,
                'year_diff': year2 - year1,
                'overlap_count': len(overlap),
                'overlap_pct': len(overlap) / 250 * 100,
                'only_year1_count': len(only_year1),
                'only_year2_count': len(only_year2)
            })

    return pd.DataFrame(results)


if __name__ == "__main__":
    # Test: fetch current Top 250 and one historical snapshot
    print("Testing historical lists fetcher...\n")

    # Test 1996 snapshot (oldest)
    print("Fetching 1996 snapshot...")
    df_1996 = fetch_imdb_top250_snapshot(1996)
    if df_1996 is not None:
        print(f"\n1996 Top 10:")
        print(df_1996.head(10)[['rank', 'title', 'year']])

    print("\n" + "="*60)

    # Test 2024 snapshot (most recent)
    print("\nFetching 2024 snapshot...")
    df_2024 = fetch_imdb_top250_snapshot(2024)
    if df_2024 is not None:
        print(f"\n2024 Top 10:")
        print(df_2024.head(10)[['rank', 'title', 'year']])

    # Compare overlap
    if df_1996 is not None and df_2024 is not None:
        ids_1996 = set(df_1996['imdb_id'])
        ids_2024 = set(df_2024['imdb_id'])
        overlap = ids_1996 & ids_2024

        print(f"\n{'='*60}")
        print(f"Overlap Analysis:")
        print(f"  1996: {len(ids_1996)} movies")
        print(f"  2024: {len(ids_2024)} movies")
        print(f"  Overlap: {len(overlap)} movies ({len(overlap)/250*100:.1f}%)")
        print(f"  Only in 1996: {len(ids_1996 - ids_2024)} movies")
        print(f"  Only in 2024: {len(ids_2024 - ids_1996)} movies")

    print("\n[SUCCESS] Historical lists module working!")
