"""Generate all publication figures."""

import sys
sys.path.insert(0, 'src')

from rating_analysis import (
    load_master_with_metadata,
    analyze_rating_inflation,
    compare_all_cutoffs,
    analyze_high_rated_by_decade
)
from viz import generate_all_figures

print("="*80)
print("GENERATING PUBLICATION FIGURES")
print("="*80)

print("\n[1/4] Loading master dataset...")
master = load_master_with_metadata()

print("\n[2/4] Analyzing rating trends...")
yearly_stats = analyze_rating_inflation(master, min_votes=1000)

print("\n[3/4] Testing cutoff hypotheses...")
cutoff_results = compare_all_cutoffs(master, min_votes=1000)

print("\n[4/4] Analyzing high-rated movies by decade...")
decade_counts = analyze_high_rated_by_decade(master, threshold=8.0, min_votes=10000)

print("\n" + "="*80)
print("CREATING FIGURES")
print("="*80)

generate_all_figures(master, yearly_stats, cutoff_results, decade_counts)

print("\n" + "="*80)
print("SUCCESS - All figures generated!")
print("="*80)
