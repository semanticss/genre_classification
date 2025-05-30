import os
import librosa
import json
import numpy as np

input_dir = "downloads"
output_dir = "librosa_feature_outputs"
os.makedirs(output_dir, exist_ok=True)

def extract_librosa_features(filepath):
    y, sr = librosa.load(filepath, sr=44100)

    # Tempo (BPM)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # Chroma (12 pitch classes, averaged)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1).tolist()

    # Key estimation: pick the pitch class with highest energy
    pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                     'F#', 'G', 'G#', 'A', 'A#', 'B']
    max_index = int(np.argmax(chroma_mean))
    estimated_key = pitch_classes[max_index]

    # Beat positions (in seconds)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    # Optional: MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = mfcc.mean(axis=1).tolist()

    features = {
        "tempo_bpm": float(tempo),
        "estimated_key": estimated_key,
        "chroma_mean": chroma_mean,
        "beat_times_sec": beat_times,
        "mfcc_mean": mfcc_mean
    }

    return features

# Process all WAV files
for filename in os.listdir(input_dir):
    if filename.endswith(".wav"):
        filepath = os.path.join(input_dir, filename)
        try:
            print(f"processing: {filename}")
            features = extract_librosa_features(filepath)

            out_name = os.path.splitext(filename)[0] + ".json"
            out_path = os.path.join(output_dir, out_name)

            with open(out_path, "w") as f:
                json.dump(features, f, indent=2)

            print(f"saved features to: {out_path}")
        except Exception as e:
            print(f"error processing {filename}: {e}")