import os
import joblib
import pandas as pd
import numpy as np
from rich.console import Console
from rich.progress import track
from model_utils import TempScaledModel

console = Console()

# ------------------- Paths -------------------
INPUT_PATH = "raw_generated_test_data.csv"   # CSV with flows, no labels
ENCODER_PATH = "label_encoder.pkl"
MODEL_PATH = "threatvision_realistic_temp.pkl"

# ------------------- Features -------------------
basic_features = [
    "Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets",
    "Total_Length_of_Fwd_Packets", "Total_Length_of_Bwd_Packets",
    "Fwd_Packet_Length_Max", "Fwd_Packet_Length_Min",
    "Fwd_Packet_Length_Mean", "Fwd_Packet_Length_Std",
    "Bwd_Packet_Length_Max", "Bwd_Packet_Length_Min",
    "Bwd_Packet_Length_Mean", "Bwd_Packet_Length_Std",
    "Flow_Bytes_s", "Flow_Packets_s",
    "Flow_IAT_Mean", "Flow_IAT_Std", "Flow_IAT_Max", "Flow_IAT_Min",
    "Packet_Length_Variance"
]
extra_features = ["Fwd_Bwd_Packet_Ratio", "Fwd_Bwd_Bytes_Ratio"]
feature_cols = basic_features + extra_features

# ------------------- Load Model & Encoder -------------------
console.print("[bold cyan]🔍 Loading trained model...[/bold cyan]")
model: TempScaledModel = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

# ------------------- Load input CSV -------------------
def load_flows(path: str):
    if not os.path.exists(path):
        console.print(f"[red]❌ File {path} not found[/red]")
        exit()

    console.print(f"📂 Loading flows from {path}...")
    chunks = []
    for chunk in track(pd.read_csv(path, chunksize=100000), description="Reading flows..."):
        # Clean columns
        chunk.columns = chunk.columns.str.strip().str.replace("/", "_").str.replace(" ", "_")

        # Feature engineering
        chunk["Fwd_Bwd_Packet_Ratio"] = chunk["Total_Fwd_Packets"] / (chunk["Total_Backward_Packets"] + 1)
        chunk["Fwd_Bwd_Bytes_Ratio"] = chunk["Total_Length_of_Fwd_Packets"] / (chunk["Total_Length_of_Bwd_Packets"] + 1)

        # Keep only feature columns
        chunk_features = chunk[feature_cols].copy()

        # Replace inf/-inf and fill NaNs
        chunk_features.replace([np.inf, -np.inf], np.nan, inplace=True)
        chunk_features.fillna(0, inplace=True)

        # Downcast numeric types
        for col in chunk_features.select_dtypes(include=['int64']).columns:
            chunk_features[col] = pd.to_numeric(chunk_features[col], downcast='integer')
        for col in chunk_features.select_dtypes(include=['float64']).columns:
            chunk_features[col] = pd.to_numeric(chunk_features[col], downcast='float')

        chunks.append(chunk_features)

    X = pd.concat(chunks, ignore_index=True)
    return X

# ------------------- Predict -------------------
X = load_flows(INPUT_PATH)
console.print(f"🔮 Predicting {len(X)} flows...")

y_pred = model.predict(X)
y_pred_names = encoder.inverse_transform(y_pred)
binary_pred = ["BENIGN" if pred=="BENIGN" else "MALICIOUS" for pred in y_pred_names]

# ------------------- Display flows -------------------
console.print("\n[bold green]Flow Predictions:[/bold green]")
for i, (pred, row) in enumerate(zip(binary_pred, X.to_dict(orient="records"))):
    if pred == "BENIGN":
        console.print(f"[green]Flow {i+1}: {pred}[/green]")
    else:
        console.print(f"[bold red]Flow {i+1}: {pred} ⚠️ MALICIOUS DETECTED[/bold red]")
        # Display top feature values
        top_feats = sorted(row.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        console.print("[red]  Top feature values:[/red]")
        for feat, val in top_feats:
            console.print(f"    {feat}: {val}")

# ------------------- Summary -------------------
num_flows = len(binary_pred)
num_benign = binary_pred.count("BENIGN")
num_malicious = binary_pred.count("MALICIOUS")

console.print("\n[bold cyan]Prediction Summary:[/bold cyan]")
console.print(f"Total flows: {num_flows}")
console.print(f"Normal (BENIGN) flows: {num_benign} ({num_benign/num_flows*100:.2f}%)")
console.print(f"Malicious flows: {num_malicious} ({num_malicious/num_flows*100:.2f}%)")

# Save predictions to CSV
output_df = X.copy()
output_df["Prediction"] = binary_pred
output_file = "flow_predictions.csv"
output_df.to_csv(output_file, index=False)
console.print(f"[bold cyan]✅ Predictions saved to {output_file}[/bold cyan]")
