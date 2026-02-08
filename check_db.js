const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database('polymarket_history.db', (err) => {
  if (err) {
    console.error('Error opening database:', err);
    process.exit(1);
  }
});

db.get("SELECT COUNT(DISTINCT market_id) as count FROM price_history", (err, row) => {
  if (err) {
    console.error('Error:', err);
    process.exit(1);
  }
  console.log(`Markets in database: ${row.count}`);
  
  db.get("SELECT MIN(timestamp) as min_ts, MAX(timestamp) as max_ts, COUNT(*) as total FROM price_history", (err, row) => {
    if (err) {
      console.error('Error:', err);
      process.exit(1);
    }
    const minDate = new Date(row.min_ts * 1000);
    const maxDate = new Date(row.max_ts * 1000);
    console.log(`Date range: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
    console.log(`Total records: ${row.total}`);
    
    db.all(`
      SELECT market_id, COUNT(*) as records, 
             MIN(timestamp) as first_ts, 
             MAX(timestamp) as last_ts
      FROM price_history 
      GROUP BY market_id 
      LIMIT 5
    `, (err, rows) => {
      if (err) {
        console.error('Error:', err);
        process.exit(1);
      }
      
      console.log('\nSample markets:');
      rows.forEach(row => {
        const first = new Date(row.first_ts * 1000).toISOString();
        const last = new Date(row.last_ts * 1000).toISOString();
        console.log(`  ${row.market_id.substring(0, 30)}... - ${row.records} records from ${first} to ${last}`);
      });
      
      db.close();
    });
  });
});
