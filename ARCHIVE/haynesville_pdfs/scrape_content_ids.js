// Content ID Extraction Script for Haynesville Black Books
// Run this in browser console to extract FIELD ORDER Content IDs

function extractFieldOrders() {
  const rows = document.querySelectorAll('table[summary*="Document Results"] tbody tr, table tbody tr');
  const results = [];
  
  for (const row of rows) {
    const cells = row.querySelectorAll('td');
    if (cells.length < 6) continue;
    
    // Find the Document Type cell (contains "FIELD ORDER", "SURVEY PLATS", etc.)
    let docTypeIdx = -1;
    let contentIdIdx = -1;
    
    for (let i = 0; i < cells.length; i++) {
      const text = cells[i].textContent.trim();
      if (text === 'FIELD ORDER' || text === 'SURVEY PLATS' || text === 'HEARING DOCKET') {
        docTypeIdx = i;
      }
      // Content ID is numeric, 5-8 digits, appears before doc type
      if (/^\d{5,8}$/.test(text) && contentIdIdx === -1 && docTypeIdx === -1) {
        contentIdIdx = i;
      }
    }
    
    // Only capture FIELD ORDER documents
    if (docTypeIdx > -1 && cells[docTypeIdx].textContent.trim() === 'FIELD ORDER') {
      results.push({
        contentId: cells[contentIdIdx]?.textContent.trim() || cells[3]?.textContent.trim(),
        docType: 'FIELD ORDER',
        refNum: cells[docTypeIdx + 2]?.textContent.trim() || '',
        fieldCode: cells[docTypeIdx + 3]?.textContent.trim() || '',
        fieldName: cells[docTypeIdx + 4]?.textContent.trim() || '',
        description: cells[docTypeIdx + 5]?.textContent.trim() || '',
        docket: cells[docTypeIdx + 6]?.textContent.trim() || '',
        pages: cells[cells.length - 1]?.textContent.trim() || ''
      });
    }
  }
  
  return results;
}

// Return results
extractFieldOrders();
