import json

with open('files\ok.json', encoding="utf8") as f:
    data = json.load(f)

summary = {
    "title": data.get('title'),
    "artist": data.get('uploader'),
    "duration": f"{(int(data.get('duration')) / 60):.2f}",
    "release_data": f"{data.get('upload_date')[0:4]}-{data.get('upload_date')[4:6]}-{data.get('upload_date')[6:]}"
}

print(summary)