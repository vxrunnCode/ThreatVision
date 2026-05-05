import pandas as pd 
import numpy as np 
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier 
from sklearn.preprocessing import StandardScaler, LabelEncoder 
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score 
from imblearn.over_sampling import SMOTE 
import xgboost as xgb 
import warnings 
warnings.filterwarnings('ignore') 
 
def load_and_prepare_data(csv_path): 
    """Load and prepare network flow data""" 
    df = pd.read_csv(csv_path) 
     
    # Fill NaN values 
    df = df.fillna(0) 
     
    # Encode categorical variables 
    le = LabelEncoder() 
    if 'Protocol' in df.columns: 
        df['Protocol'] = le.fit_transform(df['Protocol']) 
     
    # Extract features (exclude metadata columns) 
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
     
    # Only use columns that exist 
    available_features = [col for col in feature_columns if col in df.columns] 
    X = df[available_features].copy() 
     
    return df, X, available_features 
 
def create_malicious_features(X, malicious_indices): 
    """Artificially create malicious feature patterns""" 
    for idx in malicious_indices: 
        if idx < len(X): 
            # High packet count attack 
            X.loc[idx, 'Total_Fwd_Packets'] = np.random.randint(1000, 100000) 
            X.loc[idx, 'Flow_Packets_s'] = np.random.uniform(100000, 10000000) 
            X.loc[idx, 'Flow_Bytes_s'] = np.random.uniform(1000000, 100000000) 
             
            # Short burst attack patterns 
            X.loc[idx, 'Flow_Duration'] = np.random.uniform(0.001, 1.0) 
            X.loc[idx, 'Flow_IAT_Mean'] = np.random.uniform(0.000001, 0.001) 
            X.loc[idx, 'Flow_IAT_Std'] = np.random.uniform(0.000001, 0.0001) 
             
            # Suspicious packet size patterns 
            X.loc[idx, 'Fwd_Packet_Length_Mean'] = np.random.choice([40, 64, 128, 1500]) 
            X.loc[idx, 'Fwd_Packet_Length_Std'] = np.random.uniform(0, 10) 
             
            # One-sided traffic (common in DDoS) 
            X.loc[idx, 'Total_Backward_Packets'] = np.random.randint(0, 10) 
            X.loc[idx, 'Fwd_Bwd_Packet_Ratio'] = np.random.uniform(100, 10000) 
     
    return X 
 
def train_intrusion_detection_model(training_csv, test_csv=None): 
    """Train an intrusion detection model with realistic attack patterns""" 
     
    # Load data 
    df_train, X_train, features = load_and_prepare_data(training_csv) 
     
    # Create labels - assuming we know which are malicious in training 
    # In real scenario, you'd have labeled data 
    y_train = np.zeros(len(X_train)) 
     
    # Mark 30% of data as malicious (for synthetic training) 
    n_malicious = int(0.3 * len(X_train)) 
    malicious_indices = np.random.choice(len(X_train), n_malicious, replace=False) 
    y_train[malicious_indices] = 1 
     
    # Create realistic malicious patterns 
    X_train = create_malicious_features(X_train, malicious_indices) 
     
    # Handle class imbalance with SMOTE 
    smote = SMOTE(random_state=42) 
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train) 
     
    # Scale features 
    scaler = StandardScaler() 
    X_train_scaled = scaler.fit_transform(X_train_resampled) 
     
    # Train multiple models 
    models = { 
        'XGBoost': xgb.XGBClassifier( 
            n_estimators=200, 
            max_depth=10, 
            learning_rate=0.1, 
            subsample=0.8, 
            colsample_bytree=0.8, 
            random_state=42, 
            scale_pos_weight=len(y_train[y_train==0])/len(y_train[y_train==1]) 
        ), 
        'RandomForest': RandomForestClassifier( 
            n_estimators=200, 
            max_depth=15, 
            min_samples_split=5, 
            min_samples_leaf=2, 
            random_state=42, 
            class_weight='balanced' 
        ), 
        'GradientBoosting': GradientBoostingClassifier( 
            n_estimators=200, 
            max_depth=7, 
            learning_rate=0.1, 
            random_state=42 
        ) 
    } 
     
    trained_models = {} 
    for name, model in models.items(): 
        print(f"\nTraining {name}...") 
        model.fit(X_train_scaled, y_train_resampled) 
        trained_models[name] = model 
     
    # Evaluate on training data 
    print("\n" + "="*50) 
    print("Training Results:") 
    print("="*50) 
     
    for name, model in trained_models.items(): 
        y_pred = model.predict(X_train_scaled) 
        print(f"\n{name} Classification Report:") 
        print(classification_report(y_train_resampled, y_pred,  
                                   target_names=['Benign', 'Malicious'])) 
     
    # If test data provided, evaluate on it 
    if test_csv: 
        df_test, X_test, _ = load_and_prepare_data(test_csv) 
        X_test_scaled = scaler.transform(X_test) 
         
        print("\n" + "="*50) 
        print("Test Results (using best model - XGBoost):") 
        print("="*50) 
         
        best_model = trained_models['XGBoost'] 
        y_test_pred = best_model.predict(X_test_scaled) 
         
        # For test, we need actual labels - create synthetic for demonstration 
        y_test = np.random.choice([0, 1], size=len(X_test), p=[0.7, 0.3]) 
         
        print(f"\nTest Classification Report:") 
        print(classification_report(y_test, y_test_pred,  
                                   target_names=['Benign', 'Malicious'])) 
     
    return trained_models['XGBoost'], scaler, features 
 
def generate_realistic_test_data(output_path, n_samples=1000): 
    """Generate realistic test data with clear attack patterns""" 
     
    data = [] 
     
    for i in range(n_samples): 
        # Determine if this is malicious (30% chance) 
        is_malicious = np.random.random() < 0.3 
         
        if is_malicious: 
            # Generate malicious traffic patterns 
             
            # Attack type selection 
            attack_type = np.random.choice(['ddos', 'port_scan', 'brute_force', 'malware']) 
             
            if attack_type == 'ddos': 
                # DDoS attack pattern 
                row = { 
                    'Total_Fwd_Packets': np.random.randint(5000, 100000), 
                    'Total_Backward_Packets': np.random.randint(0, 100), 
                    'Flow_Duration': np.random.uniform(0.1, 10.0), 
                    'Flow_Bytes_s': np.random.uniform(1000000, 100000000), 
                    'Flow_Packets_s': np.random.uniform(10000, 1000000), 
                    'Flow_IAT_Mean': np.random.uniform(0.00001, 0.001), 
                    'Fwd_Bwd_Packet_Ratio': np.random.uniform(50, 1000), 
                    'Fwd_Packet_Length_Mean': np.random.choice([40, 64, 128]), 
                    'Fwd_Packet_Length_Std': np.random.uniform(0, 5) 
                } 
                 
            elif attack_type == 'port_scan': 
                # Port scan pattern 
                row = { 
                    'Total_Fwd_Packets': np.random.randint(100, 1000), 
                    'Total_Backward_Packets': np.random.randint(0, 10), 
                    'Flow_Duration': np.random.uniform(0.01, 1.0), 
                    'Flow_Bytes_s': np.random.uniform(10000, 1000000), 
                    'Flow_Packets_s': np.random.uniform(100, 10000), 
                    'Flow_IAT_Mean': np.random.uniform(0.0001, 0.01), 
                    'Fwd_Bwd_Packet_Ratio': np.random.uniform(10, 100), 
                    'Fwd_Packet_Length_Mean': 40,  # Small SYN packets 
                    'Fwd_Packet_Length_Std': np.random.uniform(0, 2) 
                } 
                 
            elif attack_type == 'brute_force': 
                # Brute force attack pattern 
                row = { 
                    'Total_Fwd_Packets': np.random.randint(100, 5000), 
                    'Total_Backward_Packets': np.random.randint(10, 100), 
                    'Flow_Duration': np.random.uniform(1.0, 60.0), 
                    'Flow_Bytes_s': np.random.uniform(1000, 100000), 
                    'Flow_Packets_s': np.random.uniform(10, 1000), 
                    'Flow_IAT_Mean': np.random.uniform(0.01, 0.1), 
                    'Fwd_Bwd_Packet_Ratio': np.random.uniform(1, 10), 
                    'Fwd_Packet_Length_Mean': np.random.uniform(100, 500), 
                    'Fwd_Packet_Length_Std': np.random.uniform(10, 100) 
                } 
                 
        else: 
            # Generate benign traffic pattern 
            row = { 
                'Total_Fwd_Packets': np.random.randint(1, 100), 
                'Total_Backward_Packets': np.random.randint(1, 50), 
                'Flow_Duration': np.random.uniform(0.1, 1000.0), 
                'Flow_Bytes_s': np.random.uniform(100, 10000), 
                'Flow_Packets_s': np.random.uniform(1, 100), 
                'Flow_IAT_Mean': np.random.uniform(0.001, 1.0), 
                'Fwd_Bwd_Packet_Ratio': np.random.uniform(0.1, 10), 
                'Fwd_Packet_Length_Mean': np.random.uniform(100, 1500), 
                'Fwd_Packet_Length_Std': np.random.uniform(10, 500) 
            } 
         
        # Add common features 
        row.update({ 
            'Length': np.random.randint(40, 1500), 
            'Total_Length_of_Fwd_Packets': row['Total_Fwd_Packets'] * 
row['Fwd_Packet_Length_Mean'], 
            'Total_Length_of_Bwd_Packets': row['Total_Backward_Packets'] * np.random.uniform(50, 
1500), 
            'Fwd_Packet_Length_Max': row['Fwd_Packet_Length_Mean'] + np.random.uniform(0, 100), 
            'Fwd_Packet_Length_Min': max(40, row['Fwd_Packet_Length_Mean'] - np.random.uniform(0, 
100)), 
            'Bwd_Packet_Length_Max': np.random.uniform(50, 1500), 
            'Bwd_Packet_Length_Min': np.random.uniform(40, 100), 
            'Bwd_Packet_Length_Mean': np.random.uniform(100, 1000), 
            'Bwd_Packet_Length_Std': np.random.uniform(10, 500), 
            'Flow_IAT_Std': row['Flow_IAT_Mean'] * np.random.uniform(0.5, 2), 
            'Flow_IAT_Max': row['Flow_IAT_Mean'] * np.random.uniform(2, 10), 
            'Flow_IAT_Min': row['Flow_IAT_Mean'] * np.random.uniform(0.1, 0.5), 
            'Packet_Length_Variance': row['Fwd_Packet_Length_Std'] ** 2, 
            'Fwd_Bwd_Bytes_Ratio': row['Fwd_Bwd_Packet_Ratio'] * np.random.uniform(0.5, 2) 
        }) 
         
        data.append(row) 
     
    df = pd.DataFrame(data) 
    df.to_csv(output_path, index=False) 
    print(f"Generated test data with {len(df)} samples saved to {output_path}") 
     
    # Add labels for training 
    df['Label'] = [1 if i < n_samples * 0.3 else 0 for i in range(n_samples)] 
     
    return df 
 
# Example usage 
if __name__ == "__main__": 
    # Step 1: Generate realistic training data 
    print("Generating realistic training data...") 
    training_data = generate_realistic_test_data("realistic_training_data.csv", n_samples=5000) 
     
    # Step 2: Train model 
    print("\nTraining intrusion detection model...") 
    model, scaler, features = train_intrusion_detection_model("realistic_training_data.csv") 
     
    # Step 3: Generate test data 
    print("\nGenerating test data...") 
    test_data = generate_realistic_test_data("realistic_test_data.csv", n_samples=1000) 
     
    print("\nTraining complete! Use the trained model to predict on new data.") 
  
 
# model_utils.py 
import numpy as np 
 
# ------------------- Temperature Scaling ------------------- 
def temperature_scale(probs, T=1.5): 
    """ 
    Apply temperature scaling to probabilities. 
    T > 1 makes probabilities softer 
    T < 1 makes probabilities sharper 
    """ 
    logits = np.log(np.clip(probs, 1e-12, 1 - 1e-12))  # logit transform 
    scaled_logits = logits / T 
    return 1 / (1 + np.exp(-scaled_logits)) 
 
# ------------------- Wrapper Class ------------------- 
class TempScaledModel: 
    """ 
    Wraps a scikit-learn or XGBoost classifier with temperature scaling. 
    """ 
    def __init__(self, base_model, T=1.5): 
        self.base_model = base_model 
        self.T = T 
 
    def predict_proba(self, X): 
        base_probs = self.base_model.predict_proba(X) 
        scaled_probs = np.zeros_like(base_probs) 
        for i in range(base_probs.shape[1]): 
            scaled_probs[:, i] = temperature_scale(base_probs[:, i], self.T) 
        scaled_probs /= scaled_probs.sum(axis=1, keepdims=True)  # normalize 
        return scaled_probs 
 
    def predict(self, X): 
        return np.argmax(self.predict_proba(X), axis=1) 
 
  

# pages/1_Report.py 
 
import streamlit as st 
import pandas as pd 
import numpy as np 
import joblib 
import matplotlib.pyplot as plt 
import io 
from datetime import datetime 
 
st.set_page_config(page_title="ThreatVision - Report", layout="wide") 
st.title("      ThreatVision Report Generator") 
 
# Load trained model & label encoder 
@st.cache_resource 
def load_model(): 
    model = joblib.load("threatvision_realistic_temp.pkl") 
    label_encoder = joblib.load("label_encoder.pkl") 
    return model, label_encoder 
 
model, label_encoder = load_model() 
 
# Define feature columns (must match training) 
feature_cols = [ 
    "Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets", 
    "Total_Length_of_Fwd_Packets", "Total_Length_of_Bwd_Packets", 
    "Fwd_Packet_Length_Max", "Fwd_Packet_Length_Min", "Fwd_Packet_Length_Mean", 
    "Fwd_Packet_Length_Std", "Bwd_Packet_Length_Max", "Bwd_Packet_Length_Min", 
    "Bwd_Packet_Length_Mean", "Bwd_Packet_Length_Std", "Flow_Bytes_s", 
    "Flow_Packets_s", "Flow_IAT_Mean", "Flow_IAT_Std", "Flow_IAT_Max", 
    "Flow_IAT_Min", "Packet_Length_Variance", "Fwd_Bwd_Packet_Ratio", 
    "Fwd_Bwd_Bytes_Ratio" 
] 
 
# Upload CSV 
uploaded_file = st.file_uploader("   Upload a network traffic CSV file", type=["csv"]) 
 
if uploaded_file is not None: 
    df = pd.read_csv(uploaded_file) 
    st.success("   File uploaded successfully!") 
 
    # Ensure all required features exist 
    for col in feature_cols: 
        if col not in df.columns: 
            df[col] = 0  # fill missing features with 0 
 
    # Extract features safely 
    X_features = df[feature_cols].replace([np.inf, -np.inf], 0).fillna(0).astype(float) 
 
    if "Fwd_Bwd_Packet_Ratio" not in df.columns: 
        df["Fwd_Bwd_Packet_Ratio"] = ( 
            df["Total_Fwd_Packets"] / (df["Total_Backward_Packets"] + 1e-6) 
        ) 
 
    if "Fwd_Bwd_Bytes_Ratio" not in df.columns: 
        df["Fwd_Bwd_Bytes_Ratio"] = ( 
            df["Total_Length_of_Fwd_Packets"] / (df["Total_Length_of_Bwd_Packets"] + 1e-6) 
        ) 
 
    # Run predictions 
    y_pred = model.predict(X_features) 
    df["Prediction"] = label_encoder.inverse_transform(y_pred) 
 
    # Summary Pie Chart 
    st.subheader("    Prediction Summary") 
    summary = df["Prediction"].value_counts() 
 
    # Define colors for each class 
    colors = plt.cm.Set2.colors[:len(summary.index)] 
 
    fig, ax = plt.subplots() 
    wedges, texts = ax.pie( 
        summary, 
        labels=None,  # Remove labels from pie chart 
        startangle=90, 
        colors=colors 
    ) 
    ax.axis('equal') 
 
    # Create legend mapping colors to class names 
    legend_labels = [f"{cls}" for cls in summary.index] 
    ax.legend(wedges, legend_labels, title="Class", loc="center left", bbox_to_anchor=(1, 0.5)) 
 
    st.pyplot(fig) 
 
    # Show percentage table separately 
    percent_df = pd.DataFrame({ 
        "Class": summary.index, 
        "Percentage": (summary / summary.sum() * 100).round(2) 
    }) 
    st.subheader("      Prediction Percentages") 
    st.table(percent_df) 
 
    # Show styled predictions 
    st.subheader("       Detailed Predictions") 
    st.dataframe(df[["Prediction"]].head(50))  # show first 50 predictions 
 
    # ------------------- Additional Packet Information Graphs ------------------- 
    st.subheader("    Packet Information Graphs") 
 
    # Example 1: Packet Length Distribution 
    if "Length" in df.columns: 
        fig_len, ax_len = plt.subplots() 
        ax_len.hist(df["Length"].dropna(), bins=30, color='skyblue', edgecolor='black') 
        ax_len.set_title("Packet Length Distribution") 
        ax_len.set_xlabel("Packet Length (Bytes)") 
        ax_len.set_ylabel("Count") 
        st.pyplot(fig_len) 
else: 
    st.info("     Please upload a CSV file to generate the report.") 
 
  
