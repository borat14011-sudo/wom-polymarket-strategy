from playwright.sync_api import sync_playwright
import time
import os

def upload_to_google_drive():
    print("Starting full Google Drive automation...")
    print("This will create folder and upload files automatically.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1400, 'height': 900})
        page = context.new_page()
        
        # Go to Google Drive
        print("Opening Google Drive...")
        page.goto('https://drive.google.com/drive/my-drive')
        
        # Wait for page to load
        print("Waiting for Google Drive to load...")
        page.wait_for_timeout(3000)
        
        # Check if login required
        if 'signin' in page.url or page.locator('text=Sign in').count() > 0:
            print("Please log in to Google Drive (Borat14011@gmail.com)")
            print("Waiting for login...")
            while 'signin' in page.url or page.locator('text=Sign in').count() > 0:
                page.wait_for_timeout(2000)
            print("Logged in!")
        
        print("Creating folder...")
        # Click New button
        page.click('[role="button"]:has-text("New")')
        page.wait_for_timeout(1000)
        
        # Click Folder
        page.click('text=Folder')
        page.wait_for_timeout(1000)
        
        # Type folder name
        page.fill('input[aria-label="Folder name"]', 'Trading-Strategy-Presentation')
        page.wait_for_timeout(500)
        
        # Click Create
        page.click('button:has-text("Create")')
        page.wait_for_timeout(2000)
        
        print("Folder created! Opening it...")
        
        # Double click to open folder
        page.dblclick('text=Trading-Strategy-Presentation')
        page.wait_for_timeout(2000)
        
        # Upload first file (index.html)
        print("Uploading index.html...")
        file_path = r"C:\Users\Borat\.openclaw\workspace\netlify-deploy\index.html"
        
        # Click New
        page.click('[role="button"]:has-text("New")')
        page.wait_for_timeout(1000)
        
        # Click File upload
        page.click('text=File upload')
        page.wait_for_timeout(1000)
        
        # Handle file chooser
        with page.expect_file_chooser() as fc_info:
            page.click('text=File upload')
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        
        page.wait_for_timeout(3000)
        print("index.html uploaded!")
        
        # Upload second file
        print("Uploading PROFESSIONAL_STRATEGY_PRESENTATION.md...")
        file_path2 = r"C:\Users\Borat\.openclaw\workspace\PROFESSIONAL_STRATEGY_PRESENTATION.md"
        
        page.click('[role="button"]:has-text("New")')
        page.wait_for_timeout(1000)
        
        with page.expect_file_chooser() as fc_info:
            page.click('text=File upload')
        file_chooser = fc_info.value
        file_chooser.set_files(file_path2)
        
        page.wait_for_timeout(3000)
        print("PROFESSIONAL_STRATEGY_PRESENTATION.md uploaded!")
        
        # Get shareable link
        print("Getting shareable link...")
        page.click('[role="button"]:has-text("New")')
        page.wait_for_timeout(500)
        page.click('text=Folder')
        page.wait_for_timeout(500)
        
        # Go back to parent
        page.click('[aria-label="Back"]')
        page.wait_for_timeout(1000)
        
        # Right click on folder
        page.click('text=Trading-Strategy-Presentation', button='right')
        page.wait_for_timeout(1000)
        
        # Click Share
        page.click('text=Share')
        page.wait_for_timeout(2000)
        
        # Copy link
        page.click('text=Copy link')
        page.wait_for_timeout(1000)
        
        print("Link copied to clipboard!")
        print("Check your clipboard or the Share dialog for the link.")
        print("Browser will stay open. Close manually when done.")
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    try:
        upload_to_google_drive()
    except Exception as e:
        print(f"Error: {e}")
        print("Please try manual upload instead.")
        input("Press Enter to exit...")
