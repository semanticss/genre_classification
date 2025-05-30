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
df_with_year = df[df["original_year"].notna() & df["tempo_bpm"].notna()]
df_with_year["original_year"] = df_with_year["original_year"].astype(int)
df_classical = df[df["original_year"].isna() & df["tempo_bpm"].notna()]  # Assume classical if year is missing

# === Plotting Setup ===
sns.set(style="whitegrid")

# --- Tempo over Time ---
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_with_year, x="original_year", y="tempo_bpm", errorbar=None)
if not df_classical.empty:
    classical_tempo = df_classical["tempo_bpm"].mean()
    plt.axhline(classical_tempo, color="gray", linestyle="--", label="Classical Avg Tempo")
    plt.legend()
plt.title("Average Tempo Over Time")
plt.xlabel("Year")
plt.ylabel("Tempo (BPM)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "tempo_over_time.png"))
plt.close()

# --- Classical Only Plots ---
if not df_classical.empty:
    # Chroma for Classical
    chroma_df = pd.DataFrame(df_classical["chroma_mean"].tolist())
    plt.figure(figsize=(10, 6))
    sns.heatmap(chroma_df.mean().to_frame().T, cmap="viridis", cbar_kws={'label': 'Mean Chroma Energy'})
    plt.title("Chroma Distribution - Classical")
    plt.xlabel("Chroma Bins (C to B)")
    plt.yticks([])
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "classical_chroma.png"))
    plt.close()

    # MFCC for Classical
    mfcc_df = pd.DataFrame(df_classical["mfcc_mean"].tolist())
    mfcc_avg = mfcc_df.mean()
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=mfcc_avg.index, y=mfcc_avg.values)
    plt.title("MFCC Mean Coefficients - Classical")
    plt.xlabel("MFCC Coefficient Index")
    plt.ylabel("Mean Value")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "classical_mfcc.png"))
    plt.close()

# --- Chroma Heatmap by Year (Average) ---
if "chroma_mean" in df.columns:
    chroma_avg = pd.DataFrame(df_with_year["chroma_mean"].tolist()).groupby(df_with_year["original_year"]).mean()

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
    mfcc_df = pd.DataFrame(df_with_year["mfcc_mean"].tolist())
    mfcc_df["year"] = df_with_year["original_year"]
    mfcc_melted = mfcc_df.melt(id_vars="year", var_name="MFCC Coefficient", value_name="Value")

    plt.figure(figsize=(14, 6))
    sns.lineplot(data=mfcc_melted, x="year", y="Value", hue="MFCC Coefficient", palette="tab10", errorbar=None)
    plt.title("MFCC Trends Over Time")
    plt.xlabel("Year")
    plt.ylabel("MFCC Mean Value")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "mfcc_trends.png"))
    plt.close()
