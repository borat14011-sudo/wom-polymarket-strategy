const https = require('https');
const { URL } = require('url');

const urlString = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=7&interval=daily';
const url = new URL(urlString);

const options = {
  hostname: url.hostname,
  path: url.pathname + url.search,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
  }
};

console.log('Request:', options);

https.get(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    console.log('Data length:', data.length);
    
    try {
      const parsed = JSON.parse(data);
      console.log('Parsed! Keys:', Object.keys(parsed));
      console.log('Has prices?', !!parsed.prices);
      if (parsed.prices) {
        console.log('Prices length:', parsed.prices.length);
        console.log('First:', parsed.prices[0]);
      }
    } catch (e) {
      console.log('Parse error:', e.message);
      console.log('First 500 chars:', data.substring(0, 500));
    }
  });
}).on('error', (err) => {
  console.error('HTTP error:', err);
});
