from abc import ABC, abstractmethod

class Plan(ABC):
    def __init__(self, name, precio_base):
        self.name = name
        self.precio_base = precio_base

    @abstractmethod
    def get_details(self):
        pass

class PostpaidPlan(Plan):
    def __init__(self, name, precio_base, data_limit_gb, minutes_limit):
        super().__init__(name, precio_base)
        self.data_limit_gb = data_limit_gb
        self.minutes_limit = minutes_limit

    def get_details(self):
        return f"Postpago '{self.name}': {self.data_limit_gb}GB, {self.minutes_limit} min. Precio: ${self.precio_base}"

class PrepaidPlan(Plan):
    def __init__(self, name, precio_base, validity_days):
        super().__init__(name, precio_base)
        self.validity_days = validity_days

    def get_details(self):
        return f"Prepago '{self.name}': Vigencia {self.validity_days} días. Precio: ${self.precio_base}"

class FiberPlan(Plan):
    def __init__(self, name, precio_base, speed_mbps):
        super().__init__(name, precio_base)
        self.speed_mbps = speed_mbps

    def get_details(self):
        return f"Fibra Óptica '{self.name}': Velocidad {self.speed_mbps}Mbps. Precio: ${self.precio_base}"