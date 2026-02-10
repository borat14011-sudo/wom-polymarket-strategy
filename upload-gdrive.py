from playwright.sync_api import sync_playwright
import time

def upload_files():
    print("Google Drive automation - uploading files...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1400, 'height': 900})
        page = context.new_page()
        
        # Go to Google Drive
        print("Opening Google Drive...")
        page.goto('https://drive.google.com/drive/my-drive')
        page.wait_for_timeout(3000)
        
        # Create folder using keyboard shortcut or menu
        print("Creating folder 'Trading-Strategy-Presentation'...")
        
        # Try to find and click the main "New" button (usually top left)
        try:
            # Look for the specific New button with the plus icon
            new_button = page.locator('button:has([aria-label="New"]), [role="button"]:has([data-tooltip="New"])').first
            new_button.click()
        except:
            # Alternative: use keyboard shortcut
            page.keyboard.press('c')
        
        page.wait_for_timeout(1500)
        
        # Click Folder option
        try:
            page.click('text=Folder', timeout=5000)
        except:
            # Try alternative selector
            page.locator('div:has-text("Folder"):not(:has(*))').first.click()
        
        page.wait_for_timeout(1000)
        
        # Type folder name
        page.keyboard.type('Trading-Strategy-Presentation')
        page.wait_for_timeout(500)
        page.keyboard.press('Enter')
        page.wait_for_timeout(2000)
        
        print("Folder created! Navigating into it...")
        
        # Double click to open folder
        page.dblclick('text=Trading-Strategy-Presentation')
        page.wait_for_timeout(2000)
        
        # Upload files
        files_to_upload = [
            r"C:\Users\Borat\.openclaw\workspace\netlify-deploy\index.html",
            r"C:\Users\Borat\.openclaw\workspace\PROFESSIONAL_STRATEGY_PRESENTATION.md"
        ]
        
        for file_path in files_to_upload:
            print(f"Uploading: {file_path.split('\\')[-1]}...")
            
            # Click New
            try:
                new_button = page.locator('button:has([aria-label="New"]), [role="button"]:has([data-tooltip="New"])').first
                new_button.click()
            except:
                page.keyboard.press('c')
            
            page.wait_for_timeout(1000)
            
            # Click File upload
            page.click('text=File upload')
            page.wait_for_timeout(1000)
            
            # Handle file chooser
            try:
                with page.expect_file_chooser(timeout=10000) as fc_info:
                    pass
                file_chooser = fc_info.value
                file_chooser.set_files(file_path)
            except:
                # Manual file dialog will appear - user needs to select
                print(f"Please select file: {file_path}")
                print("Waiting 10 seconds for you to select file...")
                page.wait_for_timeout(10000)
            
            page.wait_for_timeout(3000)
            print(f"Uploaded!")
        
        print("All files uploaded!")
        print("Right-click the folder to get shareable link.")
        print("Browser stays open.")
        
        while True:
            time.sleep(1)

if __name__ == "__main__":
    try:
        upload_files()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
