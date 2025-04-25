#!/bin/bash

WATCH_DIR="/var/www/band.fccsv.com/audio"
LOG_FILE="/var/log/monitor_audio.log"
LOCK_DIR="/tmp/audio_processing_locks"
QUEUE_FILE="/tmp/folder_watch_queue.txt"
WAIT_TIME=300  # 5 minutes
RSS_SCRIPT="/usr/local/bin/PodcastFeedGen.py --all"
CLEAN_SCRIPT="/usr/local/bin/cleanMP3.py"
INDEX_FILE="/var/www/band.fccsv.com/index.html"

mkdir -p "$LOCK_DIR"
touch "$QUEUE_FILE"

log() {
    echo "$(date): $1" >> "$LOG_FILE"
}

# Background processor loop
process_queue() {
    while true; do
        sleep 10  # check every 10 seconds

        now=$(date +%s)
        mapfile -t lines < "$QUEUE_FILE"
        > "$QUEUE_FILE"

        for line in "${lines[@]}"; do
            IFS='|' read -r folder timestamp <<< "$line"
            [[ -z "$folder" ]] && continue

            age=$((now - timestamp))
            if (( age < WAIT_TIME )); then
                echo "$folder|$timestamp" >> "$QUEUE_FILE"  # not ready yet, requeue
                continue
            fi

            basename=$(basename "$folder")
            lock="$LOCK_DIR/$basename.lock"
            if mkdir "$lock" 2>/dev/null; then
                log "Processing folder $folder"
                python3 "$CLEAN_SCRIPT"
                python3 $RSS_SCRIPT

                # rebuild index.html
                tmp_index="/tmp/index.$$.html"
                cat <<EOF > "$tmp_index"
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Worship Practice Recordings</title></head>
<body><h1>Worship Practice Recordings</h1><ul>
EOF

                for dir in "$WATCH_DIR"/practice-*; do
                    [ -d "$dir" ] || continue
                    date_str=$(basename "$dir" | sed 's/practice-//')
                    echo "  <li><a href=\"audio/practice-$date_str/\">Practice $date_str</a></li>" >> "$tmp_index"
                done

                cat <<EOF >> "$tmp_index"
</ul><p><a href="rss_feed.xml">Podcast RSS Feed</a></p></body></html>
EOF

                mv "$tmp_index" "$INDEX_FILE"
                chown www-data:www-data "$INDEX_FILE"
                chmod 644 "$INDEX_FILE"

                log "Finished processing $folder"
                rm -rf "$lock"
            else
                log "Skip $folder (already locked)"
            fi
        done
    done
}

# Start background processor
process_queue &

# Watcher loop
inotifywait -m -r -e close_write --format "%w %f" "$WATCH_DIR" | while read dir file; do
    [[ "$file" == *.mp3 ]] || continue
    folder="${dir%/}"

    # Avoid spamming queue: only add new folder timestamp
    grep -q "^$folder|" "$QUEUE_FILE" || echo "$folder|$(date +%s)" >> "$QUEUE_FILE"
    log "Queued $file in $folder"
done
