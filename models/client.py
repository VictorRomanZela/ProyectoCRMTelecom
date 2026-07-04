from models.plans import Plan
from strategies.churn import ChurnPredictionStrategy

class Client:
    def __init__(self, client_id, name, current_plan: Plan):
        self.client_id = client_id
        self.name = name
        self.current_plan = current_plan
        self.consumption_history = {'data_usage_history_gb': []}
        self.churn_strategy = None

    def set_churn_strategy(self, strategy: ChurnPredictionStrategy):
        self.churn_strategy = strategy

    def add_consumption(self, gb_used):
        self.consumption_history['data_usage_history_gb'].append(gb_used)

    def get_churn_risk(self):
        if not self.churn_strategy:
            raise ValueError("No se ha definido una estrategia de Churn.")
        
        risk = self.churn_strategy.calculate_risk(self.consumption_history)
        return round(risk * 100, 2) 