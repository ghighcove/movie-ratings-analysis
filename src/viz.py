"""
Visualization library for rating analysis.

Creates publication-quality figures showing rating inflation trends,
cutoff evidence, and high-rated movie explosion.
"""

import logging
from pathlib import Path
from typing import Optional, List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from data_loader import PROJECT_ROOT, logger

# Output directory for figures
FIGURES_DIR = PROJECT_ROOT / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')


def save_figure(fig, filename: str, dpi: int = 300):
    """Save figure in multiple formats."""
    # PNG for web
    png_path = FIGURES_DIR / f"{filename}.png"
    fig.savefig(png_path, dpi=dpi, bbox_inches='tight')
    logger.info(f"Saved: {png_path}")

    # PDF for publication
    pdf_path = FIGURES_DIR / f"{filename}.pdf"
    fig.savefig(pdf_path, bbox_inches='tight')
    logger.info(f"Saved: {pdf_path}")


def plot_rating_inflation_timeline(yearly_stats: pd.DataFrame, cutoff_years: List[int]):
    """
    Time series showing rating inflation over time with cutoff markers.

    Args:
        yearly_stats: DataFrame with year, rating_mean, rating_std columns
        cutoff_years: List of candidate cutoff years to mark
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Filter to 1950+
    data = yearly_stats[yearly_stats['year'] >= 1950].copy()

    # Top panel: Mean rating over time
    ax1.plot(data['year'], data['rating_mean'], linewidth=2.5, color='darkblue', label='Mean Rating')

    # Add trend line (LOWESS smoothing)
    from scipy.signal import savgol_filter
    window = min(15, len(data) // 3)
    if window % 2 == 0:
        window += 1
    if window >= 3:
        smoothed = savgol_filter(data['rating_mean'], window, 2)
        ax1.plot(data['year'], smoothed, linewidth=3, color='red',
                linestyle='--', alpha=0.7, label='Trend (Smoothed)')

    # Shade inflation period (2000-2010)
    ax1.axvspan(2000, 2010, alpha=0.2, color='orange', label='Inflation Era')

    # Mark cutoff years
    for year in cutoff_years:
        ax1.axvline(year, color='red', linestyle=':', alpha=0.6, linewidth=1.5)

    # Highlight 2008 (strongest evidence)
    ax1.axvline(2008, color='red', linestyle='-', linewidth=2.5, label='2008 Cutoff', alpha=0.8)

    ax1.set_ylabel('Mean IMDb Rating', fontsize=13, fontweight='bold')
    ax1.set_title('Movie Rating Inflation Timeline (1950-2024)\nInflation ~2000, Correction ~2008',
                  fontsize=15, fontweight='bold', pad=20)
    ax1.legend(loc='upper left', fontsize=11)
    ax1.grid(alpha=0.3)
    ax1.set_ylim(5.8, 6.5)

    # Bottom panel: Number of movies per year
    ax2.bar(data['year'], data['movie_count'], color='steelblue', alpha=0.6, edgecolor='black', linewidth=0.5)
    ax2.axvspan(2000, 2010, alpha=0.2, color='orange')
    ax2.axvline(2008, color='red', linestyle='-', linewidth=2.5, alpha=0.8)

    for year in cutoff_years:
        if year != 2008:
            ax2.axvline(year, color='red', linestyle=':', alpha=0.6, linewidth=1.5)

    ax2.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Movie Count', fontsize=13, fontweight='bold')
    ax2.set_title('Number of Movies Released (with ≥1,000 votes)', fontsize=13, fontweight='bold')
    ax2.grid(alpha=0.3, axis='y')

    plt.tight_layout()
    save_figure(fig, 'fig1_rating_inflation_timeline')
    plt.close()


def plot_era_comparison(master: pd.DataFrame):
    """
    Box plots comparing rating distributions across eras.

    Args:
        master: Master dataset with 'era' and 'imdb_rating' columns
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    # Filter for movies with sufficient votes
    data = master[
        (master['num_votes'] >= 1000) &
        (master['imdb_rating'].notna())
    ].copy()

    # Box plot by era
    eras = data['era'].cat.categories
    positions = range(len(eras))

    bp = ax.boxplot(
        [data[data['era'] == era]['imdb_rating'] for era in eras],
        positions=positions,
        patch_artist=True,
        widths=0.6,
        showmeans=True,
        meanprops=dict(marker='D', markerfacecolor='red', markersize=8)
    )

    # Color boxes - highlight inflation era
    colors = ['lightblue', 'lightblue', 'lightblue', 'orange', 'lightcoral', 'lightcoral']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xticks(positions)
    ax.set_xticklabels(eras, fontsize=11, rotation=15, ha='right')
    ax.set_ylabel('IMDb Rating', fontsize=13, fontweight='bold')
    ax.set_title('Rating Distribution by Era\n2000-2009 Shows Clear Inflation',
                 fontsize=15, fontweight='bold', pad=20)
    ax.grid(alpha=0.3, axis='y')

    # Add mean values as text
    for i, era in enumerate(eras):
        mean_val = data[data['era'] == era]['imdb_rating'].mean()
        ax.text(i, mean_val + 0.15, f'{mean_val:.2f}',
                ha='center', fontsize=10, fontweight='bold', color='darkred')

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='lightblue', alpha=0.7, label='Pre-Inflation'),
        Patch(facecolor='orange', alpha=0.7, label='Inflation Era (2000-2009)'),
        Patch(facecolor='lightcoral', alpha=0.7, label='Post-Correction')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11)

    plt.tight_layout()
    save_figure(fig, 'fig2_era_comparison_boxplot')
    plt.close()


def plot_cutoff_evidence(cutoff_results: pd.DataFrame):
    """
    Bar chart showing statistical evidence for each cutoff year.

    Args:
        cutoff_results: DataFrame with cutoff test results
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Sort by combined rank
    data = cutoff_results.sort_values('combined_rank').copy()

    # Left panel: Effect size (Cohen's d)
    colors = ['darkred' if year == 2008 else 'steelblue' for year in data['cutoff_year']]
    bars1 = ax1.barh(data['cutoff_year'].astype(str), data['cohens_d'].abs(),
                     color=colors, alpha=0.7, edgecolor='black')

    ax1.set_xlabel("Effect Size (|Cohen's d|)", fontsize=12, fontweight='bold')
    ax1.set_ylabel('Cutoff Year', fontsize=12, fontweight='bold')
    ax1.set_title('Effect Size: Rating Drop After Cutoff', fontsize=13, fontweight='bold')
    ax1.grid(alpha=0.3, axis='x')

    # Add values on bars
    for i, (val, year) in enumerate(zip(data['cohens_d'].abs(), data['cutoff_year'])):
        label = f'{val:.3f}' + (' ★' if year == 2008 else '')
        ax1.text(val + 0.003, i, label, va='center', fontsize=10, fontweight='bold')

    # Right panel: -log10(p-value) for significance
    data['log_pvalue'] = -np.log10(data['t_pvalue'])
    bars2 = ax2.barh(data['cutoff_year'].astype(str), data['log_pvalue'],
                     color=colors, alpha=0.7, edgecolor='black')

    ax2.set_xlabel('-log10(p-value)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Cutoff Year', fontsize=12, fontweight='bold')
    ax2.set_title('Statistical Significance (t-test)', fontsize=13, fontweight='bold')
    ax2.grid(alpha=0.3, axis='x')

    # Add significance threshold line
    ax2.axvline(-np.log10(0.01), color='green', linestyle='--', linewidth=2,
                label='p=0.01 threshold', alpha=0.7)
    ax2.legend(fontsize=10)

    # Add values on bars
    for i, (val, year) in enumerate(zip(data['log_pvalue'], data['cutoff_year'])):
        label = f'{val:.0f}' + (' ★' if year == 2008 else '')
        ax2.text(val + 1, i, label, va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    save_figure(fig, 'fig3_cutoff_statistical_evidence')
    plt.close()


def plot_high_rated_explosion(decade_counts: pd.DataFrame):
    """
    Bar chart showing explosion of high-rated movies over time.

    Args:
        decade_counts: DataFrame with decade, count, votes_median columns
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Top panel: Count of high-rated movies by decade
    colors = ['steelblue' if d < 2000 else 'orange' if d < 2010 else 'lightcoral'
              for d in decade_counts['decade']]

    bars1 = ax1.bar(decade_counts['decade'], decade_counts['count'],
                    color=colors, alpha=0.7, edgecolor='black', width=8)

    ax1.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Count of Movies Rated ≥8.0', fontsize=12, fontweight='bold')
    ax1.set_title('Explosion of High-Rated Movies\n(≥8.0 rating, ≥10k votes)',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.grid(alpha=0.3, axis='y')

    # Add values on bars
    for bar, val in zip(bars1, decade_counts['count']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, height + 2, f'{int(val)}',
                ha='center', fontsize=10, fontweight='bold')

    # Add trend line
    z = np.polyfit(decade_counts['decade'], decade_counts['count'], 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(decade_counts['decade'].min(), decade_counts['decade'].max(), 100)
    ax1.plot(x_smooth, p(x_smooth), 'r--', linewidth=2.5, alpha=0.7, label='Trend')
    ax1.legend(fontsize=11)

    # Bottom panel: Median votes (quality scrutiny indicator)
    bars2 = ax2.bar(decade_counts['decade'], decade_counts['votes_median'] / 1000,
                    color=colors, alpha=0.7, edgecolor='black', width=8)

    ax2.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Median Votes (thousands)', fontsize=12, fontweight='bold')
    ax2.set_title('Declining Scrutiny: Fewer Votes for High-Rated Movies',
                  fontsize=14, fontweight='bold', pad=15)
    ax2.grid(alpha=0.3, axis='y')

    # Add values on bars
    for bar, val in zip(bars2, decade_counts['votes_median']):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + 10, f'{int(val/1000)}k',
                ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    save_figure(fig, 'fig4_high_rated_explosion')
    plt.close()


def plot_rating_vs_votes_scatter(master: pd.DataFrame):
    """
    Scatter plot showing relationship between rating and vote count by era.

    Args:
        master: Master dataset
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Filter for movies with sufficient data
    data = master[
        (master['num_votes'] >= 1000) &
        (master['imdb_rating'].notna()) &
        (master['year'] >= 1980)
    ].copy()

    # Sample for visualization (too many points otherwise)
    if len(data) > 10000:
        data = data.sample(10000, random_state=42)

    # Color by era
    era_colors = {
        '1980-1999': 'blue',
        '2000-2009': 'orange',
        '2010-2019': 'red',
        '2020+': 'purple'
    }

    for era, color in era_colors.items():
        era_data = data[data['era'] == era]
        ax.scatter(np.log10(era_data['num_votes']), era_data['imdb_rating'],
                  alpha=0.4, s=20, c=color, label=era, edgecolors='none')

    # Add regression lines for each era
    for era, color in era_colors.items():
        era_data = data[data['era'] == era]
        if len(era_data) > 10:
            z = np.polyfit(np.log10(era_data['num_votes']), era_data['imdb_rating'], 1)
            p = np.poly1d(z)
            x_range = np.linspace(3, 6.5, 100)
            ax.plot(x_range, p(x_range), color=color, linewidth=2.5, alpha=0.8, linestyle='--')

    ax.set_xlabel('log10(Number of Votes)', fontsize=12, fontweight='bold')
    ax.set_ylabel('IMDb Rating', fontsize=12, fontweight='bold')
    ax.set_title('Rating vs. Scrutiny (Vote Count) by Era\nHigher Ratings with Less Scrutiny in Recent Years',
                 fontsize=14, fontweight='bold', pad=15)
    ax.legend(fontsize=11, loc='lower right')
    ax.grid(alpha=0.3)

    # Add reference line at rating 8.0
    ax.axhline(8.0, color='green', linestyle=':', linewidth=2, alpha=0.5, label='Rating 8.0 threshold')

    plt.tight_layout()
    save_figure(fig, 'fig5_rating_vs_votes_scatter')
    plt.close()


def plot_summary_heatmap(yearly_stats: pd.DataFrame):
    """
    Heatmap showing rating trends over decades and vote categories.

    Args:
        yearly_stats: DataFrame with year and rating_mean
    """
    # This is a simplified version - could be enhanced with more granular data
    fig, ax = plt.subplots(figsize=(10, 6))

    # Group by decade
    data = yearly_stats[yearly_stats['year'] >= 1950].copy()
    data['decade'] = (data['year'] // 10) * 10

    decade_summary = data.groupby('decade').agg({
        'rating_mean': 'mean',
        'rating_std': 'mean',
        'movie_count': 'sum'
    }).reset_index()

    # Create simple bar chart showing the pattern
    colors = ['steelblue' if d < 2000 else 'orange' if d < 2010 else 'lightcoral'
              for d in decade_summary['decade']]

    bars = ax.bar(decade_summary['decade'], decade_summary['rating_mean'],
                  color=colors, alpha=0.7, edgecolor='black', width=8)

    ax.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean IMDb Rating', fontsize=12, fontweight='bold')
    ax.set_title('Rating Inflation by Decade\nClear Jump in 2000s',
                 fontsize=14, fontweight='bold', pad=15)
    ax.grid(alpha=0.3, axis='y')

    # Add values on bars
    for bar, val in zip(bars, decade_summary['rating_mean']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.02, f'{val:.3f}',
                ha='center', fontsize=11, fontweight='bold')

    # Add horizontal line at baseline (1980-1999 average)
    baseline = decade_summary[decade_summary['decade'].between(1980, 1999)]['rating_mean'].mean()
    ax.axhline(baseline, color='blue', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Pre-2000 Baseline ({baseline:.3f})')
    ax.legend(fontsize=11)

    plt.tight_layout()
    save_figure(fig, 'fig6_decade_summary')
    plt.close()


def generate_all_figures(master: pd.DataFrame, yearly_stats: pd.DataFrame,
                        cutoff_results: pd.DataFrame, decade_counts: pd.DataFrame):
    """
    Generate all publication figures.

    Args:
        master: Master dataset
        yearly_stats: Yearly rating statistics
        cutoff_results: Cutoff hypothesis test results
        decade_counts: High-rated movies by decade
    """
    logger.info("Generating all figures...")
    logger.info(f"Output directory: {FIGURES_DIR}")

    cutoff_years = [2000, 2008, 2012, 2018, 2020]

    logger.info("\n[1/6] Generating rating inflation timeline...")
    plot_rating_inflation_timeline(yearly_stats, cutoff_years)

    logger.info("[2/6] Generating era comparison box plots...")
    plot_era_comparison(master)

    logger.info("[3/6] Generating cutoff evidence charts...")
    plot_cutoff_evidence(cutoff_results)

    logger.info("[4/6] Generating high-rated movie explosion...")
    plot_high_rated_explosion(decade_counts)

    logger.info("[5/6] Generating rating vs votes scatter...")
    plot_rating_vs_votes_scatter(master)

    logger.info("[6/6] Generating decade summary...")
    plot_summary_heatmap(yearly_stats)

    logger.info(f"\n✓ All figures saved to {FIGURES_DIR}/")
    logger.info("  - fig1_rating_inflation_timeline.png/pdf")
    logger.info("  - fig2_era_comparison_boxplot.png/pdf")
    logger.info("  - fig3_cutoff_statistical_evidence.png/pdf")
    logger.info("  - fig4_high_rated_explosion.png/pdf")
    logger.info("  - fig5_rating_vs_votes_scatter.png/pdf")
    logger.info("  - fig6_decade_summary.png/pdf")


if __name__ == "__main__":
    print("Visualization module loaded.")
    print(f"Figures will be saved to: {FIGURES_DIR}/")
