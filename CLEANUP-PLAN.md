# 🗂️ STRATEGIC DESKTOP/WORKSPACE CLEANUP PLAN
**Generated:** 2026-02-08  
**Objective:** Keep only essential active trading and content systems

---

## 📊 CURRENT STATE ANALYSIS

### Desktop Overview (58 items)
- **Grandma Animation Project** - Recently completed (2/6/2026)
- **Instagram Content Pack** - Ready for upload/archival
- **Sonris PDF Tools** - One-time extraction task completed
- **Upload/Automation Scripts** - Temporary helper scripts
- **Video files** - 4 MP4s (grandma animation outputs)

### Workspace Overview (4,000+ files)
- **Polymarket Trading System** - Active, sophisticated trading infrastructure
- **Madrid Content Hub** - City content packs (minimal)
- **Haynesville Data** - Oil/gas well data (GIS files)
- **Node Dependencies** - Multiple node_modules folders
- **Legacy Projects** - Many abandoned/experimental scripts

---

## 🎯 PROJECT CATEGORIZATION

### ✅ ACTIVE PROJECTS (Keep)

#### 1. **Polymarket Trading System** (PRIORITY 1)
**Status:** ACTIVE & ESSENTIAL  
**Location:** `workspace/polymarket_trading_system/` + root workspace
**Value:** Live trading infrastructure, extensive backtesting, $ at stake

**Core Components:**
- `polymarket_trading_system/` - Main system (10 files)
- `backtest-results/` - Historical data
- `polymarket-backtest/` - Validation system
- `polymarket-monitor/` - Live monitoring
- `agent-monitor-live/` - Agent tracking
- Core scripts: `trading-cli.py`, `api.py`, `signal-generator.py`
- Database: `polymarket_history.db`, `historical_2024.db`
- Live monitors: `live_opportunity_monitor.py`, `live_monitor_simple.py`

**Action:** Keep all, organize into clearer structure

#### 2. **Madrid/Content System** (PRIORITY 2)
**Status:** ACTIVE - Ongoing content business
**Location:** `madrid-borat-content-hub/`, `Instagram-Content-Files/`

**Core Files:**
- Content packs: barcelona, paris, rome
- Growth systems: influencer playbook, viral hooks
- Monetization: revenue roadmap, sponsorship system

**Action:** Consolidate, archive old iterations

#### 3. **Core Workspace Infrastructure**
**Status:** ESSENTIAL
- `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`
- `.git/` repository
- `memory/` folder (daily notes)

**Action:** Keep, maintain

---

### 📦 ARCHIVE CANDIDATES (Move to Archive)

#### 1. **Grandma Animation Project** (COMPLETED)
**Status:** COMPLETED 2/6/2026  
**Location:** Desktop  
**Deliverables:** 4 MP4 videos, HTML page

**Files to Archive:**
```
grandma-animated-v2.mp4
GRANDMA-REVIEWS-PAINTINGS.mp4
GRANDMA-REVIEWS-PAINTINGS-FINAL.mp4
grandma-animation-raw.mp4
grandma-video-improved.html
grandma-scenes/ (folder)
animation-scenes.txt
VIDEO-LINK*.txt files
```

**Keep:** Final deliverable + download link only

#### 2. **Sonris PDF Extraction** (COMPLETED)
**Status:** ONE-TIME TASK COMPLETED
**Location:** Desktop + workspace

**Files to Archive:**
```
sonris_pdfs/ (folder)
SONRIS-STATUS-REPORT.md
SONRIS-EXTRACTOR-README.md
sonris-unit-order-extractor.js
sonris-example-working.js
sonris-package.json
RUN-SONRIS*.bat files
OPEN-SONRIS-FILES.bat
UPLOAD-INSTAGRAM-FILES.bat
DRAG-TO-DRIVE-NOW.txt
CHECK-DRIVE-NOW.txt
```

**Note:** This was a one-time extraction - fully completed

#### 3. **Upload/Helper Scripts** (TEMPORARY)
**Status:** TEMPORARY/USED
**Location:** Desktop

**Files to Delete:**
```
upload-via-cdp.js
extract-and-upload.ps1
drive-upload-simple.ps1
drive-api-upload.js
mouse-drag-upload.ps1
upload-reliable.ps1
upload-with-windows-automation.ps1
auto-upload-drive.js
upload-to-drive.js
WHEN-YOU-RETURN-READ-THIS.txt
EMAIL-TO-YOURSELF.txt
READY-TO-RUN.txt
ANIMATED-VIDEO-COMPLETE.txt
```

#### 4. **Kimi Model Testing** (EXPERIMENTAL - COMPLETED)
**Status:** EXPERIMENTAL COMPLETED
**Location:** Workspace root

**Files to Archive:**
```
KIMI_COMMANDS.md
KIMI_TEST_RESULTS.md
KIMI_QUICKREF.md
kimi-models-env.ps1
KIMI_MODEL_GUIDE.md
KIMI_IMPLEMENTATION_GUIDE.md
KIMI_MODEL_STACK_CONFIG.md
```

#### 5. **Polymarket Research Phase** (SUPERSEDED)
**Status:** RESEARCH COMPLETED, IMPLEMENTATION ACTIVE
**Location:** Workspace root

Many markdown reports from research phase - superseded by actual implementation.

**Keep:** Key strategy documents, archive the rest

#### 6. **Backtest Validation Reports** (HISTORICAL)
**Status:** HISTORICAL DATA

Dozens of validation reports from development. Keep latest, archive old iterations.

#### 7. **Test/Diagnostic Scripts** (DEVELOPMENT ARTIFACTS)
**Status:** TEMPORARY

Hundreds of test scripts used during development:
- `test_*.js`, `test_*.py`
- `check_*.js`, `check_*.py`
- `debug_*.js`
- Diagnostic outputs

---

### 🗑️ DELETE CANDIDATES

#### 1. **Verification Screenshots** (Desktop)
```
gmail-final-check.png
gmail-check.png
SUCCESS-CHECK.png
final-check.png
upload-verification.png
screen-verification.png
```

#### 2. **2Captcha Setup Files** (Desktop)
```
2CAPTCHA-READY.txt
INSTALL-2CAPTCHA.bat
2CAPTCHA-SETUP-GUIDE.txt
RUN-SONRIS-2CAPTCHA.bat
sonris-with-2captcha.js
```

#### 3. **Node Modules Duplicates**
Multiple `node_modules/` folders - keep only main workspace one

#### 4. **Package Lock Duplicates**
Multiple `package-lock.json` files

#### 5. **Old Memory Files**
- `MEMORY_ARCHIVE_2026-02-08.md` (superseded)

#### 6. **Git Artifacts in Wrong Places**
Nested `.git` folders if any

---

## 📁 PROPOSED ARCHIVE STRUCTURE

```
~/ARCHIVE/
├── 2026-02-08-CLEANUP/
│   ├── 01-Grandma-Animation-Project/
│   │   ├── videos/
│   │   ├── scenes/
│   │   └── documentation/
│   ├── 02-Sonris-PDF-Extraction/
│   │   ├── scripts/
│   │   ├── outputs/
│   │   └── documentation/
│   ├── 03-Kimi-Model-Testing/
│   ├── 04-Polymarket-Research-Phase/
│   │   ├── validation-reports/
│   │   ├── backtest-iterations/
│   │   └── strategy-evolution/
│   └── 05-Content-System-V1/
│       └── early-iterations/
│
~/Desktop/
├── ACTIVE/
│   └── (symlinks to current work)
└── README-Active-Projects.txt

~/workspace/ (CLEANED)
├── polymarket-trading/
│   ├── system/          (from polymarket_trading_system/)
│   ├── backtesting/
│   ├── live-monitoring/
│   ├── data/
│   └── documentation/
├── content-system/
│   ├── madrid/
│   ├── barcelona/
│   ├── paris/
│   └── rome/
├── haynesville-data/
│   └── (GIS files)
├── infrastructure/
│   ├── memory/
│   ├── agents/
│   └── tools/
└── .git/
```

---

## 🚀 RECOMMENDED CLEANUP SEQUENCE

### Phase 1: SAFETY FIRST (10 min)
1. ✅ Create full backup of workspace
2. ✅ Commit current state to git
3. ✅ Create `ARCHIVE/` folder on Desktop

### Phase 2: Desktop Quick Win (15 min)
1. Move Grandma Animation → `ARCHIVE/01-Grandma-Animation/`
2. Delete all verification screenshots
3. Delete all upload helper scripts
4. Move Sonris files → `ARCHIVE/02-Sonris-PDF/`
5. Delete 2Captcha setup files
6. Keep only: `README.txt`, `Visual Studio Code.lnk`

### Phase 3: Workspace Archive (30 min)
1. Create `workspace/ARCHIVE/` folder
2. Move all `KIMI_*.md` files → Archive
3. Move old `BACKTEST_*.md` reports → Archive (keep last 5)
4. Move `AGENT*_*.md` reports → Archive
5. Move test/diagnostic scripts → Archive

### Phase 4: Organization (30 min)
1. Consolidate Polymarket system:
   ```
   polymarket-trading/
   ├── core/          (trading_bot.py, api.py, config)
   ├── backtest/      (backtest scripts + results)
   ├── live/          (monitoring scripts)
   ├── data/          (databases, json files)
   └── docs/          (essential docs only)
   ```
2. Consolidate Content system
3. Clean up stray files at root

### Phase 5: Final Cleanup (15 min)
1. Remove duplicate `node_modules` (keep main)
2. Remove `.pyc` cache files
3. Remove empty folders
4. Update `.gitignore`
5. Final git commit

---

## 📊 ESTIMATED IMPACT

### Before Cleanup
- **Desktop:** ~58 files/folders
- **Workspace:** ~4,000+ files
- **Clutter Level:** HIGH
- **Focus Clarity:** LOW

### After Cleanup
- **Desktop:** ~5-10 active items
- **Workspace:** ~500-800 active files
- **Clutter Level:** MINIMAL
- **Focus Clarity:** HIGH

### Space Savings
- Estimated reduction: 60-70% fewer files in active workspace
- Archive folder: ~2,000-2,500 files safely stored

---

## ⚠️ IMPORTANT NOTES

### DO NOT DELETE:
1. ✅ `polymarket_trading_system/` - ACTIVE TRADING
2. ✅ `trading-cli.py`, `api.py`, `signal-generator.py`
3. ✅ Any `.db` files (trading data)
4. ✅ `AGENTS.md`, `SOUL.md`, `USER.md`
5. ✅ `.git/` repository
6. ✅ `memory/` folder

### SAFE TO ARCHIVE:
1. ✅ Anything marked "COMPLETED"
2. ✅ Test/diagnostic scripts (can restore if needed)
3. ✅ Old validation reports (superseded by newer)
4. ✅ Research phase documentation

### RISKS:
- **LOW:** Archiving old reports and tests
- **MEDIUM:** Moving database files (verify references first)
- **HIGH:** Deleting active trading system files

---

## 🎬 NEXT ACTIONS

1. **Review this plan** - Mark any disagreements
2. **Run Phase 1** (safety backup)
3. **Execute Phase 2** (desktop cleanup - safe)
4. **Review Phase 3 results** before proceeding
5. **Continue with Phases 4-5** as comfortable

**Total Estimated Time:** 1.5-2 hours  
**Recommended:** Execute in chunks, not all at once

---

## 📈 ONGOING MAINTENANCE

- Weekly: Archive completed tasks
- Monthly: Review and archive old reports
- Quarterly: Full cleanup pass

**Golden Rule:** If not touched in 30 days → Archive. If not touched in 90 days → Consider delete.
