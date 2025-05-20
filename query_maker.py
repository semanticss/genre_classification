import json

with open('./classical_artists_with_eras.json', 'r') as j:
    contents = json.loads(j.read())

    for artist, details in contents.items():
        works = details['works']
        for song in works:
            print(song)
