import sys
sys.path.insert(0, 'src')

from rating_analysis import load_master_with_metadata, compare_all_cutoffs

print("Loading master dataset...")
master = load_master_with_metadata()

print("\nComparing all candidate cutoff years...")
results = compare_all_cutoffs(master, min_votes=1000)

print("\n" + "="*80)
print("FINAL RESULTS - Ranked by Combined Statistical Evidence")
print("="*80)
print(results[['cutoff_year', 'mean_diff', 'cohens_d', 't_pvalue', 'ks_pvalue', 'combined_rank']].to_string(index=False))
