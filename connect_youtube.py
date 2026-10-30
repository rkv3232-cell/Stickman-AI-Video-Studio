"""
1-Click YouTube Channel Authorization Tool for Stickman AI Video Studio.
Guides user to connect their YouTube channel securely using Google OAuth 2.0.
"""

import sys
import json
import webbrowser
from pathlib import Path

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure root dir on sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import ROOT_DIR, CHANNEL_NAME
from src.youtube_uploader import youtube_uploader, CLIENT_SECRETS_FILE, TOKEN_FILE
from src.database import set_setting

def print_setup_guide():
    print("\n" + "=" * 70)
    print("🔑 YOUTUBE OAUTH SETUP GUIDE (Required Once Only)")
    print("=" * 70)
    print("Google/YouTube requires an OAuth 2.0 Client credentials file to allow")
    print("automated uploading without sharing your Google password.\n")
    print("Follow these 3 simple steps (Takes ~2 minutes):")
    print("-" * 70)
    print("STEP 1: Open Google Cloud Console")
    print("  👉 https://console.cloud.google.com/")
    print("  - Create a new project (e.g. 'My YouTube Studio') or select existing.")
    print("\nSTEP 2: Enable 'YouTube Data API v3'")
    print("  👉 Go to 'APIs & Services' -> 'Library'")
    print("  - Search for 'YouTube Data API v3' and click 'ENABLE'.")
    print("\nSTEP 3: Create OAuth Client ID & Download JSON")
    print("  👉 Go to 'APIs & Services' -> 'Credentials' -> 'Create Credentials' -> 'OAuth client ID'")
    print("  - Application Type choose: 'Desktop app' (or 'Web application')")
    print("  - Name: 'Stickman YouTube Studio'")
    print("  - Click 'CREATE' -> Then click 'DOWNLOAD JSON'.")
    print("-" * 70)
    print("STEP 4: Save the downloaded file into this project folder as:")
    print(f"  📁 {CLIENT_SECRETS_FILE}")
    print("-" * 70)
    print("After placing 'client_secrets.json', simply run this script again:")
    print("  python connect_youtube.py")
    print("=" * 70 + "\n")

def main():
    print("=" * 70)
    print(f"   {CHANNEL_NAME} — YOUTUBE CHANNEL CONNECT WIZARD")
    print("=" * 70)

    # 1. Check if already authenticated
    if youtube_uploader.is_authenticated():
        info = youtube_uploader.get_channel_info()
        print("\n✅ YouTube Channel is ALREADY CONNECTED!")
        print(f"   📺 Channel Name: {info.get('channel_name')}")
        print(f"   👥 Subscribers:  {info.get('subscribers'):,}")
        print(f"   🎥 Total Videos: {info.get('video_count'):,}")
        print(f"   👁️ Total Views:  {info.get('total_views'):,}")
        print("\nYour automated publishing pipeline is active and ready to upload videos!")
        return

    # 2. Check if client_secrets.json exists
    if not CLIENT_SECRETS_FILE.exists():
        print(f"\n⚠️ 'client_secrets.json' file not found in project root:")
        print(f"   Missing at: {CLIENT_SECRETS_FILE}")
        print_setup_guide()
        return

    # 3. Launch interactive authorization
    print("\n🌐 Opening Google Authorization in your default browser...")
    print("Please select your Google Account and click 'Allow' to grant YouTube upload permissions.")
    print("(Note: If Google displays 'Google hasn't verified this app', click 'Advanced' -> 'Go to Stickman YouTube Studio (unsafe)' to proceed.)\n")

    success, msg = youtube_uploader.authenticate_interactive()
    if success:
        info = youtube_uploader.get_channel_info()
        print("\n" + "=" * 70)
        print("🎉 YOUTUBE CHANNEL SUCCESSFULLY CONNECTED!")
        print("=" * 70)
        print(f"   📺 Channel Name: {info.get('channel_name')}")
        print(f"   👥 Subscribers:  {info.get('subscribers'):,}")
        print(f"   🎥 Total Videos: {info.get('video_count'):,}")
        print(f"   🔗 Status:       {info.get('status')}")
        print("=" * 70)
        # Update settings in DB
        set_setting("youtube_channel_title", info.get("channel_name", ""))
        set_setting("youtube_channel_id", info.get("channel_id", ""))
    else:
        print(f"\n❌ Connection failed: {msg}")
        print("Please check your client_secrets.json file and try again.")

if __name__ == "__main__":
    main()
