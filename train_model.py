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
    df = pd.read_csv(csv_path) 
    # Clean column names (replace spaces with underscores, remove special chars)
    df.columns = [c.strip().replace(' ', '_').replace('/', '_') for c in df.columns]
    
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True) 
     
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder() 
    if 'Protocol' in df.columns: 
        df['Protocol'] = le.fit_transform(df['Protocol'].astype(str)) 
     
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
    
    y = None
    if 'Class' in df.columns:
        y = (df['Class'] == 'Attack').astype(int)
    elif 'Label' in df.columns:
        y = (~df['Label'].astype(str).str.contains('BENIGN|Normal', case=False)).astype(int)
     
    return df, X, y, available_features 
 
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
    df_train, X_train, y_train, features = load_and_prepare_data(training_csv) 
     
    if y_train is None:
        raise ValueError("Dataset does not contain a Label or Class column for training.")
     
    from imblearn.over_sampling import SMOTE
    from sklearn.preprocessing import StandardScaler
    import xgboost as xgb
    
    # Handle class imbalance with SMOTE 
    smote = SMOTE(random_state=42) 
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train) 
     
    # Scale features 
    scaler = StandardScaler() 
    X_train_scaled = scaler.fit_transform(X_train_resampled) 
     
    print("\\nTraining XGBoost...")
    model = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train_resampled) 
     
    from sklearn.metrics import classification_report
    y_pred = model.predict(X_train_scaled) 
    print("\\nXGBoost Classification Report:") 
    print(classification_report(y_train_resampled, y_pred)) 
     
    # Save the model
    from model_utils import TempScaledModel
    import joblib
    scaled_model = TempScaledModel(model, T=1.5)
    joblib.dump(scaled_model, 'threatvision_realistic_temp.pkl')
    # Save a dummy label encoder for the dashboard
    from sklearn.preprocessing import LabelEncoder
    encoder = LabelEncoder()
    encoder.fit(['BENIGN', 'MALICIOUS'])
    joblib.dump(encoder, 'label_encoder.pkl')
    
    return model, scaler, features 
 
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
    print("Training intrusion detection model on cicddos2019_dataset.csv...") 
    model, scaler, features = train_intrusion_detection_model("cicddos2019_dataset.csv") 
     
    print("\nTraining complete! Use the trained model to predict on new data.") 
  
 

