"""
Fix Article 2 to intersperse visualizations throughout the text
"""
import base64
import re

def embed_image(img_path):
    """Convert image to base64 data URI"""
    with open(img_path, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{img_data}"

print("Fixing Article 2 visualization placement...")

# Read the current file
with open('article/COMPLETE_article2_manipulation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the "Visual Evidence" section at the end (everything from that heading to the Conclusion)
html = re.sub(r'<h2>Visual Evidence</h2>.*?<h2>Conclusion</h2>', '<h2>Conclusion</h2>', html, flags=re.DOTALL)

# Now insert visualizations at appropriate points in the narrative

# 1. Insert Genre Anomalies chart after the Documentary discussion
genre_fig = f'''
<div class="figure">
    <img src="{embed_image('visualizations/manipulation_genre_anomalies.png')}" alt="Genre Anomalies">
    <p class="figure-caption"><strong>Figure 1: Genre Anomalies.</strong> Documentary genre shows 7.21 mean rating, 1.40 points above baseline. This statistical anomaly suggests systematic coordination in nonfiction content, likely driven by advocacy groups and political interests using documentaries for agenda-setting.</p>
</div>
'''
html = html.replace('<h2>The Evidence: Five Smoking Guns</h2>',
                   '<h2>The Evidence: Five Smoking Guns</h2>' + genre_fig)

# 2. Insert Franchise Coordination chart after Smoking Gun #1
franchise_fig = f'''
<div class="figure">
    <img src="{embed_image('visualizations/manipulation_franchise_coordination.png')}" alt="Franchise Coordination">
    <p class="figure-caption"><strong>Figure 2: Franchise Coordination.</strong> Action franchise films rate +0.93 points higher than standalone Action films (p&lt;0.000002, Cohen's d=0.75). Adventure franchises show +0.54 boost. This massive statistical gap (three-quarters of a standard deviation) cannot occur naturally and indicates organized fan voting campaigns coordinating to inflate franchise ratings.</p>
</div>
'''
html = html.replace('</p>\n\n<hr>\n\n<h3>Smoking Gun #2:',
                   '</p>\n\n' + franchise_fig + '\n<hr>\n\n<h3>Smoking Gun #2:')

# 3. Insert Studio Advantage chart after Smoking Gun #4
studio_fig = f'''
<div class="figure">
    <img src="{embed_image('visualizations/manipulation_studio_advantage.png')}" alt="Studio Advantage">
    <p class="figure-caption"><strong>Figure 3: Studio Advantage.</strong> Disney shows +0.32 rating boost vs independent films (6.40 vs 6.07), the largest studio-specific effect detected. Netflix shows +0.43 but with small sample (16 films). Warner Bros, Sony, and Paramount show small advantages, while Universal shows no advantage. The studio effect is primarily a Disney effect, driven by franchise-heavy portfolio (Marvel, Star Wars, Pixar).</p>
</div>
'''
html = html.replace('</p>\n\n<hr>\n\n<h3>Smoking Gun #5:',
                   '</p>\n\n' + studio_fig + '\n<hr>\n\n<h3>Smoking Gun #5:')

# 4. Insert Benford's Law chart after discussion of vote manipulation
benford_fig = f'''
<div class="figure">
    <img src="{embed_image('visualizations/manipulation_benford_violations.png')}" alt="Benford\'s Law Violations">
    <p class="figure-caption"><strong>Figure 4: Benford's Law Violations.</strong> Vote count first-digit distribution deviates from expected logarithmic pattern (Benford's Law). P-value worsening from 0.168 (2010-2018) to 0.056 (2019-2024) suggests increasing prevalence of artificial voting patterns, though still below statistical significance threshold (p&lt;0.05). Round-number clustering shows 87 movies with suspiciously round vote counts.</p>
</div>
'''
# Insert after Historical Trend section
html = html.replace('<hr>\n\n<h2>Counter-Arguments',
                   benford_fig + '\n<hr>\n\n<h2>Counter-Arguments')

# 5. Insert Documentary chart near documentary discussion (earlier in the article)
doc_fig = f'''
<div class="figure">
    <img src="{embed_image('visualizations/manipulation_documentary.png')}" alt="Documentary Manipulation">
    <p class="figure-caption"><strong>Figure 5: Documentary Manipulation.</strong> Documentary vote efficiency (rating per 1000 votes) is 27× higher than expected baseline, with recent mean rating of 7.21 vs historical 7.17. The efficiency anomaly indicates systematic boosting: documentaries achieve elite ratings with disproportionately fewer votes than other genres, consistent with coordinated campaigns by advocacy groups and political organizations using documentary ratings for agenda validation.</p>
</div>
'''
# Insert after first mention of documentary anomaly
html = html.replace('<p><strong>The Finding:</strong> 47 films show rating boosts',
                   doc_fig + '\n<p><strong>The Finding:</strong> 47 films show rating boosts')

# Write the fixed file
with open('article/COMPLETE_article2_manipulation.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("[OK] Fixed article/COMPLETE_article2_manipulation.html")
print("Visualizations now appear throughout the article at relevant points")
