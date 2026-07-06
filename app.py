from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import json
import random
import os

# Importamos nuestros módulos POO
from models import Client, PostpaidPlan, PrepaidPlan, FiberPlan
from strategies.churn import StatisticalThresholdStrategy
from strategies.billing import PostpaidBilling, PrepaidBilling, FiberBilling
from analytics.data_analysis import generate_advanced_dashboard
from services.api_service import obtener_tipo_cambio_usd_pen

app = Flask(__name__)
app.secret_key = 'clave_secreta_crm_telecom'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm_telecom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ClienteDB(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_plan = db.Column(db.String(50), nullable=False)
    historial_consumo = db.Column(db.Text, default="[]") 

churn_strategy = StatisticalThresholdStrategy()

def reconstruir_objeto_cliente(cliente_db):
    if cliente_db.tipo_plan == 'postpago_basico':
        plan = PostpaidPlan("Básico", 20.0, 10, 500)
    elif cliente_db.tipo_plan == 'postpago_premium':
        plan = PostpaidPlan("Premium", 40.0, 999, 9999)
    elif cliente_db.tipo_plan == 'prepago_mensual':
        plan = PrepaidPlan("Mensual", 10.0, 30)
    elif cliente_db.tipo_plan == 'fibra_100':
        plan = FiberPlan("Fibra 100", 35.0, 100)
    else:
        plan = FiberPlan("Fibra 500", 60.0, 500)

    cliente_oop = Client(cliente_db.id, cliente_db.nombre, plan)
    cliente_oop.set_churn_strategy(churn_strategy)
    cliente_oop.consumption_history['data_usage_history_gb'] = json.loads(cliente_db.historial_consumo)
    
    return cliente_oop

# Inicializamos la BD y metemos datos de prueba si está vacía
with app.app_context():
    db.create_all()
    if ClienteDB.query.count() == 0:
        c1 = ClienteDB(id="CLI-001", nombre="Ana Gomez", tipo_plan="postpago_basico", historial_consumo=json.dumps([8.5, 9.0, 8.8, 9.2, 9.0]))
        c2 = ClienteDB(id="CLI-002", nombre="Luis Ramirez", tipo_plan="fibra_100", historial_consumo=json.dumps([120, 115, 110, 40, 15]))
        c3 = ClienteDB(id="CLI-003", nombre="Carlos Mendoza", tipo_plan="prepago_mensual", historial_consumo=json.dumps([2.0, 2.5, 3.0, 4.0, 5.5]))
        db.session.add_all([c1, c2, c3])
        db.session.commit()

def filtrar_clientes_en_riesgo(clientes):
    """
    Uso de Generadores (yield) para optimización de memoria.
    En lugar de crear y devolver una lista completa en RAM, evalúa y "escupe" 
    (yield) a los clientes uno por uno solo cuando se necesitan.
    """
    for c in clientes:
        if c.get_churn_risk() > 70:
            historial = c.consumption_history.get('data_usage_history_gb', [])
            media = sum(historial[:-1]) / len(historial[:-1]) if len(historial) > 1 else 1
            caida = ((media - historial[-1]) / media) * 100 if media > 0 else 0
            
            c.drop_ratio = round(caida, 2)
            yield c  # Retorna este cliente y pausa la ejecución hasta que pidan el siguiente


@app.route('/')
def index():
    return redirect(url_for('gestion_clientes'))


@app.route('/clientes', methods=['GET'])
def gestion_clientes():
    termino_busqueda = request.args.get('buscar', '')
    
    if termino_busqueda:
        clientes_bd = ClienteDB.query.filter(ClienteDB.nombre.ilike(f'%{termino_busqueda}%')).all()
    else:
        clientes_bd = ClienteDB.query.all()
        
    clientes_oop = [reconstruir_objeto_cliente(c) for c in clientes_bd]
    return render_template('clientes.html', clientes=clientes_oop, busqueda=termino_busqueda)

@app.route('/clientes/<cliente_id>', methods=['GET'])
def ver_perfil(cliente_id):
    cliente_bd = ClienteDB.query.get_or_404(cliente_id)
    
    cliente_oop = reconstruir_objeto_cliente(cliente_bd)
    
    return render_template('perfil.html', cliente=cliente_oop)

@app.route('/clientes/add', methods=['POST'])
def add_cliente():
    nombre = request.form.get('nombre')
    plan_str = request.form.get('plan')
    
    total_clientes = ClienteDB.query.count()
    nuevo_id = f"CLI-{total_clientes + 1:03d}"
    
    
    if random.random() > 0.7: 
        historial = [50, 48, 45, 10, 2] 
    else:
        historial_base = random.uniform(5, 50)
        historial = [max(0, historial_base + random.uniform(-5, 5)) for _ in range(5)]
    
    nuevo_cliente = ClienteDB(
        id=nuevo_id, 
        nombre=nombre, 
        tipo_plan=plan_str, 
        historial_consumo=json.dumps(historial)
    )
    db.session.add(nuevo_cliente)
    db.session.commit()
    
    return redirect(url_for('gestion_clientes'))

@app.route('/facturacion', methods=['GET'])
def facturacion():
    clientes_bd = ClienteDB.query.all()
    clientes_oop = [reconstruir_objeto_cliente(c) for c in clientes_bd]
    return render_template('facturacion.html', clientes=clientes_oop, factura=None)

@app.route('/facturacion/generar', methods=['POST'])
def generar_factura():
    cliente_id = request.form.get('cliente_id')
    mes = request.form.get('mes')
    
    cliente_bd = ClienteDB.query.get(cliente_id)
    
    if cliente_bd:
        cliente_oop = reconstruir_objeto_cliente(cliente_bd)
        
        if isinstance(cliente_oop.current_plan, PostpaidPlan):
            billing_strategy = PostpaidBilling()
        elif isinstance(cliente_oop.current_plan, PrepaidPlan):
            billing_strategy = PrepaidBilling()
        else:
            billing_strategy = FiberBilling()
            
        consumo_actual = cliente_oop.consumption_history['data_usage_history_gb'][-1]
        datos_consumo = {'current_month_gb': consumo_actual}
        
        resultado = billing_strategy.calculo_total(cliente_oop.current_plan, datos_consumo)
        
        # Consultamos la API externa
        tipo_cambio = obtener_tipo_cambio_usd_pen()
        total_usd = resultado['total']
        total_pen = total_usd * tipo_cambio
        
        factura = {
            'cliente': cliente_oop.name,
            'plan_detalles': cliente_oop.current_plan.get_details(),
            'cargos_extra': round(resultado['cargo_extra'], 2),
            'total_usd': round(total_usd, 2),
            'total_pen': round(total_pen, 2),
            'tipo_cambio': round(tipo_cambio, 3)
        }
        
        clientes_bd_all = ClienteDB.query.all()
        clientes_oop_all = [reconstruir_objeto_cliente(c) for c in clientes_bd_all]
        return render_template('facturacion.html', clientes=clientes_oop_all, factura=factura)
        
    return redirect(url_for('facturacion'))

@app.route('/facturacion/descargar_txt', methods=['POST'])
def descargar_factura_txt():
    cliente = request.form.get('cliente')
    plan = request.form.get('plan')
    total_usd = request.form.get('total_usd')
    total_pen = request.form.get('total_pen')
    
    nombre_archivo = f"Factura_{cliente.replace(' ', '_')}.txt"
    
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write("=========================================\n")
        archivo.write("         COMPROBANTE DE PAGO - CRM       \n")
        archivo.write("=========================================\n\n")
        archivo.write(f"Titular del servicio : {cliente}\n")
        archivo.write(f"Detalle del Plan     : {plan}\n")
        archivo.write("-----------------------------------------\n")
        archivo.write(f"TOTAL A PAGAR (USD)  : $ {total_usd}\n")
        archivo.write(f"TOTAL A PAGAR (PEN)  : S/ {total_pen}\n\n")
        archivo.write("=========================================\n")
        archivo.write("Gracias por confiar en nuestros servicios.\n")
    
    return send_file(nombre_archivo, as_attachment=True)


@app.route('/dashboard')
def dashboard():
    clientes_bd = ClienteDB.query.all()
    clientes_oop = [reconstruir_objeto_cliente(c) for c in clientes_bd]
    
    
    clientes_riesgo = list(filtrar_clientes_en_riesgo(clientes_oop))

    return render_template('dashboard.html', clientes_riesgo=clientes_riesgo)

@app.route('/clientes/<cliente_id>/retencion', methods=['POST'])
def aplicar_retencion(cliente_id):
    # Buscamos al cliente en la base de datos
    cliente_bd = ClienteDB.query.get_or_404(cliente_id)
    
    mensaje = f"¡Protocolo de retención activado exitosamente para {cliente_bd.nombre}! Se ha enviado una oferta de 20% de descuento a su correo."

    flash(mensaje, "success") 
    
    return redirect(url_for('dashboard'))

@app.route('/plot/dashboard_avanzado')
def plot_dashboard_avanzado():
    clientes_bd = ClienteDB.query.all()
    clientes_oop = [reconstruir_objeto_cliente(c) for c in clientes_bd]
    img_buffer = generate_advanced_dashboard(clientes_oop)
    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)




