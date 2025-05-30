import os
import glob
import hdf5_getters as GETTERS
import pandas as pd

subset_path = "C:/Users/huds0/Downloads/millionsongsubset"  # adjust if needed
records = []

file_paths = glob.glob(f"{subset_path}/**/*.h5", recursive=True)
print(f"Found {len(file_paths)} files.")

for h5_path in file_paths:
    try:
        h5 = GETTERS.open_h5_file_read(h5_path)

        # safely decode only if bytes
        def safe_decode(val):
            return val.decode("utf-8") if isinstance(val, bytes) else val

        title = safe_decode(GETTERS.get_title(h5))
        artist = safe_decode(GETTERS.get_artist_name(h5))
        year = GETTERS.get_year(h5)
        tempo = GETTERS.get_tempo(h5)
        duration = GETTERS.get_duration(h5)
        key = GETTERS.get_key(h5)
        mode = GETTERS.get_mode(h5)
        loudness = GETTERS.get_loudness(h5)
        song_id = safe_decode(GETTERS.get_song_id(h5))

        records.append({
            "song_id": song_id,
            "title": title,
            "artist": artist,
            "year": year,
            "tempo": tempo,
            "duration": duration,
            "key": key,
            "mode": mode,
            "loudness": loudness
        })

        h5.close()

    except Exception as e:
        print(f"❌ Error reading {h5_path}: {e}")

# Build dataframe if successful
if records:
    df = pd.DataFrame(records)
    df = df[df["year"] > 0]
    df.to_csv("msd_subset_summary.csv", index=False)
    print(f"✅ Processed {len(df)} tracks. CSV saved.")
else:
    print("⚠️ No records were extracted.")
