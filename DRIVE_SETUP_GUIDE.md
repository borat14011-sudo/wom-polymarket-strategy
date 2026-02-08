# Google Drive Uploader Setup Guide

This guide will walk you through setting up the Google Drive Uploader with OAuth authentication.

## Prerequisites

- Python 3.7 or higher
- Google account
- Basic knowledge of command line/terminal

## Step 1: Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "Drive Uploader") and click "Create"
4. Wait for project creation, then select your new project
5. In the sidebar, go to "APIs & Services" → "Library"
6. Search for "Google Drive API" and click on it
7. Click "Enable" to enable the API for your project

## Step 2: Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" for user type
   - Fill in app name (e.g., "Drive Uploader")
   - Add your email as user support email
   - Add your email as developer contact
   - Add scope: `https://www.googleapis.com/auth/drive.file`
   - Add test user (your email)
4. For Application type, choose "Desktop app"
5. Enter a name (e.g., "Drive Uploader Client")
6. Click "Create"
7. Click "Download JSON" to download your credentials
8. **IMPORTANT**: Rename the downloaded file to `credentials.json` and place it in the same folder as the scripts

## Step 3: Install Dependencies

1. Open terminal/command prompt
2. Navigate to the folder containing the scripts
3. Install required packages:

```bash
pip install -r requirements.txt
```

## Step 4: First Time Authentication

1. Run the uploader script:

```bash
python drive_uploader.py
```

2. On first run, your browser will open with Google login
3. Sign in with your Google account
4. Click "Allow" to grant permissions
5. You'll be redirected to a success page
6. Close the browser tab
7. A `token.pickle` file will be created automatically

**Note**: The token is valid for long-term use. You won't need to authenticate again unless you revoke access.

## Step 5: Test Upload

Create a test file and upload it:

```python
from drive_uploader import DriveUploader

# Initialize uploader
uploader = DriveUploader()

# Upload a file
file_info = uploader.upload_file('test_file.txt')
print(f"File uploaded: {file_info['webViewLink']}")
```

## Usage Examples

### Upload Single File
```python
from drive_uploader import DriveUploader

uploader = DriveUploader()
uploader.upload_file('document.pdf')
```

### Upload to Specific Folder
```python
# First create a folder
folder = uploader.create_folder('My Uploads')
folder_id = folder['id']

# Then upload to that folder
uploader.upload_file('photo.jpg', folder_id=folder_id)
```

### Upload Entire Folder
```python
uploader.upload_folder('/path/to/local/folder')
```

### List Files
```python
files = uploader.list_files()
for file in files:
    print(f"{file['name']} - {file['id']}")
```

## Telegram Integration

To receive Telegram notifications when files are uploaded:

1. Create a Telegram bot using [@BotFather](https://t.me/botfather)
2. Get your bot token and chat ID
3. Set environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

4. Use the notification script:

```python
from notify_drive_links import notify_upload

notify_upload("document.pdf", "https://drive.google.com/file/d/ABC123/view")
```

## Troubleshooting

### Common Issues

**Q: `credentials.json` not found error**
A: Make sure you downloaded and renamed the credentials file correctly. It should be named exactly `credentials.json` in the same folder as the scripts.

**Q: Authentication fails or browser doesn't open**
A: 
- Check your internet connection
- Ensure you're using the correct Google account
- Try clearing browser cache/cookies
- Check if any firewall is blocking localhost connections

**Q: Upload fails with "Insufficient permissions"**
A: Make sure you enabled the Google Drive API and the OAuth consent screen is properly configured.

**Q: Token expires frequently**
A: The token should last for a long time. If it keeps expiring, check if you're using the correct scopes and your app is in production mode (not testing).

**Q: Large files fail to upload**
A: For files larger than 5MB, the uploader automatically uses resumable uploads. If it still fails, check your internet connection stability.

### Security Notes

- Never share your `credentials.json` or `token.pickle` files
- Store these files securely and don't commit them to version control
- Use `.gitignore` to exclude these files:

```
credentials.json
token.pickle
__pycache__/
*.pyc
```

### Getting Help

1. Check the error messages carefully - they often contain the solution
2. Verify all setup steps were completed
3. Ensure your Google Cloud project is properly configured
4. Check the [Google Drive API documentation](https://developers.google.com/drive/api/v3/about-sdk)

## Next Steps

- Customize the uploader for your specific needs
- Set up automated uploads with cron jobs
- Integrate with other applications
- Add error handling and logging as needed

---

**Happy uploading! 🚀**