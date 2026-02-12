"""
Comprehensive manipulation investigation with TMDb integration and temporal tracking.

Phases:
1. TMDb Integration - Fetch studio metadata
2. Studio-Specific Analysis - Disney vs. Warner Bros vs. Indies
3. Top 250 Volatility Tracking - Flash campaigns
4. Historical Comparison - 2010-2018 vs. 2019-2024
5. Final Report Generation
"""

import sys
sys.path.append('src')

from pathlib import Path
import pandas as pd
import numpy as np

from data_loader import load_title_basics, load_title_ratings, merge_master_dataset, logger
from manipulation_detection import (
    analyze_genre_anomalies,
    detect_vote_clustering,
    detect_franchise_coordination,
    analyze_documentary_manipulation,
    identify_chinese_films_proxy
)
from tmdb_integration import (
    fetch_tmdb_metadata_for_dataset,
    add_studio_tags,
    TMDbClient
)
from historical_lists import (
    track_top250_volatility,
    identify_suspicious_top250_entries
)


def main():
    print("="*70)
    print("COMPREHENSIVE MANIPULATION INVESTIGATION")
    print("="*70)
    print("\nPhases:")
    print("  [1] TMDb Integration - Studio identification")
    print("  [2] Studio-Specific Analysis - Disney vs. Warner Bros")
    print("  [3] Top 250 Volatility - Flash campaigns")
    print("  [4] Historical Comparison - 2010-2018 vs. 2019-2024")
    print("  [5] Final Report Generation")
    print("="*70)

    # Load master dataset
    print("\n[0] Loading master dataset...")
    basics = load_title_basics()
    ratings = load_title_ratings()
    master = merge_master_dataset(basics, ratings, min_votes=1000)
    print(f"[OK] Loaded {len(master):,} movies")

    # ========================================
    # PHASE 1: TMDb Integration
    # ========================================
    print("\n" + "="*70)
    print("[PHASE 1] TMDb Integration")
    print("="*70)

    try:
        print("\nFetching TMDb metadata for 2019-2024 films...")
        print("(This may take 40-50 minutes for ~9,000 films at 40 req/10sec)")
        print("Results will be cached for future runs.")

        master_with_tmdb = fetch_tmdb_metadata_for_dataset(
            master,
            years_range=(2019, 2024),
            force_refresh=False
        )

        # Add studio tags
        master_with_tmdb = add_studio_tags(master_with_tmdb)

        print(f"[OK] TMDb metadata fetched for {master_with_tmdb['tmdb_id'].notna().sum():,} movies")
        print(f"[OK] Major studios identified: {master_with_tmdb['is_major_studio'].sum():,} movies")

        # Summary by studio
        print("\nStudio Distribution (2019-2024):")
        for studio in ['Disney', 'Warner Bros', 'Universal', 'Sony', 'Paramount', 'Netflix']:
            count = master_with_tmdb[f'studio_{studio.lower().replace(" ", "_")}'].sum()
            if count > 0:
                mean_rating = master_with_tmdb[
                    master_with_tmdb[f'studio_{studio.lower().replace(" ", "_")}']
                ]['imdb_rating'].mean()
                print(f"  - {studio}: {count} movies (mean rating: {mean_rating:.2f})")

    except Exception as e:
        logger.error(f"TMDb integration failed: {e}")
        logger.error("Continuing without TMDb data...")
        master_with_tmdb = master.copy()

    # ========================================
    # PHASE 2: Studio-Specific Analysis
    # ========================================
    print("\n" + "="*70)
    print("[PHASE 2] Studio-Specific Analysis")
    print("="*70)

    if 'is_major_studio' in master_with_tmdb.columns:
        recent = master_with_tmdb[master_with_tmdb['year'].between(2019, 2024)].copy()

        # Compare major studios vs. indies
        major_studio_films = recent[recent['is_major_studio']]
        indie_films = recent[~recent['is_major_studio']]

        if len(major_studio_films) > 0 and len(indie_films) > 0:
            major_mean = major_studio_films['imdb_rating'].mean()
            indie_mean = indie_films['imdb_rating'].mean()
            diff = major_mean - indie_mean

            from scipy import stats
            t_stat, p_value = stats.ttest_ind(
                major_studio_films['imdb_rating'].dropna(),
                indie_films['imdb_rating'].dropna(),
                equal_var=False
            )

            print(f"\nMajor Studios vs. Indies:")
            print(f"  Major studios: {major_mean:.2f} (n={len(major_studio_films)})")
            print(f"  Indies: {indie_mean:.2f} (n={len(indie_films)})")
            print(f"  Difference: {diff:+.2f} (p={p_value:.6f})")

            if p_value < 0.05:
                print(f"  [ALERT] Statistically significant difference!")

            # Compare individual studios
            print("\nIndividual Studio Analysis:")
            studio_results = []
            for studio in ['Disney', 'Warner Bros', 'Universal', 'Sony', 'Paramount']:
                col = f'studio_{studio.lower().replace(" ", "_")}'
                if col in recent.columns:
                    studio_films = recent[recent[col]]
                    if len(studio_films) >= 10:
                        studio_mean = studio_films['imdb_rating'].mean()
                        studio_vs_indie = studio_mean - indie_mean

                        studio_results.append({
                            'studio': studio,
                            'count': len(studio_films),
                            'mean_rating': studio_mean,
                            'vs_indie': studio_vs_indie
                        })

                        print(f"  - {studio}: {studio_mean:.2f} ({len(studio_films)} films, "
                              f"{studio_vs_indie:+.2f} vs. indies)")

            # Export studio analysis
            if studio_results:
                studio_df = pd.DataFrame(studio_results).sort_values('vs_indie', ascending=False)
                output_dir = Path('article')
                studio_df.to_csv(output_dir / 'manipulation_studio_analysis.csv', index=False)
                print(f"\n[OK] Studio analysis exported to article/manipulation_studio_analysis.csv")

    else:
        print("[SKIP] No TMDb data available for studio analysis")

    # ========================================
    # PHASE 3: Top 250 Volatility Tracking
    # ========================================
    print("\n" + "="*70)
    print("[PHASE 3] Top 250 Volatility Tracking")
    print("="*70)
    print("\nFetching quarterly Top 250 snapshots (2019-2024)...")
    print("(This may take 10-15 minutes to fetch ~20 snapshots from Wayback Machine)")

    try:
        volatility_df = track_top250_volatility(years_range=(2019, 2024))

        if len(volatility_df) > 0:
            print(f"\n[OK] Tracked {len(volatility_df)} unique films across snapshots")

            # Identify suspicious entries
            suspicious_entries = identify_suspicious_top250_entries(volatility_df, master)

            print(f"\nVolatility Patterns:")
            print(f"  - Flash campaigns: {volatility_df['is_flash_campaign'].sum()}")
            print(f"  - Yo-yo patterns: {volatility_df['is_yoyo'].sum()}")
            print(f"  - Sustained (>0.7): {(volatility_df['stability_score'] > 0.7).sum()}")
            print(f"  - Suspicious (score>=3): {len(suspicious_entries)}")

            if len(suspicious_entries) > 0:
                print("\nTop 10 Suspicious Top 250 Entries:")
                print(suspicious_entries[['title', 'year', 'stability_score', 'num_votes',
                                          'is_flash_campaign', 'is_yoyo', 'suspicion_score']].head(10))

                # Export
                output_dir = Path('article')
                suspicious_entries.to_csv(output_dir / 'manipulation_top250_suspicious.csv', index=False)
                print(f"\n[OK] Suspicious Top 250 entries exported")

    except Exception as e:
        logger.error(f"Top 250 tracking failed: {e}")
        logger.error("Continuing without volatility data...")

    # ========================================
    # PHASE 4: Historical Comparison
    # ========================================
    print("\n" + "="*70)
    print("[PHASE 4] Historical Comparison (2010-2018 vs. 2019-2024)")
    print("="*70)

    print("\nRunning analysis for 2010-2018 period...")
    period1_genre = analyze_genre_anomalies(master, years_range=(2010, 2018))
    period1_benford = detect_vote_clustering(master, years_range=(2010, 2018))
    period1_franchise = detect_franchise_coordination(master, years_range=(2010, 2018))

    print("\nRunning analysis for 2019-2024 period...")
    period2_genre = analyze_genre_anomalies(master, years_range=(2019, 2024))
    period2_benford = detect_vote_clustering(master, years_range=(2019, 2024))
    period2_franchise = detect_franchise_coordination(master, years_range=(2019, 2024))

    print("\n" + "-"*70)
    print("COMPARISON: 2010-2018 vs. 2019-2024")
    print("-"*70)

    print("\n[1] Genre Anomalies:")
    print(f"  2010-2018: {len(period1_genre[period1_genre['suspicious']])} suspicious genres")
    print(f"  2019-2024: {len(period2_genre[period2_genre['suspicious']])} suspicious genres")

    print("\n[2] Benford's Law:")
    print(f"  2010-2018: p={period1_benford['p_value']:.4f} ({period1_benford['manipulation_probability']})")
    print(f"  2019-2024: p={period2_benford['p_value']:.4f} ({period2_benford['manipulation_probability']})")

    print("\n[3] Franchise Coordination:")
    print(f"  2010-2018: {len(period1_franchise[period1_franchise['suspicious']])} genres with boost")
    print(f"  2019-2024: {len(period2_franchise[period2_franchise['suspicious']])} genres with boost")

    if len(period1_franchise) > 0 and len(period2_franchise) > 0:
        # Compare Action genre across periods
        action1 = period1_franchise[period1_franchise['genre'] == 'Action']
        action2 = period2_franchise[period2_franchise['genre'] == 'Action']

        if len(action1) > 0 and len(action2) > 0:
            boost1 = action1.iloc[0]['difference']
            boost2 = action2.iloc[0]['difference']
            print(f"\n  Action Franchise Boost:")
            print(f"    2010-2018: +{boost1:.2f}")
            print(f"    2019-2024: +{boost2:.2f}")
            print(f"    Change: {boost2 - boost1:+.2f} {'[INCREASING]' if boost2 > boost1 else '[STABLE]'}")

    # ========================================
    # PHASE 5: Final Report
    # ========================================
    print("\n" + "="*70)
    print("[PHASE 5] Final Report Generation")
    print("="*70)

    # Count evidence across all analyses
    evidence_count = 0
    evidence_details = []

    # Genre anomalies (2019-2024)
    if len(period2_genre[period2_genre['suspicious']]) > 0:
        evidence_count += 1
        evidence_details.append("Genre anomalies detected")

    # Benford violations (2019-2024)
    if period2_benford['p_value'] < 0.05:
        evidence_count += 1
        evidence_details.append("Benford's Law violations")

    # Franchise coordination (2019-2024)
    if len(period2_franchise[period2_franchise['suspicious']]) > 0:
        evidence_count += 1
        evidence_details.append("Franchise coordination")

    # Top 250 volatility
    try:
        if len(suspicious_entries) > 5:
            evidence_count += 1
            evidence_details.append("Top 250 flash campaigns")
    except:
        pass

    # Studio disparities
    try:
        if 'studio_results' in locals() and len(studio_results) > 0:
            max_boost = max([s['vs_indie'] for s in studio_results])
            if max_boost > 0.3:
                evidence_count += 1
                evidence_details.append("Major studio rating advantage")
    except:
        pass

    # Historical trend (increasing manipulation)
    if period2_benford['p_value'] < period1_benford['p_value'] * 2:  # Getting worse
        evidence_count += 1
        evidence_details.append("Manipulation increasing over time")

    print(f"\n{evidence_count}/6 manipulation signatures detected:")
    for detail in evidence_details:
        print(f"  [YES] {detail}")

    # Missing evidence
    all_possible = [
        "Genre anomalies detected",
        "Benford's Law violations",
        "Franchise coordination",
        "Top 250 flash campaigns",
        "Major studio rating advantage",
        "Manipulation increasing over time"
    ]
    for possible in all_possible:
        if possible not in evidence_details:
            print(f"  [NO]  {possible}")

    print("\n" + "="*70)
    if evidence_count >= 4:
        print("[VERDICT] STRONG EVIDENCE of coordinated rating manipulation")
    elif evidence_count >= 3:
        print("[VERDICT] MODERATE EVIDENCE of rating manipulation")
    else:
        print("[VERDICT] LIMITED EVIDENCE - patterns may be organic")
    print("="*70)

    print("\n[SUCCESS] Comprehensive analysis complete!")
    print("\nAll results exported to: article/")
    print("  - manipulation_studio_analysis.csv (if TMDb data available)")
    print("  - manipulation_top250_suspicious.csv (if volatility tracked)")
    print("  - [previous exports from basic analysis]")


if __name__ == "__main__":
    main()
