import os
import yt_dlp
import json
import librosa
import numpy as np
import pandas as pd
import time
from yt_dlp import YoutubeDL

# === CONFIG ===
CSV_FILE = './msd_subset_summary.csv'  # Source of titles, artists, years
OUTPUT_DIR = 'downloads'  # Folder to save WAV and JSON
FAILED_LOG = 'failed_queries.json'
LAST_INDEX_FILE = 'last_index.txt'
os.makedirs(OUTPUT_DIR, exist_ok=True)

max_duration_sec = 600
REQUEST_DELAY_SEC = 2.5  # delay between downloads to avoid rate limiting

# === Load Queries from CSV ===
df_csv = pd.read_csv(CSV_FILE)
df_csv = df_csv.dropna(subset=['title', 'artist', 'year'])
df_csv["query"] = df_csv["artist"] + " - " + df_csv["title"]
df_csv["safe_title"] = df_csv["query"].str.replace("/", "-").str.replace(":", "-").str.replace("?", "").str.replace("\\", "").str.replace("*", "").str.replace("\"", "").str.strip()

# === Feature Extraction Function ===
def extract_audio_features(filepath):
    y, sr = librosa.load(filepath, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1)
    return float(np.squeeze(tempo)), chroma, mfcc

# === Main ===
all_metadata = []
failed_queries = []

# Resume support
start_index = 0
if os.path.exists(LAST_INDEX_FILE):
    with open(LAST_INDEX_FILE, 'r') as f:
        start_index = int(f.read().strip())

if __name__ == "__main__":
    for idx, row in df_csv.iloc[start_index:].iterrows():
        query = row["query"]
        safe_title = row["safe_title"]
        year = int(row["year"])
        filepath = os.path.join(OUTPUT_DIR, f"{safe_title}.wav")

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(OUTPUT_DIR, f"{safe_title}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'default_search': 'ytsearch1',
            'match_filter': lambda info: (
                "reject" if info.get("duration", 0) > max_duration_sec else None
            ),
            'cookiefile': 'cookies.txt'
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)

            upload_date = info.get("upload_date")
            upload_year = int(upload_date[:4]) if upload_date else None

            # Extract features
            tempo, chroma, mfcc = extract_audio_features(filepath)

            metadata = {
                "query": query,
                "artist": row["artist"],
                "title": row["title"],
                "original_year": year,
                "upload_year": upload_year,
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "like_count": info.get("like_count"),
                "tempo_bpm": tempo,
                "estimated_key": None,
                "chroma_mean": chroma.tolist(),
                "mfcc_mean": mfcc.tolist(),
                "filepath": filepath
            }

            # Save metadata JSON
            json_path = os.path.join(OUTPUT_DIR, f"{safe_title}.json")
            with open(json_path, "w") as jf:
                json.dump(metadata, jf, indent=2)

            print(f"Downloaded and processed: {metadata['title']}")
            all_metadata.append(metadata)

            # Save index
            with open(LAST_INDEX_FILE, 'w') as f:
                f.write(str(start_index + idx + 1))

            # Optionally delete WAV
            os.remove(filepath)

            time.sleep(REQUEST_DELAY_SEC)  # Delay to avoid rate limiting

        except Exception as e:
            print(f"Failed for: {query} — {e}")
            failed_queries.append(query)
            time.sleep(REQUEST_DELAY_SEC)  # Delay on failure too

    # Save batch metadata
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w") as f:
        json.dump(all_metadata, f, indent=2)

    # Save failed queries
    with open(FAILED_LOG, "w") as f:
        json.dump(failed_queries, f, indent=2)

    print(f"Saved metadata for {len(all_metadata)} tracks.")
