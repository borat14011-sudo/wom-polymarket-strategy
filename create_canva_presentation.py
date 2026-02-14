#!/usr/bin/env python3
"""
Create Canva presentation files and save to OneDrive
"""

import os
import json
from datetime import datetime

def create_canva_presentation():
    """Create Canva presentation files"""
    
    print("="*60)
    print("CREATE CANVA PRESENTATION FOR ONEDRIVE")
    print("="*60)
    
    # Target directory in OneDrive
    target_dir = r"C:\Users\Borat\OneDrive\Trading\Canva_Presentation"
    
    # Create directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")
    
    # Read the Canva presentation content
    with open('CANVA_PRESENTATION_CONTENT.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse slides from the markdown
    slides = []
    current_slide = {}
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('## SLIDE'):
            if current_slide:
                slides.append(current_slide)
            slide_num = line.split(':')[0].split()[-1]
            slide_title = line.split(':')[1].strip() if ':' in line else ''
            current_slide = {
                'number': slide_num,
                'title': slide_title,
                'content': [],
                'visuals': [],
                'elements': []
            }
        elif line.startswith('**Title:**') and 'title' in current_slide and not current_slide['title']:
            current_slide['title'] = line.replace('**Title:**', '').strip()
        elif line.startswith('**Content:**'):
            # Skip the content header
            pass
        elif line.startswith('**Visual:**'):
            current_slide['visuals'].append(line.replace('**Visual:**', '').strip())
        elif line.startswith('**Elements:**'):
            # Skip elements header
            pass
        elif line.startswith('- ') and 'elements' in current_slide:
            current_slide['elements'].append(line[2:].strip())
        elif line and not line.startswith('---') and not line.startswith('#') and not line.startswith('**Design'):
            if line and 'content' in current_slide:
                current_slide['content'].append(line)
    
    if current_slide:
        slides.append(current_slide)
    
    # Create slide-by-slide files
    print(f"\nCreating {len(slides)} slide files...")
    
    for i, slide in enumerate(slides[:15]):  # First 15 slides
        slide_num = i + 1
        slide_file = os.path.join(target_dir, f"Slide_{slide_num:02d}.txt")
        
        slide_content = f"""SLIDE {slide_num}: {slide.get('title', '')}
{'='*60}

CONTENT:
{chr(10).join(slide.get('content', []))}

VISUALS:
{chr(10).join(['- ' + v for v in slide.get('visuals', [])])}

ELEMENTS:
{chr(10).join(['- ' + e for e in slide.get('elements', [])])}

DESIGN NOTES:
- Background: Dark gradient (#0f0c29 to #302b63)
- Primary Color: #00ff88 (green)
- Font: Montserrat Bold (headers), Inter Regular (body)
- Icons: Use Kazakhstan flag, robot, chart emojis
"""
        
        with open(slide_file, 'w', encoding='utf-8') as f:
            f.write(slide_content)
        
        print(f"  Created: Slide_{slide_num:02d}.txt")
    
    # Create a master presentation file
    master_file = os.path.join(target_dir, "BORAT_TRADING_SYSTEM_PRESENTATION.md")
    
    master_content = f"""# BORAT LIVE TRADING SYSTEM - CANVA PRESENTATION
## Complete Presentation for Canva Import

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Target:** OneDrive\\Trading\\Canva_Presentation
**Slides:** 15
**Status:** READY FOR CANVA IMPORT

---

## PRESENTATION OVERVIEW

**Title:** BORAT LIVE TRADING SYSTEM
**Subtitle:** AI-Powered Prediction Market Trading
**Theme:** Dark Tech / Finance Dashboard
**Slides:** 15 total

**Color Palette:**
- Background: Dark gradient (#0f0c29 → #302b63)
- Primary: #00ff88 (green)
- Secondary: #00d4ff (cyan) 
- Accent: #ffeb3b (yellow)
- Text: White #ffffff

**Fonts:**
- Headers: Montserrat Bold
- Body: Inter Regular
- Metrics: JetBrains Mono

**Icons/Emojis:**
🇰🇿 🤖 📈 💰 ⚡ ✅

---

## SLIDE LIST

"""
    
    # Add slide summaries
    for i, slide in enumerate(slides[:15]):
        slide_num = i + 1
        title = slide.get('title', f'Slide {slide_num}')
        master_content += f"{slide_num:2d}. {title}\n"
    
    master_content += f"""
---

## CANVA IMPORT INSTRUCTIONS

1. **Open Canva** (canva.com)
2. **Create New Presentation**
3. **Choose Template:** "Dark Tech Presentation" or "Crypto Dashboard"
4. **For Each Slide:**
   - Open corresponding Slide_XX.txt file
   - Copy content into Canva slide
   - Apply design elements as noted
5. **Apply Design:**
   - Set background to dark gradient
   - Use color palette consistently
   - Add Kazakhstan flag emoji where indicated
6. **Export Options:**
   - PDF: For sharing/documentation
   - PPTX: For PowerPoint
   - Video: For animated presentation
   - Link: For online sharing

---

## QUICK START

**Easiest Method:**
1. Open Canva
2. Search for "Dark Tech Presentation" template
3. Replace template text with content from Slide_XX.txt files
4. Apply Kazakhstan flag 🇰🇿 and robot 🤖 emojis
5. Export as PDF to OneDrive

**File Location:** {target_dir}

**Total Slides:** 15
**Estimated Time:** 30-45 minutes to build in Canva

---

## DESIGN ASSETS TO ADD

1. **Charts/Graphs:**
   - Performance metrics bar chart
   - Equity curve timeline
   - Risk pyramid diagram
   - Agent architecture flowchart

2. **Icons:**
   - Kazakhstan flag 🇰🇿
   - Robot/AI 🤖
   - Money bag 💰
   - Lightning bolt ⚡
   - Checkmarks ✅

3. **Screenshots:**
   - Live dashboard
   - Telegram logs
   - Portfolio tracker

---

## EXPORT SETTINGS

**PDF Export:**
- Quality: High
- Pages: All
- Size: Standard (1920x1080)
- Include speaker notes: Yes

**Presentation Mode:**
- Auto-advance: 30 seconds per slide
- Transitions: Fade
- Background music: Optional (tech/ambient)

---

## SHARING OPTIONS

1. **OneDrive:** Save PDF to Trading folder
2. **Google Drive:** Upload for team access
3. **Email:** Send as PDF attachment
4. **Slack/Teams:** Share link
5. **Presentation:** Present directly from Canva

---

**Presentation Ready for Canva Import!**
"""
    
    with open(master_file, 'w', encoding='utf-8') as f:
        f.write(master_content)
    
    print(f"\nCreated master file: {master_file}")
    
    # Create a batch file to open the folder
    batch_file = os.path.join(target_dir, "OPEN_PRESENTATION_FILES.bat")
    batch_content = f"""@echo off
echo ========================================
echo BORAT TRADING SYSTEM - CANVA PRESENTATION
echo ========================================
echo.
echo Presentation files are ready in this folder!
echo.
echo FILES:
echo 1. BORAT_TRADING_SYSTEM_PRESENTATION.md - Complete guide
echo 2. Slide_01.txt to Slide_15.txt - Individual slides
echo 3. OPEN_PRESENTATION_FILES.bat - This file
echo.
echo TO BUILD IN CANVA:
echo 1. Open Canva (canva.com)
echo 2. Create new presentation
echo 3. Use "Dark Tech" template
echo 4. Copy content from Slide_XX.txt files
echo 5. Export as PDF
echo.
echo Press any key to open this folder...
pause >nul

explorer "{target_dir}"
"""
    
    with open(batch_file, 'w', encoding='ascii') as f:
        f.write(batch_content)
    
    print(f"Created batch file: {batch_file}")
    
    # Create a simple HTML version for quick preview
    html_file = os.path.join(target_dir, "PRESENTATION_PREVIEW.html")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Borat Trading System - Presentation Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 100%);
            color: white;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(0,0,0,0.7);
            padding: 30px;
            border-radius: 10px;
        }}
        h1 {{
            color: #00ff88;
            text-align: center;
        }}
        h2 {{
            color: #00d4ff;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 10px;
        }}
        .slide {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 4px solid #ffeb3b;
        }}
        .slide-number {{
            background: #00ff88;
            color: black;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 10px;
        }}
        .instructions {{
            background: rgba(0, 212, 255, 0.2);
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .emoji {{
            font-size: 24px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="emoji">🇰🇿 BORAT LIVE TRADING SYSTEM</h1>
        <h2>AI-Powered Prediction Market Trading</h2>
        
        <div class="instructions">
            <h3>📋 Presentation Preview</h3>
            <p>This is a preview of the Canva presentation. To build in Canva:</p>
            <ol>
                <li>Open <strong>canva.com</strong></li>
                <li>Create new presentation with "Dark Tech" template</li>
                <li>Copy content from Slide_XX.txt files in this folder</li>
                <li>Export as PDF to OneDrive</li>
            </ol>
            <p><strong>Location:</strong> {target_dir}</p>
        </div>
        
        <h2>📊 Slide Preview (15 Slides Total)</h2>
"""
    
    # Add slide previews
    for i, slide in enumerate(slides[:15]):
        slide_num = i + 1
        title = slide.get('title', f'Slide {slide_num}')
        content_preview = ' '.join(slide.get('content', []))[:150] + '...' if slide.get('content') else ''
        
        html_content += f"""
        <div class="slide">
            <div class="slide-number">SLIDE {slide_num}</div>
            <h3>{title}</h3>
            <p>{content_preview}</p>
            <p><strong>Visuals:</strong> {', '.join(slide.get('visuals', ['Chart/Diagram']))}</p>
        </div>
        """
    
    html_content += f"""
        <div class="instructions">
            <h3>🚀 Ready for Canva!</h3>
            <p>All 15 slides are prepared with content, visuals, and design notes.</p>
            <p>Open the folder and start building in Canva:</p>
            <button onclick="window.open('file:///{target_dir.replace('\\\\', '/')}')">
                📁 Open Presentation Folder
            </button>
        </div>
        
        <div style="text-align: center; margin-top: 40px; color: #ffeb3b;">
            <p class="emoji">🤖 📈 💰 ⚡ ✅</p>
            <p><strong>Great success! The future is automated trading with AI!</strong></p>
            <p>🇰🇿 Borat Trading System | {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
    
    <script>
        // Make the button work
        document.querySelector('button').addEventListener('click', function() {{
            window.open('file:///{target_dir.replace('\\\\', '/')}');
        }});
    </script>
</body>
</html>
"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Created HTML preview: {html_file}")
    
    return target_dir, len(slides[:15])

def main():
    print("\nCreating Canva presentation files...")
    
    try:
        target_dir, slide_count = create_canva_presentation()
        
        print("\n" + "="*60)
        print("✅ CANVA PRESENTATION CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nLocation: {target_dir}")
        print(f"Total Slides: {slide_count}")
        print("\nFiles Created:")
        print(f"1. BORAT_TRADING_SYSTEM_PRESENTATION.md - Complete guide")
        print(f"2. Slide_01.txt to Slide_{slide_count:02d}.txt - Individual slides")
        print(f"3. PRESENTATION_PREVIEW.html - Web preview")
        print(f"4. OPEN_PRESENTATION_FILES.bat - One-click opener")
        
        print("\n🎨 TO BUILD IN CANVA:")
        print("1. Open Canva (canva.com)")
        print("2. Create new presentation")
        print("3. Use 'Dark Tech Presentation' template")
        print("4. Copy content from Slide_XX.txt files")
        print("5. Apply Kazakhstan flag 🇰🇿 and robot 🤖 emojis")
        print("6. Export as PDF to OneDrive")
        
        print("\n🚀 QUICK START:")
        print(f"Run: OPEN_PRESENTATION_FILES.bat in the folder")
        
        # Try to open the folder
        try:
            os.startfile(target_dir)
            print("\n📁 Folder opened automatically!")
        except:
            print(f"\n📁 Open folder manually: {target_dir}")
            
    except Exception as e:
        print(f"\n❌ Error creating presentation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "="*60)
        print("🇰🇿 GREAT SUCCESS! PRESENTATION READY FOR CANVA!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ PRESENTATION CREATION FAILED")
        print("="*60)