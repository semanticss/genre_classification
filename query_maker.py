import json
from subprocess import run

with open('./classical_artists_with_eras.json', 'r') as j:
    contents = json.loads(j.read())

    querys = []
    for artist, details in contents.items():
        # print(artist)
        works = details['works']
        for song in works:
            query_profile = {
                'query': f"{song['title']} {artist}",
                'title': song['title'],
                'artist': artist
                }
            querys.append(query_profile)
    
    with open("./classical_queries", "w") as f:
        json.dump(querys, f, indent=4, ensure_ascii=False)
