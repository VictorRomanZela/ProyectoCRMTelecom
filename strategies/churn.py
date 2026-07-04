from abc import ABC, abstractmethod
import numpy as np

class ChurnPredictionStrategy(ABC):
    @abstractmethod
    def calculate_risk(self, client_data: dict) -> float:
        pass

class StatisticalThresholdStrategy(ChurnPredictionStrategy):
    
    def calculate_risk(self, client_data: dict) -> float:
        history = client_data.get('data_usage_history_gb', [])
        
        if len(history) < 2:
            return 0.10  
        
        historical_mean = np.mean(history[:-1])
        recent_usage = history[-1]
        
        if historical_mean == 0:
            return 0.0
            
        drop_ratio = (historical_mean - recent_usage) / historical_mean
        
        if drop_ratio > 0.5:
            return 0.85 
        elif drop_ratio > 0.2:
            return 0.40  
        elif drop_ratio < 0:
            return 0.05  
        else:
            return 0.15  