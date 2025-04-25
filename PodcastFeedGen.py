#!/usr/bin/env python3

import os
import datetime
import xml.sax.saxutils as saxutils
import argparse

# Configuration Variables
BASE_URL = "https://band.fccsv.com"
AUDIO_DIRECTORY = "/var/www/band.fccsv.com/audio"
OUTPUT_FILE = "/var/www/band.fccsv.com/rss_feed.xml"  # Master RSS feed

def generate_master_rss_feed():
    """
    Generates a single RSS feed containing all practice recordings, sorted by date (newest first).
    """
    all_items = []

    # Iterate over all 'practice-*' folders, sorted by date (newest first)
    for folder in sorted(os.listdir(AUDIO_DIRECTORY), reverse=True):
        if folder.startswith('practice-'):
            practice_date = folder.replace('practice-', '')
            practice_path = os.path.join(AUDIO_DIRECTORY, folder)

            if not os.path.exists(practice_path):
                print(f"⚠️ Skipping missing directory: {practice_path}")
                continue

            try:
                audio_files = [f for f in sorted(os.listdir(practice_path), key=str.lower) if f.endswith('.mp3')]
            except OSError as e:
                print(f"❌ Error accessing '{practice_path}': {e}")
                continue

            if not audio_files:
                print(f"⚠️ No MP3 files in '{practice_path}', skipping.")
                continue

            for index, audio_file in enumerate(audio_files, start=1):
                file_path = os.path.join(practice_path, audio_file)
                try:
                    file_size = os.path.getsize(file_path)
                except OSError as e:
                    print(f"⚠️ Warning: Unable to read size of '{file_path}': {e}")
                    continue

                file_url = f"{BASE_URL}/audio/{folder}/{audio_file}"
                pub_date = datetime.datetime.strptime(practice_date, "%Y-%m-%d").strftime("%a, %d %b %Y %H:%M:%S GMT")

                all_items.append(f"""
        <item>
            <guid isPermaLink="true">{saxutils.escape(file_url)}</guid>
            <title>{saxutils.escape(audio_file)}</title>
            <link>{saxutils.escape(file_url)}</link>
            <description>Track from worship practice on {saxutils.escape(practice_date)}</description>
            <pubDate>{pub_date}</pubDate>
            <enclosure length="{file_size}" type="audio/mpeg" url="{saxutils.escape(file_url)}"/>
            <itunes:episode>{index}</itunes:episode>
        </item>
    """)

    if not all_items:
        print("❌ No valid practice recordings found. RSS feed not created.")
        return

    pub_date_now = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
    <channel>
        <title>Worship Practice Recordings</title>
        <link>{saxutils.escape(BASE_URL)}</link>
        <description>Complete archive of worship practice recordings</description>
        <pubDate>{pub_date_now}</pubDate>
        {''.join(all_items)}
    </channel>
</rss>
"""

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(rss_content)
        print(f"✅ Master RSS feed generated: {OUTPUT_FILE}")
    except OSError as e:
        print(f"❌ Error writing RSS file '{OUTPUT_FILE}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RSS feeds for worship practice.")
    parser.add_argument("--all", action="store_true", help="Reprocess all practice folders into a single RSS feed.")
    args = parser.parse_args()

    if args.all:
        generate_master_rss_feed()
