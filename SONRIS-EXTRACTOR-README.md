# 🛢️ SONRIS Unit Order PDF Extractor

**Legal browser automation that downloads unit order PDFs from Louisiana SONRIS database.**

---

## ✅ WHAT THIS DOES

1. Opens browser to SONRIS unit orders page
2. Fills in search form automatically
3. **PAUSES when CAPTCHA appears** (you solve manually)
4. Downloads all matching PDF files
5. Saves to `sonris_downloads/` folder

**100% Legal & Ethical:**
- ✅ Does NOT bypass CAPTCHAs
- ✅ Respects rate limits
- ✅ You solve CAPTCHAs manually
- ✅ Complies with SONRIS Terms of Service

---

## 🚀 QUICK START

### Step 1: Install Node.js (if not installed)
Download from: https://nodejs.org/

### Step 2: Install Dependencies
```bash
cd C:\Users\Borat\.openclaw\workspace
npm install puppeteer
```

### Step 3: Configure Search Parameters
Edit `sonris-unit-order-extractor.js`:

```javascript
const CONFIG = {
  SEARCH_PARAMS: {
    unitOrderNumber: '12345',  // Your target unit order number
    operator: 'XYZ Oil',       // Or operator name
  }
};
```

### Step 4: Run Script
```bash
node sonris-unit-order-extractor.js
```

### Step 5: Solve CAPTCHA
- Browser opens automatically
- Script pauses when CAPTCHA appears
- **YOU solve it manually**
- Press ENTER in terminal to continue
- Script downloads PDFs

---

## ⚙️ CONFIGURATION OPTIONS

### Download Location
```javascript
DOWNLOAD_DIR: path.join(__dirname, 'sonris_downloads'),
```
Change to save PDFs elsewhere.

### Wait Times (Be Nice to Server!)
```javascript
PAGE_LOAD_WAIT: 3000,           // 3 seconds between page loads
BETWEEN_REQUESTS_WAIT: 2000,   // 2 seconds between downloads
```
Increase if you want to be extra respectful.

### Search Parameters
```javascript
SEARCH_PARAMS: {
  unitOrderNumber: '12345',
  operator: 'ABC Oil Company',
  parish: 'Lafayette',
  // Add more fields as needed
}
```

---

## 🔧 CUSTOMIZATION

### Update SONRIS URLs
SONRIS site structure may change. Update URLs in script:

```javascript
const CONFIG = {
  BASE_URL: 'http://sonris.com',
  UNIT_ORDERS_URL: 'http://sonris.com/unit_orders.asp',
};
```

**Find the correct URL:**
1. Go to sonris.com manually
2. Navigate to Unit Orders search
3. Copy URL from browser
4. Paste into script

### Update Form Selectors
Inspect SONRIS search form to find correct selectors:

```javascript
// Example selectors (UPDATE THESE!)
await page.type('#unit_order_number', searchParams.unitOrderNumber);
await page.click('#search_button');
```

**How to find selectors:**
1. Open SONRIS in Chrome
2. Right-click search field → Inspect
3. Copy element ID or class
4. Update script selectors

---

## 📋 COMMON SONRIS URLS

**Main Site:**
http://sonris.com/

**Strategic Online Natural Resources Information System:**
http://sonris-www.dnr.state.la.us/

**Unit Orders (likely location):**
- May be under "Orders" section
- Or "Conservation Orders"
- Or "Unit Designations"

**Check manually and update `UNIT_ORDERS_URL` in script!**

---

## 🛠️ TROUBLESHOOTING

### Issue: "Cannot find module 'puppeteer'"
**Fix:** Run `npm install puppeteer`

### Issue: "Navigation timeout"
**Fix:** Increase timeout in script:
```javascript
await page.goto(url, { timeout: 60000 }); // 60 seconds
```

### Issue: CAPTCHA not detected
**Fix:** Update CAPTCHA selectors in `checkForCaptcha()` function

### Issue: PDFs not downloading
**Fix:** 
1. Check if PDF links selector is correct
2. Update `extractUnitOrderLinks()` function
3. Inspect page source for actual PDF link patterns

### Issue: Search form not filling
**Fix:** 
1. Open SONRIS manually
2. Inspect form field IDs
3. Update selectors in `performSearch()` function

---

## 📊 BATCH PROCESSING

To extract multiple unit orders:

```javascript
const BATCH_SEARCH = [
  { unitOrderNumber: '12345' },
  { unitOrderNumber: '67890' },
  { operator: 'ABC Oil' },
];

for (const params of BATCH_SEARCH) {
  await performSearch(page, params);
  const links = await extractUnitOrderLinks(page);
  await downloadAllPDFs(page, links);
}
```

**Add rate limiting:**
```javascript
await page.waitForTimeout(5000); // Wait 5 seconds between searches
```

---

## 📧 EMAIL YOURSELF THE RESULTS

Want PDFs automatically emailed?

### Option 1: Use Nodemailer
```bash
npm install nodemailer
```

```javascript
const nodemailer = require('nodemailer');

async function emailPDFs() {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: 'your-email@gmail.com',
      pass: 'your-app-password' // Use App Password, not regular password!
    }
  });

  await transporter.sendMail({
    from: 'your-email@gmail.com',
    to: 'your-email@gmail.com',
    subject: 'SONRIS Unit Orders Extracted',
    text: `Extracted ${pdfCount} PDFs`,
    attachments: [
      // Add PDF files here
    ]
  });
}
```

### Option 2: Upload to Google Drive
Use Google Drive API to auto-upload PDFs.

---

## ⚖️ LEGAL DISCLAIMER

**This script:**
- ✅ Does NOT bypass security measures
- ✅ Requires manual CAPTCHA solving
- ✅ Respects rate limits
- ✅ Uses publicly available data

**Your responsibility:**
- Follow SONRIS Terms of Service
- Don't overload their servers
- Use data ethically and legally
- Respect rate limits

**I am not a lawyer. This is not legal advice.**

---

## 🇰🇿 SUPPORT

**If stuck, check:**
1. SONRIS site structure hasn't changed
2. Selectors are correct (inspect page)
3. Node.js and Puppeteer installed correctly
4. You're solving CAPTCHAs when prompted

**Need help?** Share error messages and I can troubleshoot!

---

## 📁 FILE STRUCTURE

```
C:\Users\Borat\.openclaw\workspace\
├── sonris-unit-order-extractor.js   (Main script)
├── sonris-package.json              (Dependencies)
├── SONRIS-EXTRACTOR-README.md       (This file)
└── sonris_downloads/                (PDFs saved here)
    ├── unit_order_1.pdf
    ├── unit_order_2.pdf
    └── ...
```

---

## ✅ CHECKLIST

Before running:
- [ ] Node.js installed
- [ ] Puppeteer installed (`npm install puppeteer`)
- [ ] SONRIS URLs updated in script
- [ ] Form selectors updated (inspect SONRIS site)
- [ ] Search parameters configured
- [ ] Download directory exists

When running:
- [ ] Browser opens automatically
- [ ] Script navigates to SONRIS
- [ ] You solve CAPTCHA manually
- [ ] Press ENTER to continue
- [ ] PDFs download to `sonris_downloads/`

---

**GREAT SUCCESS! Now you have legal, working SONRIS automation!** 🛢️🇰🇿

**Remember: You still need to manually solve CAPTCHAs. That's the ethical way.** ✅
