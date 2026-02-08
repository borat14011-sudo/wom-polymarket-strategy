$data = Invoke-RestMethod -Uri 'https://gamma-api.polymarket.com/markets?limit=100&active=true&closed=false'
$data | ConvertTo-Json -Depth 20 | Out-File -FilePath 'markets.json' -Encoding UTF8
