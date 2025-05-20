import os
import yt_dlp
import eyed3
import json
import ffmpeg

def tag_mp3(mp3_path, metadata_path):
    file = eyed3.load(mp3_path)
    if file.tag is None:
        file.initTag()

    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    file.tag.title = data.get('title')
    file.tag.artist = data.get('uploader')
    file.tag.album = data.get('album') or "YouTube"
    file.tag.genre = "YouTube"

    if data.get('track_number'):
        file.tag.track_num = data['track_number']
    if data.get('upload_date'):
        year = data['upload_date'][:4]
        file.tag.recording_date = eyed3.core.Date(int(year))

    file.tag.save()


def download_and_tag_youtube(urls, output_dir="downloads"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts_eta = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'forcejson': True,
        'simulate': True,
    }

    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    for url in urls:
        try:
            print(f"getting metadata: {url}")
            with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title", "unknown")
            mp3_name = f"{title}.mp3"
            json_name = f"{title}.json"

            json_path = os.path.join(output_dir, json_name)
            mp3_path = os.path.join(output_dir, mp3_name)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

            print(f"downloading audio: {title}")
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])

            tag_mp3(mp3_path, json_path)

        except Exception as e:
            print(f"fucked up with {url}: {e}")


if __name__ == "__main__":
    youtube_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        # something like that
    ]
    
    download_and_tag_youtube(youtube_urls)