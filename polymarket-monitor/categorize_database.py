"""
Categorize existing markets in the database
Applies taxonomy to assign event types
"""
import sqlite3
import re
from datetime import datetime

# Market taxonomy (from event backtest system)
TAXONOMY = {
    'Crypto/BTC-UpDown': [r'\bbitcoin\s+up\s+or\s+down\b', r'\bbtc\s+higher\s+or\s+lower\b'],
    'Crypto/BTC-Price': [r'\bprice of bitcoin\b', r'\bbitcoin\b.*\$\d+', r'\bbtc\b.*\$\d+'],
    'Crypto/ETH': [r'\bethereum\b.*up\s+or\s+down\b', r'\beth\b.*higher'],
    'Crypto/Altcoins': [r'\bsolana\b', r'\bxrp\b', r'\bcardano\b', r'\bada\b', r'\bsol\b', r'\bavax\b', r'\bdoge\b'],
    'Weather/Temperature': [r'\btemperature\b', r'\bdegrees?\b', r'\bcelsius\b', r'\bfahrenheit\b', r'\bweather\b'],
    'Tech/Musk': [r'\bmusk\b.*tweet', r'\belon\s*musk\b.*post', r'\belon.*tweet'],
    'Tech/Companies': [r'\b(msft|microsoft|aapl|apple|nvda|nvidia|tsla|tesla)\b'],
    'Politics/Trump': [r'\btrump\b'],
    'Politics/Biden': [r'\bbiden\b'],
    'Politics/Election': [r'\belection\b', r'\bpresidential\b', r'\bnomination\b'],
    'Government/Fed': [r'\bfed\s+chair\b', r'\bfederal\s+reserve\b', r'\binterest\s+rate\b'],
    'Government/Shutdown': [r'\bshutdown\b'],
    'Sports/NFL': [r'\bnfl\b', r'\bsuper\s+bowl\b'],
    'Sports/NBA': [r'\bnba\b', r'\blebron\b'],
    'Sports/Soccer': [r'\bpremier\s+league\b', r'\bworld\s+cup\b', r'\bchampions\s+league\b'],
    'Economy/SPX': [r'\bs&p\s*500\b', r'\bspx\b', r'\bstock\s+market\b'],
    'Celebrities': [r'\boprah\b', r'\btaylor\s+swift\b', r'\bcelebrity\b']
}

def categorize_question(question: str) -> str:
    """Match question to category using regex"""
    question_lower = question.lower()
    
    for category, patterns in TAXONOMY.items():
        for pattern in patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return category
    
    return 'Unknown'

def main():
    print("[START] Categorizing database markets...")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Connect to database
    conn = sqlite3.connect('polymarket_data.db')
    cursor = conn.cursor()
    
    # Get all markets
    cursor.execute("SELECT market_id, question FROM markets")
    markets = cursor.fetchall()
    
    print(f"\n[INFO] Found {len(markets)} markets to categorize")
    
    # Categorize each
    category_counts = {}
    updated = 0
    
    for i, (market_id, question) in enumerate(markets, 1):
        category = categorize_question(question)
        
        # Update database
        cursor.execute(
            "UPDATE markets SET category = ? WHERE market_id = ?",
            (category, market_id)
        )
        
        # Track stats
        category_counts[category] = category_counts.get(category, 0) + 1
        updated += 1
        
        # Progress update every 200 markets
        if i % 200 == 0:
            print(f"[PROGRESS] {i}/{len(markets)} ({i/len(markets)*100:.0f}%)")
    
    # Commit changes
    conn.commit()
    
    print(f"\n[COMPLETE] Categorized {updated} markets")
    
    # Print category breakdown
    print("\n[CATEGORIES] Distribution:")
    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    
    for cat, count in sorted_cats[:15]:
        pct = count / len(markets) * 100
        print(f"  {cat:30} {count:5} ({pct:5.1f}%)")
    
    # Show high-signal categories (for our strategies)
    print("\n[HIGH-SIGNAL] Categories with proven strategies:")
    high_signal = ['Tech/Musk', 'Weather/Temperature', 'Crypto/Altcoins', 'Crypto/BTC-Price', 'Crypto/BTC-UpDown']
    
    for cat in high_signal:
        count = category_counts.get(cat, 0)
        if count > 0:
            print(f"  {cat}: {count} markets")
    
    conn.close()
    print(f"\n[DONE] Time: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
