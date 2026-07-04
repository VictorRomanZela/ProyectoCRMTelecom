from abc import ABC, abstractmethod

class BillingStrategy(ABC):
    @abstractmethod
    def calculo_total(self, plan, datos_consumo: dict) -> dict:
        pass

class PostpaidBilling(BillingStrategy):
    def calculo_total(self, plan, datos_consumo: dict) -> dict:
        base = plan.precio_base
        gb_used = datos_consumo.get('current_month_gb', 0)
        cargo_extra = 0
        
        if gb_used > plan.data_limit_gb:
            cargo_extra = (gb_used - plan.data_limit_gb) * 2.5 
            
        total = base + cargo_extra
        return {
            "precio_base": base,
            "cargo_extra": cargo_extra,
            "total": total
        }

class PrepaidBilling(BillingStrategy):
    def calculo_total(self, plan, datos_consumo: dict) -> dict:
        return {
            "precio_base": plan.precio_base,
            "cargo_extra": 0.0,
            "total": plan.precio_base
        }

class FiberBilling(BillingStrategy):
    def calculo_total(self, plan, datos_consumo: dict) -> dict:
        return {
            "precio_base": plan.precio_base,
            "cargo_extra": 0.0,
            "total": plan.precio_base
        }