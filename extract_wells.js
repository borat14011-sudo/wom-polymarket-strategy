const DBFFile = require('dbffile');

async function extractWells() {
    try {
        const dbf = await DBFFile.DBFFile.open('C:\\Users\\Borat\\.openclaw\\workspace\\haynesville_data\\Haynesville_Shale_Oil_Gas_Wells.dbf');
        
        console.log('DBF file opened successfully');
        console.log('Field names:', dbf.fields.map(f => f.name).join(', '));
        console.log('Total records:', dbf.recordCount);
        console.log('\n--- First 10 Wells ---\n');
        
        const records = await dbf.readRecords(10);
        
        records.forEach((record, index) => {
            console.log(`\n=== Well ${index + 1} ===`);
            console.log(JSON.stringify(record, null, 2));
        });
        
        // Save to JSON for later use
        const fs = require('fs');
        fs.writeFileSync('wells_data.json', JSON.stringify(records, null, 2));
        console.log('\n\nWell data saved to wells_data.json');
        
    } catch (error) {
        console.error('Error reading DBF file:', error);
    }
}

extractWells();
