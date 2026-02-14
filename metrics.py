import json
from datetime import datetime, timezone

# Load active markets
with open('active-markets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

markets = data.get('markets', [])
# Sort by volumeNum descending
markets.sort(key=lambda m: m.get('volumeNum', 0), reverse=True)
top20 = markets[:20]

# Current date (UTC)
today = datetime.now(timezone.utc).date()

print("Top 20 Markets by Volume (Days to Resolution):")
print("Rank | ID | Question (truncated) | Volume ($) | Liquidity ($) | End Date | Days Left")
print("-" * 120)
for i, m in enumerate(top20, 1):
    q = m.get('question', '')[:50]
    vol = m.get('volumeNum', 0)
    liq = m.get('liquidityNum', 0)
    end_str = m.get('endDateIso')
    days_left = None
    if end_str:
        try:
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            days_left = (end_date - today).days
        except:
            days_left = '?'
    else:
        days_left = '?'
    print(f"{i:3} | {m.get('id')} | {q} | {vol:,.0f} | {liq:,.0f} | {end_str} | {days_left}")

# Total volume and liquidity across top 20
total_vol = sum(m.get('volumeNum', 0) for m in top20)
total_liq = sum(m.get('liquidityNum', 0) for m in top20)
avg_vol = total_vol / 20
avg_liq = total_liq / 20
print(f"\nTotal Volume Top20: ${total_vol:,.0f}")
print(f"Total Liquidity Top20: ${total_liq:,.0f}")
print(f"Average Volume: ${avg_vol:,.0f}")
print(f"Average Liquidity: ${avg_liq:,.0f}")

# Count days left categories
days_list = []
for m in top20:
    end_str = m.get('endDateIso')
    if end_str:
        try:
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            days = (end_date - today).days
            days_list.append(days)
        except:
            pass
if days_list:
    print(f"\nDays to resolution (min/avg/max): {min(days_list)} / {sum(days_list)/len(days_list):.1f} / {max(days_list)}")
    # Count near-term (<30 days)
    near = sum(1 for d in days_list if d <= 30)
    print(f"Markets resolving within 30 days: {near}")