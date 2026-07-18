import os
import requests

# --- কনফিগারেশন ---
FILE_PATH = "audio/hq-quality.m3u"
FOLDER_ID = "1TW4p81uwcOMlY_YSZAej-f0NaZIa6wTb"
DEFAULT_LOGO = "https://i.ibb.co.com/v4wpmy1X/In-Shot-20260718-152636973.jpg"
API_KEY = os.environ.get("GDRIVE_API_KEY")

def get_drive_files():
    """Google Drive API ব্যবহার করে নির্ভুলভাবে ফাইল লিস্ট আনবে"""
    url = f"https://www.googleapis.com/drive/v3/files?q='{FOLDER_ID}'+in+parents+and+trashed=false&fields=files(id,name)&key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return []
            
        data = response.json()
        return data.get('files', [])
    except Exception as e:
        print(f"Error fetching files: {e}")
        return []

def clean_and_update_m3u():
    existing_lines = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            existing_lines = f.read().strip().splitlines()

    unique_links = set()
    cleaned_m3u = ["#EXTM3U"]
    
    # বর্তমান ফাইলের গানগুলো প্রসেস করা (ডুপ্লিকেট বাদ দিয়ে)
    i = 1
    while i < len(existing_lines):
        line = existing_lines[i]
        if line.startswith("#EXTINF"):
            if i + 1 < len(existing_lines):
                link = existing_lines[i+1]
                if link not in unique_links and link.startswith("http"):
                    unique_links.add(link)
                    cleaned_m3u.append(line)
                    cleaned_m3u.append(link)
                i += 2
                continue
        i += 1

    print("Fetching new songs from Drive API...")
    drive_files = get_drive_files()
    
    new_added = 0
    for file in drive_files:
        # শুধু অডিও ফাইলগুলো ফিল্টার করা
        filename = file['name']
        if not filename.lower().endswith(('.flac', '.mp3', '.m4a', '.wav')):
            continue
            
        raw_link = f"https://drive.google.com/uc?export=download&id={file['id']}"
        
        if raw_link not in unique_links:
            title = os.path.splitext(filename)[0].strip()
            
            cleaned_m3u.append(f'#EXTINF:-1 tvg-logo="{DEFAULT_LOGO}",{title}')
            cleaned_m3u.append(raw_link)
            
            unique_links.add(raw_link)
            new_added += 1

    # নতুন আপডেট হওয়া কন্টেন্ট ফাইলে সেভ করা
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_m3u) + "\n")
        
    print(f"Cleaned duplicates. Added {new_added} new songs.")

if __name__ == "__main__":
    if not API_KEY:
        print("Error: GDRIVE_API_KEY is not set in secrets!")
    else:
        clean_and_update_m3u()
