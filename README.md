# ThreatVision - Real-Time Network Traffic Dashboard

ThreatVision is an advanced Security Operations Center (SOC) platform designed for live network traffic monitoring and multi-stage threat detection. The project integrates real-time packet processing, flow feature extraction, and high-performance machine learning models (XGBoost/RandomForest) to distinguish between benign and malicious network behavior with high confidence.

## Technical Stack
- **Frontend**: Streamlit Framework with Plotly Visualizations & Custom CSS Glassmorphism
- **Backend Engine**: Python (Thread-based simulation & queue management)
- **Machine Learning**: Scikit-learn, XGBoost, Temperature Scaling Calibration

## Features
- **Live Traffic Monitoring**: Captures network traffic and visualizes it in real-time.
- **Machine Learning Threat Detection**: Integrates with a pre-trained model (`threatvision_realistic_temp.pkl`) to detect malicious network flows instantly.
- **IP Threat Tracking**: Tracks threat scores and ML predictions per IP address to automatically flag suspicious traffic.
- **Real-time Analytics**: Displays key metrics including Packets/sec, Protocol breakdowns, Top Source/Destination IPs, and Live Threat Rates.
- **Visualizations**: Interactive charts and a live history table that triggers active threat alerts.

## Prerequisites
- Python 3.8+
- Required packages (see `requirements.txt`)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ThreatVision.git
   cd ThreatVision
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Dashboard

To start the unified SOC dashboard, run the following command in your terminal:
```bash
streamlit run final_dashboard.py
```

## Running the ML Training Pipeline (Optional)

To train a new threat detection model using custom traffic data, run:
```bash
python train_model.py
```
