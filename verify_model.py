import os
import joblib
import pandas as pd
import numpy as np

# ------------------- Paths -------------------
INPUT_PATH = "cicddos2019_dataset.csv"   # CSV with flows, no labels
ENCODER_PATH = "label_encoder.pkl"
MODEL_PATH = "threatvision_realistic_temp.pkl"

print("Loading trained model...")
model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

def load_flows(path: str):
    if not os.path.exists(path):
        print(f"File {path} not found")
        exit()

    print(f"Loading flows from {path}...")
    df = pd.read_csv(path, nrows=50000) # just verify on first 50k
    df.columns = [c.strip().replace(' ', '_').replace('/', '_') for c in df.columns]
    
    feature_columns = [ 
        'Length', 'Flow_Duration', 'Total_Fwd_Packets', 'Total_Backward_Packets', 
        'Total_Length_of_Fwd_Packets', 'Total_Length_of_Bwd_Packets', 
        'Fwd_Packet_Length_Max', 'Fwd_Packet_Length_Min', 'Fwd_Packet_Length_Mean', 
        'Fwd_Packet_Length_Std', 'Bwd_Packet_Length_Max', 'Bwd_Packet_Length_Min', 
        'Bwd_Packet_Length_Mean', 'Bwd_Packet_Length_Std', 'Flow_Bytes_s', 
        'Flow_Packets_s', 'Flow_IAT_Mean', 'Flow_IAT_Std', 'Flow_IAT_Max', 
        'Flow_IAT_Min', 'Packet_Length_Variance', 'Fwd_Bwd_Packet_Ratio', 
        'Fwd_Bwd_Bytes_Ratio' 
    ]
    available_features = [col for col in feature_columns if col in df.columns]
    
    X = df[available_features].copy()
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.fillna(0, inplace=True)
    return X, df

X, original_df = load_flows(INPUT_PATH)
print(f"Predicting {len(X)} flows...")

# Get predictions using the same features the model was trained on
y_pred = model.predict(X)

# Binary mappings
if hasattr(encoder, 'inverse_transform') and len(encoder.classes_) > 0:
    y_pred_names = encoder.inverse_transform(y_pred)
    binary_pred = ["BENIGN" if pred in ["BENIGN", 0, "0", 0.0] else "MALICIOUS" for pred in y_pred_names]
else:
    binary_pred = ["BENIGN" if pred == 0 else "MALICIOUS" for pred in y_pred]

num_flows = len(binary_pred)
num_benign = binary_pred.count("BENIGN")
num_malicious = binary_pred.count("MALICIOUS")

print("\nPrediction Summary:")
print(f"Total flows: {num_flows}")
print(f"Normal (BENIGN) flows: {num_benign} ({num_benign/num_flows*100:.2f}%)")
print(f"Malicious flows: {num_malicious} ({num_malicious/num_flows*100:.2f}%)")
print("Verify complete!")
