import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === CONFIG ===
JSON_DIR = "downloads"  # Folder with all the .json files
OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Load JSON files ===
data = []
for file in os.listdir(JSON_DIR):
    if file.endswith(".json") and file != "metadata.json":
        with open(os.path.join(JSON_DIR, file), "r") as f:
            try:
                record = json.load(f)
                data.append(record)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {file}")

# === Convert to DataFrame ===
df = pd.DataFrame(data)
df = df[df["original_year"].notna() & df["tempo_bpm"].notna()]
df["original_year"] = df["original_year"].astype(int)

# === Plotting Setup ===
sns.set(style="whitegrid")

# --- Tempo over Time ---
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x="original_year", y="tempo_bpm", errorbar=None)
plt.title("Average Tempo Over Time")
plt.xlabel("Year")
plt.ylabel("Tempo (BPM)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "tempo_over_time.png"))
plt.close()

# --- Chroma Heatmap by Year (Average) ---
if "chroma_mean" in df.columns:
    chroma_avg = pd.DataFrame(df["chroma_mean"].tolist()).groupby(df["original_year"]).mean()

    plt.figure(figsize=(14, 6))
    sns.heatmap(chroma_avg.T, cmap="viridis", cbar_kws={'label': 'Mean Chroma Energy'})
    plt.title("Average Chroma Distribution by Year")
    plt.xlabel("Year")
    plt.ylabel("Chroma Bins (C to B)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "chroma_heatmap.png"))
    plt.close()

# --- MFCC Mean Trends ---
if "mfcc_mean" in df.columns:
    mfcc_df = pd.DataFrame(df["mfcc_mean"].tolist())
    mfcc_df["year"] = df["original_year"]
    mfcc_melted = mfcc_df.melt(id_vars="year", var_name="MFCC Coefficient", value_name="Value")

    plt.figure(figsize=(14, 6))
    sns.lineplot(data=mfcc_melted, x="year", y="Value", hue="MFCC Coefficient", palette="tab10", errorbar=None)
    plt.title("MFCC Trends Over Time")
    plt.xlabel("Year")
    plt.ylabel("MFCC Mean Value")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "mfcc_trends.png"))
    plt.close()

# === Explanations ===
print("Saved tempo_over_time.png: Shows how the average beats-per-minute (tempo) of songs has changed across years.")
print("Saved chroma_heatmap.png: Displays the average chroma feature (pitch class energy from C to B) over time. Indicates shifts in harmonic content.")
print("Saved mfcc_trends.png: Plots trends in timbral features (MFCCs), showing changes in overall texture or tone color over time.")
