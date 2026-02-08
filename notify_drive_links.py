#!/usr/bin/env python3
"""
Telegram Notification Service for Google Drive Uploads
Sends notifications with file links when uploads are completed
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

try:
    from telegram import Bot, InputFile
    from telegram.constants import ParseMode
    from telegram.error import TelegramError
except ImportError:
    print("⚠️  python-telegram-bot not installed. Install with: pip install python-telegram-bot")
    print("⚠️  Telegram notifications will be disabled.")
    Bot = None
    InputFile = None
    ParseMode = None
    TelegramError = Exception

# Load environment variables
load_dotenv()

class TelegramNotifier:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """Initialize Telegram notifier with bot token and chat ID."""
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("Telegram bot token not provided or found in TELEGRAM_BOT_TOKEN environment variable")
        
        if not self.chat_id:
            raise ValueError("Telegram chat ID not provided or found in TELEGRAM_CHAT_ID environment variable")
        
        if Bot is None:
            raise ImportError("python-telegram-bot package is required for Telegram notifications")
        
        self.bot = Bot(token=self.bot_token)
        self.chat_id = int(self.chat_id) if self.chat_id.isdigit() else self.chat_id
    
    async def send_message(self, message: str, parse_mode: str = ParseMode.HTML) -> bool:
        """
        Send a text message to Telegram.
        
        Args:
            message: Message text to send
            parse_mode: Parse mode for message formatting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            return True
        except TelegramError as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    async def send_file_with_link(self, file_name: str, drive_link: str, file_size: Optional[int] = None, 
                                folder_name: Optional[str] = None, upload_time: Optional[datetime] = None) -> bool:
        """
        Send a notification about an uploaded file with Drive link.
        
        Args:
            file_name: Name of the uploaded file
            drive_link: Google Drive shareable link
            file_size: File size in bytes (optional)
            folder_name: Drive folder name (optional)
            upload_time: Upload timestamp (optional)
            
        Returns:
            True if successful, False otherwise
        """
        # Format the message
        timestamp = upload_time.strftime("%Y-%m-%d %H:%M:%S") if upload_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        size_str = self._format_size(file_size) if file_size else "Unknown size"
        
        message = f"""
📤 <b>File Uploaded Successfully!</b>

📄 <b>File:</b> {file_name}
📏 <b>Size:</b> {size_str}
📅 <b>Time:</b> {timestamp}
"""
        
        if folder_name:
            message += f"📁 <b>Folder:</b> {folder_name}\n"
        
        message += f"""
🔗 <b>Download Link:</b>
<a href="{drive_link}">📥 Click here to download</a>

<i>File is publicly accessible via the link above.</i>
"""
        
        return await self.send_message(message)
    
    async def send_bulk_upload_notification(self, files: List[dict], folder_name: Optional[str] = None) -> bool:
        """
        Send notification for multiple uploaded files.
        
        Args:
            files: List of dicts with 'name', 'link', 'size' keys
            folder_name: Drive folder name (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not files:
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_files = len(files)
        total_size = sum(file.get('size', 0) for file in files)
        
        message = f"""
📁 <b>Bulk Upload Completed!</b>

📊 <b>Summary:</b>
• Total files: {total_files}
• Total size: {self._format_size(total_size)}
• Time: {timestamp}
"""
        
        if folder_name:
            message += f"• Folder: {folder_name}\n"
        
        message += "\n📄 <b>Files:</b>\n"
        
        # Add file list (limit to first 10 files to avoid message length limits)
        for i, file in enumerate(files[:10]):
            file_name = file.get('name', 'Unknown')
            file_link = file.get('link', '')
            message += f"{i+1}. <a href='{file_link}'>{file_name}</a>\n"
        
        if len(files) > 10:
            message += f"... and {len(files) - 10} more files\n"
        
        message += "\n<i>All files are publicly accessible via their links.</i>"
        
        return await self.send_message(message)
    
    async def send_error_notification(self, error_message: str, file_name: Optional[str] = None) -> bool:
        """
        Send error notification when upload fails.
        
        Args:
            error_message: Error description
            file_name: File that failed to upload (optional)
            
        Returns:
            True if successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
❌ <b>Upload Failed!</b>

📅 <b>Time:</b> {timestamp}
"""
        
        if file_name:
            message += f"📄 <b>File:</b> {file_name}\n"
        
        message += f"""
❗ <b>Error:</b>
{error_message}

<i>Please check the logs and try again.</i>
"""
        
        return await self.send_message(message)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"


# Convenience functions for synchronous usage
def notify_upload(file_name: str, drive_link: str, file_size: Optional[int] = None, 
                 folder_name: Optional[str] = None, chat_id: Optional[str] = None) -> bool:
    """
    Send notification about a single uploaded file (synchronous wrapper).
    
    Args:
        file_name: Name of the uploaded file
        drive_link: Google Drive shareable link
        file_size: File size in bytes (optional)
        folder_name: Drive folder name (optional)
        chat_id: Telegram chat ID (optional, uses env var if not provided)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        notifier = TelegramNotifier(chat_id=chat_id)
        return asyncio.run(notifier.send_file_with_link(file_name, drive_link, file_size, folder_name))
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {e}")
        return False


def notify_bulk_upload(files: List[dict], folder_name: Optional[str] = None, 
                      chat_id: Optional[str] = None) -> bool:
    """
    Send notification for multiple uploaded files (synchronous wrapper).
    
    Args:
        files: List of dicts with 'name', 'link', 'size' keys
        folder_name: Drive folder name (optional)
        chat_id: Telegram chat ID (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        notifier = TelegramNotifier(chat_id=chat_id)
        return asyncio.run(notifier.send_bulk_upload_notification(files, folder_name))
    except Exception as e:
        print(f"❌ Failed to send bulk notification: {e}")
        return False


def notify_error(error_message: str, file_name: Optional[str] = None, 
                chat_id: Optional[str] = None) -> bool:
    """
    Send error notification (synchronous wrapper).
    
    Args:
        error_message: Error description
        file_name: File that failed to upload (optional)
        chat_id: Telegram chat ID (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        notifier = TelegramNotifier(chat_id=chat_id)
        return asyncio.run(notifier.send_error_notification(error_message, file_name))
    except Exception as e:
        print(f"❌ Failed to send error notification: {e}")
        return False


def main():
    """Test the Telegram notifier."""
    print("🧪 Testing Telegram Notifier...")
    
    # Test single file notification
    print("\n1. Testing single file notification...")
    success = notify_upload(
        file_name="test_document.pdf",
        drive_link="https://drive.google.com/file/d/123456789/view",
        file_size=1024 * 1024,  # 1 MB
        folder_name="Test Uploads"
    )
    
    if success:
        print("✅ Single file notification sent successfully!")
    else:
        print("❌ Failed to send single file notification")
    
    # Test bulk notification
    print("\n2. Testing bulk upload notification...")
    test_files = [
        {'name': 'file1.txt', 'link': 'https://drive.google.com/file/d/1/view', 'size': 1024},
        {'name': 'file2.jpg', 'link': 'https://drive.google.com/file/d/2/view', 'size': 2048},
        {'name': 'file3.pdf', 'link': 'https://drive.google.com/file/d/3/view', 'size': 4096}
    ]
    
    success = notify_bulk_upload(test_files, folder_name="Test Batch")
    
    if success:
        print("✅ Bulk notification sent successfully!")
    else:
        print("❌ Failed to send bulk notification")
    
    # Test error notification
    print("\n3. Testing error notification...")
    success = notify_error(
        error_message="Network timeout occurred while uploading",
        file_name="large_file.zip"
    )
    
    if success:
        print("✅ Error notification sent successfully!")
    else:
        print("❌ Failed to send error notification")


if __name__ == '__main__':
    # Check if required environment variables are set
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("⚠️  Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        print("💡 You can also pass them directly to the functions")
        print("\nExample:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("export TELEGRAM_CHAT_ID='your_chat_id'")
    else:
        main()