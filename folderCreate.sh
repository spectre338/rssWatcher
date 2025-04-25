#!/bin/bash

LOG_FILE="/var/log/monitor_audio.log"
echo "$(date): folderCreate.sh started" >> "$LOG_FILE"

WATCH_DIR="/var/www/band.fccsv.com/audio"
OWNER="ftpfccsv"
GROUP="audioaccess"

# Create folders for the next two Fridays in UTC
for i in 1 2; do
    folder_date_utc=$(date -u -d "next Friday +$(( (i-1)*7 )) days" +%F)
    folder_path="$WATCH_DIR/practice-$folder_date_utc"

    if [ ! -d "$folder_path" ]; then
        echo "$(date): Creating folder $folder_path" >> "$LOG_FILE"
        mkdir -p "$folder_path"
        chown "$OWNER:$GROUP" "$folder_path"
        chmod 2775 "$folder_path"
    else
        echo "$(date): Folder $folder_path already exists, no action taken" >> "$LOG_FILE"
    fi
done
