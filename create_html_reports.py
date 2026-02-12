import base64
from pathlib import Path

def embed_image(img_path):
    """Convert image to base64 data URI"""
    with open(img_path, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{img_data}"

# Article 1: Rating Inflation
print("Creating Article 1 with embedded images...")
article1_images = [
    ('figures/fig1_rating_inflation_timeline.png', 'Figure 1: Rating Inflation Timeline - The 2008 correction brought ratings down from the 2000-2010 inflation era'),
    ('figures/fig2_era_comparison_boxplot.png', 'Figure 2: Era Comparison - Distribution of ratings before and after 2008'),
    ('figures/fig3_cutoff_statistical_evidence.png', 'Figure 3: Statistical Evidence - 2008 shows the strongest regime change'),
    ('figures/fig4_high_rated_explosion.png', 'Figure 4: High-Rated Movie Explosion - 3x increase in 8.0+ films despite lower scrutiny'),
    ('figures/fig5_rating_vs_votes_scatter.png', 'Figure 5: Rating vs. Scrutiny - Recent high-rated films have far fewer votes')
]

html1_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Great Movie Rating Inflation: When 2008 Marked the Correction</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .article-container {
            background-color: white;
            padding: 60px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            font-size: 2.5em;
            line-height: 1.2;
            margin-bottom: 0.3em;
            color: #1a1a1a;
        }
        h2 {
            font-size: 1.8em;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #2c3e50;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 10px;
        }
        h3 {
            font-size: 1.3em;
            margin-top: 1.2em;
            color: #34495e;
        }
        .subtitle {
            font-size: 1.2em;
            color: #555;
            font-style: italic;
            margin-bottom: 1em;
        }
        .attribution {
            font-size: 0.9em;
            color: #777;
            font-style: italic;
            border-left: 3px solid #3498db;
            padding-left: 15px;
            margin: 20px 0;
        }
        .figure {
            margin: 30px 0;
            text-align: center;
        }
        .figure img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .figure-caption {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
            margin-top: 10px;
            text-align: center;
        }
        strong {
            color: #e74c3c;
            font-weight: 600;
        }
        p {
            margin-bottom: 1.2em;
        }
    </style>
</head>
<body>
    <div class="article-container">
        <h1>The Great Movie Rating Inflation: When 2008 Marked the Correction</h1>
        <p class="subtitle">A statistical analysis of IMDb ratings reveals a surprising truth about when movie ratings became inflated</p>

        <div class="attribution">
            <em>This article's content and analytical perspective were crafted by Claude Sonnet 4.5. The project genesis and direction came from Glenn Highcove. For more information and feedback, connect with Glenn on <a href="https://www.linkedin.com/in/glennhighcove/">LinkedIn</a>.</em>
        </div>

        <hr>

        <p><strong>Key Finding:</strong> Movie ratings didn't start inflating in 2008—they <em>corrected</em> in 2008. The real inflation happened between 2000-2010, when ratings jumped from 6.03 to 6.22. Since 2008, ratings have stabilized at a lower, more sustainable level.</p>
'''

# Add images
for img_path, caption in article1_images:
    if Path(img_path).exists():
        img_data = embed_image(img_path)
        html1_template += f'''
        <div class="figure">
            <img src="{img_data}" alt="{caption}">
            <p class="figure-caption">{caption}</p>
        </div>
'''
        print(f"  Embedded: {img_path}")
    else:
        print(f"  MISSING: {img_path}")

html1_template += '''
        <p><em>Analysis based on 737,654 films from IMDb dataset. See full article for methodology and statistical evidence.</em></p>
    </div>
</body>
</html>'''

with open('article/article1_rating_inflation_with_viz.html', 'w', encoding='utf-8') as f:
    f.write(html1_template)
print("[OK] Created article/article1_rating_inflation_with_viz.html\n")

# Article 2: Manipulation Investigation
print("Creating Article 2 with embedded images...")
article2_images = [
    ('visualizations/manipulation_genre_anomalies.png', 'Genre Anomalies: Documentary genre shows 7.21 mean rating, 1.40 points above baseline'),
    ('visualizations/manipulation_franchise_coordination.png', 'Franchise Coordination: MCU/DC/Star Wars films rate +0.93 points higher than standalone Action films'),
    ('visualizations/manipulation_studio_advantage.png', 'Studio Advantage: Disney shows +0.32 rating boost, Netflix +0.43'),
    ('visualizations/manipulation_benford_violations.png', "Benford's Law Test: Vote count distribution shows increasing manipulation signature"),
    ('visualizations/manipulation_documentary.png', 'Documentary Manipulation: Vote efficiency 27x higher than expected')
]

html2_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Ratings Manipulation Investigation: Evidence of Coordinated Voting Patterns</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .article-container {
            background-color: white;
            padding: 60px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            font-size: 2.5em;
            line-height: 1.2;
            margin-bottom: 0.3em;
            color: #1a1a1a;
        }
        h2 {
            font-size: 1.8em;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #2c3e50;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 10px;
        }
        .subtitle {
            font-size: 1.2em;
            color: #555;
            font-style: italic;
            margin-bottom: 1em;
        }
        .attribution {
            font-size: 0.9em;
            color: #777;
            font-style: italic;
            border-left: 3px solid #3498db;
            padding-left: 15px;
            margin: 20px 0;
        }
        .figure {
            margin: 30px 0;
            text-align: center;
        }
        .figure img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .figure-caption {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
            margin-top: 10px;
            text-align: center;
        }
        .evidence-box {
            background-color: #fff3cd;
            border-left: 4px solid #e74c3c;
            padding: 20px;
            margin: 20px 0;
        }
        strong {
            color: #e74c3c;
            font-weight: 600;
        }
        p {
            margin-bottom: 1.2em;
        }
    </style>
</head>
<body>
    <div class="article-container">
        <h1>The Ratings Manipulation Investigation</h1>
        <p class="subtitle">Statistical evidence reveals coordinated voting patterns across franchises, studios, and genres</p>

        <div class="attribution">
            <em>This article's content and analytical perspective were crafted by Claude Sonnet 4.5. The project genesis and direction came from Glenn Highcove. For more information and feedback, connect with Glenn on <a href="https://www.linkedin.com/in/glennhighcove/">LinkedIn</a>.</em>
        </div>

        <hr>

        <div class="evidence-box">
            <p><strong>Evidence Summary:</strong> Analysis of 9,145 films (2019-2024) detected 4 of 6 manipulation signatures:</p>
            <ul>
                <li>✓ Documentary genre anomaly (7.21 vs baseline)</li>
                <li>✓ Franchise coordination (Action +0.93, Adventure +0.54)</li>
                <li>✓ Studio advantage (Disney +0.32, Netflix +0.43)</li>
                <li>✓ Benford's Law violations worsening over time</li>
            </ul>
            <p><strong>Key Discovery:</strong> Manipulation is <em>stable</em> since 2010, not escalating as initially hypothesized.</p>
        </div>

        <h2>Visual Evidence</h2>
'''

# Add images
for img_path, caption in article2_images:
    if Path(img_path).exists():
        img_data = embed_image(img_path)
        html2_template += f'''
        <div class="figure">
            <img src="{img_data}" alt="{caption}">
            <p class="figure-caption">{caption}</p>
        </div>
'''
        print(f"  Embedded: {img_path}")
    else:
        print(f"  MISSING: {img_path}")

html2_template += '''
        <p><em>Analysis based on TMDb API integration (9,145 films fetched, 97% success rate), statistical hypothesis testing, and Benford's Law violations. See full investigation report for complete methodology.</em></p>
    </div>
</body>
</html>'''

with open('article/article2_manipulation_with_viz.html', 'w', encoding='utf-8') as f:
    f.write(html2_template)
print("[OK] Created article/article2_manipulation_with_viz.html\n")

print("\n[SUCCESS] Both reports created with embedded visualizations!")
print("Open these files in your browser:")
print("  - article/article1_rating_inflation_with_viz.html")
print("  - article/article2_manipulation_with_viz.html")
