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
