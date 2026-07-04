import unittest

# Importamos nuestras clases de negocio y estrategias
from models.plans import PostpaidPlan, PrepaidPlan
from strategies.billing import PostpaidBilling, PrepaidBilling
from strategies.churn import StatisticalThresholdStrategy

class TestCRMStrategies(unittest.TestCase):
    """Clase de QA (Aseguramiento de Calidad) para probar la lógica matemática del CRM."""

    def setUp(self):
        """Este método se ejecuta automáticamente antes de cada prueba.
        Sirve para preparar los datos iniciales (nuestro entorno de pruebas)."""
        self.plan_postpago = PostpaidPlan("Básico", 20.0, 10, 500) # Límite de 10GB
        self.plan_prepago = PrepaidPlan("Mensual", 10.0, 30)
        
        self.billing_postpago = PostpaidBilling()
        self.billing_prepago = PrepaidBilling()
        self.churn_strategy = StatisticalThresholdStrategy()

    # --- PRUEBAS DE FACTURACIÓN ---

    def test_postpaid_billing_dentro_del_limite(self):
        """Prueba: Un cliente postpago que gasta menos de su límite no debe pagar extras."""
        datos_consumo = {'current_month_gb': 8} # Gastó 8GB de 10GB
        resultado = self.billing_postpago.calculo_total(self.plan_postpago, datos_consumo)
        
        # Verificamos (assert) que el total sea igual al precio base (20.0)
        self.assertEqual(resultado['total'], 20.0)
        self.assertEqual(resultado['cargo_extra'], 0.0)

    def test_postpaid_billing_con_excedente(self):
        """Prueba: Un cliente postpago que se pasa del límite debe pagar $2.5 por cada GB extra."""
        datos_consumo = {'current_month_gb': 12} # Gastó 12GB (2GB extra)
        resultado = self.billing_postpago.calculo_total(self.plan_postpago, datos_consumo)
        
        # Matemáticas: 20.0 base + (2GB * 2.5) = 25.0
        self.assertEqual(resultado['total'], 25.0)
        self.assertEqual(resultado['cargo_extra'], 5.0)

    def test_prepaid_billing_tarifa_plana(self):
        """Prueba: Un cliente prepago siempre paga lo mismo sin importar si gasta 1GB o 100GB."""
        datos_consumo = {'current_month_gb': 50} 
        resultado = self.billing_prepago.calculo_total(self.plan_prepago, datos_consumo)
        
        self.assertEqual(resultado['total'], 10.0)

    # --- PRUEBAS DE PREDICCIÓN DE CHURN ---

    def test_churn_alto_riesgo(self):
        """Prueba: Si el consumo cae más del 50%, el riesgo debe ser del 85% (0.85)."""
        # Promedio histórico es alto, pero el último mes cayó a 15
        client_data = {'data_usage_history_gb': [120, 115, 110, 15]}
        riesgo = self.churn_strategy.calculate_risk(client_data)
        
        self.assertEqual(riesgo, 0.85)

    def test_churn_bajo_riesgo(self):
        """Prueba: Si el consumo es estable o aumenta, el riesgo debe ser muy bajo."""
        client_data = {'data_usage_history_gb': [2.0, 2.5, 3.0, 4.0]}
        riesgo = self.churn_strategy.calculate_risk(client_data)
        
        # El riesgo debe ser menor al 50%
        self.assertTrue(riesgo < 0.5)

if __name__ == '__main__':
    # Esto arranca las pruebas si ejecutamos el archivo directamente
    unittest.main()













