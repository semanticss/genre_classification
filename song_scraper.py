import os
import yt_dlp
import eyed3
import json
import ffmpeg
from subprocess import run
from yt_dlp import YoutubeDL

with open('./classical_queries', 'r') as j:
    contents = json.loads(j.read())

queries = [item['query'] for item in contents]

output_dir = "downloads"
os.makedirs(output_dir, exist_ok=True)

max_duration_sec = 600  # cap download length (e.g., 10 minutes)

# For collecting metadata
all_metadata = []

if __name__ == "__main__":
    
    for query in queries:

        safe_name = query.replace("/", "-").replace(":", "-")
        search_query = f"ytsearch1:{query}"

        safe_title = query.replace("/", "-").replace(":", "-")
        filename_template = f"{output_dir}/{safe_title}.%(ext)s"

        ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': filename_template,
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
        'extract_flat': False,
        'skip_download': False,
    }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)

            metadata = {
                "query": query,
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "upload_date": info.get("upload_date"),
                "like_count": info.get("like_count"),
                "filepath": f"{output_dir}/{safe_title}.wav"
            }
            all_metadata.append(metadata)

            print(f"downloaded: {metadata['title']}")

        except Exception as e:
            print(f"failed for: {query} — {e}")

with open(f"{output_dir}/metadata.json", "w") as f:
    json.dump(all_metadata, f, indent=2)

print(f"Metadata saved to {output_dir}/metadata.json")
