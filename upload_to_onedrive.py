#!/usr/bin/env python3
"""
OneDrive Upload Script
Uploads the Tariff Investment Thesis to OneDrive
"""

import os

FILE_TO_UPLOAD = "tariff_investment_thesis.md"

def find_onedrive_folder():
    """Find OneDrive folder location"""
    possible_paths = [
        os.path.expanduser("~/OneDrive"),
        os.path.expanduser("~/OneDrive - Personal"),
        "C:/Users/Borat/OneDrive",
        "C:/Users/Borat/OneDrive - Personal",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def upload_to_onedrive():
    """Copy file to OneDrive folder"""
    
    # Check if file exists
    if not os.path.exists(FILE_TO_UPLOAD):
        print(f"ERROR: File not found: {FILE_TO_UPLOAD}")
        print("Please ensure the file exists in the current directory")
        return False
    
    # Find OneDrive folder
    onedrive_folder = find_onedrive_folder()
    
    if not onedrive_folder:
        print("ERROR: OneDrive folder not found")
        print("\nTrying to locate OneDrive...")
        
        # Try to find via common locations
        home = os.path.expanduser("~")
        for item in os.listdir(home):
            if "onedrive" in item.lower():
                print(f"  Found: {item}")
        
        return False
    
    print(f"[OK] Found OneDrive at: {onedrive_folder}")
    
    # Create Trading folder if it doesn't exist
    trading_folder = os.path.join(onedrive_folder, "Trading")
    if not os.path.exists(trading_folder):
        print(f"Creating Trading folder...")
        os.makedirs(trading_folder)
    
    # Copy file
    destination = os.path.join(trading_folder, FILE_TO_UPLOAD)
    
    try:
        # Read and write to ensure content is copied
        with open(FILE_TO_UPLOAD, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(destination, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"SUCCESS: File uploaded!")
        print(f"Location: {destination}")
        print(f"File size: {os.path.getsize(destination):,} bytes")
        
        print("\nNOTE: The file is saved as Markdown (.md)")
        print("   OneDrive will sync it automatically")
        
        return True
        
    except Exception as e:
        print(f"ERROR uploading: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OneDrive Upload - Tariff Investment Thesis")
    print("=" * 60)
    print()
    
    success = upload_to_onedrive()
    
    if not success:
        print("\n" + "=" * 60)
        print("MANUAL UPLOAD REQUIRED")
        print("=" * 60)
        print()
        print("Please manually copy the file:")
        print(f"  Source: {os.path.abspath(FILE_TO_UPLOAD)}")
        print("  Destination: Your OneDrive/Trading folder")
        print()
        print("The file is ready at:")
        print(f"  {os.path.abspath(FILE_TO_UPLOAD)}")
