import os
import requests
import re

# --- কনফিগারেশন ---
FILE_PATH = "audio/hq-quality.m3u"
FOLDER_ID = "1TW4p81uwcOMlY_YSZAej-f0NaZIa6wTb"
DEFAULT_LOGO = "https://i.ibb.co.com/v4wpmy1X/In-Shot-20260718-152636973.jpg"

def get_drive_files():
    """ড্রাইভ ফোল্ডার থেকে ফাইল স্ক্র্যাপ করবে"""
    url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
    try:
        response = requests.get(url)
        html = response.text
        
        # Regex দিয়ে আইডি এবং নাম বের করা
        pattern = r'\["([a-zA-Z0-9_-]{25,35})","([^"]+\.(?:flac|mp3|m4a|wav|ogg))"'
        matches = re.findall(pattern, html)
        
        drive_files = []
        seen = set()
        for file_id, filename in matches:
            if file_id not in seen:
                drive_files.append({"id": file_id, "name": filename})
                seen.add(file_id)
        return drive_files
    except Exception as e:
        print(f"Scraping Error: {e}")
        return []

def clean_and_update_m3u():
    # ফাইল আগে থেকে থাকলে সেটা পড়া
    existing_lines = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            existing_lines = f.read().strip().splitlines()

    # বর্তমান ডেটা থেকে ডুপ্লিকেট রিমুভ করে ফ্রেশ লিস্ট তৈরি করা
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

    # ড্রাইভ থেকে নতুন গান চেক করা
    print("Scraping Drive...")
    drive_files = get_drive_files()
    
    new_added = 0
    for file in drive_files:
        raw_link = f"https://drive.google.com/uc?export=download&id={file['id']}"
        
        # যদি লিংকটি আগে না থাকে, তবেই যোগ করবে
        if raw_link not in unique_links:
            title = os.path.splitext(file['name'])[0].strip()
            
            cleaned_m3u.append(f'#EXTINF:-1 tvg-logo="{DEFAULT_LOGO}",{title}')
            cleaned_m3u.append(raw_link)
            
            unique_links.add(raw_link)
            new_added += 1

    # নতুন আপডেট হওয়া কন্টেন্ট ফাইলে সেভ করা (ফোল্ডার না থাকলে তৈরি করে নেবে)
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_m3u) + "\n")
        
    print(f"Cleaned duplicates. Added {new_added} new songs.")

if __name__ == "__main__":
    clean_and_update_m3u()
