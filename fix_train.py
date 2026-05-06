import pandas as pd
import numpy as np
import re

# Read original
with open('train_model.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix load_and_prepare_data to rename columns
new_load = '''def load_and_prepare_data(csv_path): 
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
     
    return df, X, y, available_features'''

text = re.sub(r'def load_and_prepare_data\(csv_path\):.*?return df, X, available_features', new_load, text, flags=re.DOTALL)

# Fix train_intrusion_detection_model
new_train = '''def train_intrusion_detection_model(training_csv, test_csv=None): 
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
    
    return model, scaler, features'''

text = re.sub(r'def train_intrusion_detection_model\(training_csv, test_csv=None\):.*?return trained_models\[\'XGBoost\'\], scaler, features', new_train, text, flags=re.DOTALL)

with open('train_model.py', 'w', encoding='utf-8') as f:
    f.write(text)
