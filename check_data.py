import json
with open('markets_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check volume stats
volumes = [m.get('volumeNum', 0) for m in data]
print('Total markets fetched:', len(data))
print('Max volumeNum:', max(volumes) if volumes else 0)

# Show top 10 markets by volume
data_sorted = sorted(data, key=lambda x: x.get('volumeNum', 0), reverse=True)
print('\nTop 10 by volume:')
for m in data_sorted[:10]:
    q = m.get('question', '')[:50]
    vol = m.get('volumeNum', 0)
    print('  $' + '{:,.0f}'.format(vol) + ' - ' + q + '...')
