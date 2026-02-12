"""
Quick script to run full manipulation investigation and generate summary report.
"""

import sys
sys.path.append('src')

from pathlib import Path
import pandas as pd

from data_loader import load_title_basics, load_title_ratings, merge_master_dataset, logger
from manipulation_detection import (
    analyze_genre_anomalies,
    detect_vote_clustering,
    detect_franchise_coordination,
    analyze_documentary_manipulation,
    identify_chinese_films_proxy
)
from viz import (
    plot_genre_anomalies,
    plot_benford_violations,
    plot_franchise_coordination,
    plot_documentary_manipulation,
    plot_manipulation_summary
)


def main():
    print("="*70)
    print("MANIPULATION INVESTIGATION: 2019-2024 RATING INFLATION")
    print("="*70)

    # Load data
    print("\n[1/6] Loading datasets...")
    basics = load_title_basics()
    ratings = load_title_ratings()
    master = merge_master_dataset(basics, ratings, min_votes=1000)

    print(f"[OK] Loaded {len(master):,} movies (>=1,000 votes)")
    print(f"[OK] Recent period (2019-2024): {len(master[master['year'].between(2019, 2024)]):,} movies")

    # Analysis 1: Genre Anomalies
    print("\n[2/6] Running genre anomaly analysis...")
    genre_results = analyze_genre_anomalies(master, years_range=(2019, 2024))
    plot_genre_anomalies(genre_results, years_range=(2019, 2024))
    print(f"[OK] Found {len(genre_results[genre_results['suspicious']])} suspicious genres")

    # Analysis 2: Benford's Law
    print("\n[3/6] Running Benford's Law test...")
    benford_results = detect_vote_clustering(master, years_range=(2019, 2024))
    plot_benford_violations(benford_results)
    print(f"[OK] Benford test: p={benford_results['p_value']:.4f}, {benford_results['manipulation_probability']} risk")

    # Analysis 3: Franchise Coordination
    print("\n[4/6] Detecting franchise coordination...")
    franchise_results = detect_franchise_coordination(master, years_range=(2019, 2024))
    plot_franchise_coordination(franchise_results)
    print(f"[OK] Found {len(franchise_results[franchise_results['suspicious']])} genres with suspicious franchise boost")

    # Analysis 4: Documentary Manipulation
    print("\n[5/6] Analyzing documentary genre...")
    doc_results = analyze_documentary_manipulation(master, years_range=(2019, 2024))
    plot_documentary_manipulation(doc_results)
    print(f"[OK] Documentary analysis: {doc_results['suspicious_count']}/{doc_results['total_recent_docs']} suspicious")

    # Analysis 5: Chinese Films
    print("\n[6/6] Identifying Chinese film proxies...")
    chinese_films = identify_chinese_films_proxy(master, years_range=(2019, 2024))
    print(f"[OK] Identified {len(chinese_films)} likely Chinese-influenced films")

    # Generate summary figure
    print("\n[SUMMARY] Generating 4-panel summary figure...")
    plot_manipulation_summary(genre_results, benford_results, franchise_results, doc_results)
    print("[OK] Summary figure saved")

    # Print key findings
    print("\n" + "="*70)
    print("KEY FINDINGS:")
    print("="*70)

    print("\n[1] GENRE ANOMALIES:")
    suspicious_genres = genre_results[genre_results['suspicious']]
    if len(suspicious_genres) > 0:
        for _, row in suspicious_genres.iterrows():
            print(f"   - {row['genre']}: {row['recent_mean']:.2f} (historical: {row['historical_mean']:.2f}, " +
                  f"d={row['cohens_d']:.2f}, p={row['p_value']:.4f})")
    else:
        print("   - None detected")

    print("\n[2] BENFORD'S LAW:")
    print(f"   - Chi-square: {benford_results['chi2_statistic']:.2f}")
    print(f"   - P-value: {benford_results['p_value']:.6f}")
    print(f"   - Risk: {benford_results['manipulation_probability']}")
    print(f"   - Verdict: {benford_results['verdict']}")

    print("\n[3] FRANCHISE COORDINATION:")
    suspicious_franchise = franchise_results[franchise_results['suspicious']]
    if len(suspicious_franchise) > 0:
        for _, row in suspicious_franchise.iterrows():
            print(f"   - {row['genre']}: Franchise +{row['difference']:.2f} vs. standalone " +
                  f"(p={row['p_value']:.6f})")
    else:
        print("   - None detected")

    print("\n[4] DOCUMENTARY MANIPULATION:")
    print(f"   - Recent mean: {doc_results['recent_mean_rating']:.2f} (historical: {doc_results['historical_mean_rating']:.2f})")
    print(f"   - Vote efficiency boost: +{doc_results['efficiency_boost']:.2f} (p={doc_results['p_value']:.4f})")
    print(f"   - Suspicious docs: {doc_results['suspicious_count']}/{doc_results['total_recent_docs']}")

    print("\n[5] CHINESE FILM PROXIES:")
    if len(chinese_films) > 0:
        print(f"   - Identified {len(chinese_films)} likely Chinese films")
        print(f"   - Mean rating boost: +{chinese_films['rating_boost'].mean():.2f}")
        print(f"   - Top film: {chinese_films.iloc[0]['title']} ({chinese_films.iloc[0]['year']}) " +
              f"rating {chinese_films.iloc[0]['imdb_rating']:.1f}, boost +{chinese_films.iloc[0]['rating_boost']:.2f}")
    else:
        print("   - None detected with current thresholds")

    # Export results
    print("\n" + "="*70)
    print("EXPORTING RESULTS:")
    print("="*70)

    output_dir = Path('article')
    output_dir.mkdir(exist_ok=True)

    genre_results[genre_results['suspicious']].to_csv(
        output_dir / 'manipulation_suspicious_genres.csv', index=False
    )
    franchise_results.to_csv(
        output_dir / 'manipulation_franchise_analysis.csv', index=False
    )
    doc_results['suspicious_docs'].to_csv(
        output_dir / 'manipulation_suspicious_docs.csv', index=False
    )
    if len(chinese_films) > 0:
        chinese_films.to_csv(
            output_dir / 'manipulation_chinese_films.csv', index=False
        )

    print(f"[OK] All results exported to {output_dir}/")

    print("\n" + "="*70)
    print("[SUCCESS] ANALYSIS COMPLETE!")
    print("="*70)
    print("\nFigures saved to: figures/")
    print("  - fig7_genre_anomalies.png")
    print("  - fig8_benford_violations.png")
    print("  - fig9_franchise_coordination.png")
    print("  - fig10_documentary_manipulation.png")
    print("  - fig11_manipulation_summary.png")
    print("\nData exported to: article/")
    print("  - manipulation_suspicious_genres.csv")
    print("  - manipulation_franchise_analysis.csv")
    print("  - manipulation_suspicious_docs.csv")
    if len(chinese_films) > 0:
        print("  - manipulation_chinese_films.csv")

    # Generate conclusion
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)

    evidence_count = 0
    if len(suspicious_genres) > 0:
        evidence_count += 1
    if benford_results['p_value'] < 0.05:
        evidence_count += 1
    if len(suspicious_franchise) > 0:
        evidence_count += 1
    if doc_results['p_value'] < 0.05:
        evidence_count += 1
    if len(chinese_films) > 10:
        evidence_count += 1

    print(f"\n{evidence_count}/5 manipulation signatures detected:")
    print(f"  {'[YES]' if len(suspicious_genres) > 0 else '[NO] '} Genre anomalies")
    print(f"  {'[YES]' if benford_results['p_value'] < 0.05 else '[NO] '} Benford violations")
    print(f"  {'[YES]' if len(suspicious_franchise) > 0 else '[NO] '} Franchise coordination")
    print(f"  {'[YES]' if doc_results['p_value'] < 0.05 else '[NO] '} Documentary inflation")
    print(f"  {'[YES]' if len(chinese_films) > 10 else '[NO] '} Chinese film proxies")

    if evidence_count >= 3:
        print("\n[ALERT] STRONG EVIDENCE of coordinated rating manipulation in 2019-2024!")
    elif evidence_count >= 2:
        print("\n[WARNING] MODERATE EVIDENCE of rating manipulation - worth investigating further.")
    else:
        print("\n[INFO] Limited evidence of manipulation - recent inflation may be organic.")


if __name__ == "__main__":
    main()
