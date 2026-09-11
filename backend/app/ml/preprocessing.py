import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Optional

class LogPreprocessor:
    """
    StandardScaler wrapper for log feature normalization.
    """
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> "LogPreprocessor":
        self.scaler.fit(X)
        self.is_fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            return X
        return self.scaler.transform(X)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.is_fitted = True
        return self.scaler.fit_transform(X)

preprocessor = LogPreprocessor()
