from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random

RISK_KEYWORDS = ["fraud", "scam", "illegal", "laundering", "bribery", "corruption", "embezzlement", "stolen", "hack", "leak"]

def analyze_social_content(name: str, username: str) -> dict:
    """
    Analyzes simulated social media posts for sentiment, risk keywords, and toxicity.
    """
    if not name and not username:
        return {"sentiment": "Neutral", "score": 0.0, "risk": "Low"}
    
    analyzer = SentimentIntensityAnalyzer()
    
    # Mocking some posts based on whether the name sounds suspicious or just normal.
    # In a real app, we'd fetch tweets, comments, etc.
    sample_posts = [
        f"Just started a new project with {name or username}. Great stuff!",
        "Not sure about the recent transactions, looks a bit shady.",
        "Had a wonderful time at the conference today.",
        "They are accused of fraud and money laundering in the latest leak."
    ]
    
    # We will pick a random subset to simulate different results per user
    random.seed(hash(name or username))
    selected_posts = random.sample(sample_posts, k=random.randint(1, 4))
    
    total_compound = 0
    found_keywords = []
    
    for post in selected_posts:
        # Vader Sentiment
        vs = analyzer.polarity_scores(post)
        total_compound += vs['compound']
        
        # Risk Keywords
        post_lower = post.lower()
        for kw in RISK_KEYWORDS:
            if kw in post_lower and kw not in found_keywords:
                found_keywords.append(kw)
    
    avg_compound = total_compound / len(selected_posts) if selected_posts else 0
    
    # Calculate Toxicity (mocked logic based on negative sentiment and keywords)
    toxicity_score = min(1.0, (len(found_keywords) * 0.2) + (0.5 if avg_compound < -0.3 else 0.0))
    
    sentiment_label = "Positive"
    if avg_compound < -0.05:
        sentiment_label = "Negative"
    elif -0.05 <= avg_compound <= 0.05:
        sentiment_label = "Neutral"
        
    risk_label = "Low"
    if toxicity_score >= 0.7 or len(found_keywords) >= 2:
        risk_label = "High"
    elif toxicity_score >= 0.4 or len(found_keywords) == 1:
        risk_label = "Medium"
        
    return {
        "sentiment": sentiment_label,
        "score": round(avg_compound, 2),
        "toxicity": round(toxicity_score, 2),
        "risk": risk_label,
        "keywords": found_keywords
    }
