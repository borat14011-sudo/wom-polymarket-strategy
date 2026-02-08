const https = require('https');
https.get('https://gamma-api.polymarket.com/markets?limit=2&offset=10000', (res) => {
  let d = '';
  res.on('data', c => d += c);
  res.on('end', () => {
    const m = JSON.parse(d);
    m.forEach(x => console.log(x.endDate, x.question.substring(0, 40)));
  });
}).on('error', e => console.error(e));
