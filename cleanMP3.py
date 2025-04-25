import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, error

# Configuration Variables
AUDIO_DIRECTORY = "/var/www/band.fccsv.com/audio"  # Path to your practice audio files
DURATION_MIN_THRESHOLD = 45   # Minimum duration threshold in seconds
DURATION_MAX_THRESHOLD = 720  # Maximum duration threshold in seconds (12 minutes)
ARTIST_NAME = "FCCSV"

def delete_and_tag_mp3s():
    """
    Deletes MP3 files that are shorter than the minimum duration threshold
    or longer than the maximum duration threshold.
    Writes ID3 tags to valid files based on folder date.
    """
    for root, dirs, files in os.walk(AUDIO_DIRECTORY):
        for file in files:
            if file.endswith('.mp3'):
                file_path = os.path.join(root, file)
                try:
                    audio = MP3(file_path)
                    duration = audio.info.length
                    
                    # Delete files outside the duration range
                    if duration < DURATION_MIN_THRESHOLD or duration > DURATION_MAX_THRESHOLD:
                        os.remove(file_path)
                        print(f"Deleted: {file_path} (Duration: {duration:.2f} seconds)")
                    else:
                        # Extract date info from the folder name
                        folder_date = os.path.basename(root).replace("practice-", "")

                        # Initialize or update ID3 tags
                        try:
                            audio_tags = ID3(file_path)
                        except error:
                            audio_tags = ID3()  # Initialize empty ID3 tags if none exist

                        audio_tags.add(TIT2(encoding=3, text=file))  # Title
                        audio_tags.add(TPE1(encoding=3, text=ARTIST_NAME))  # Artist
                        audio_tags.add(TALB(encoding=3, text=f"Worship Practice {folder_date}"))  # Album
                        audio_tags.add(TDRC(encoding=3, text=folder_date))  # Recording date
                        audio_tags.save(file_path)
                        print(f"Tagged: {file_path} (Artist: {ARTIST_NAME}, Date: {folder_date})")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    delete_and_tag_mp3s()
