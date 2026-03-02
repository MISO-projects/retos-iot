from argparse import ArgumentError
import ssl
from django.db.models import Avg, Max
from datetime import timedelta, datetime
from django.utils import timezone
from receiver.models import Data, Measurement
import paho.mqtt.client as mqtt
import schedule
import time
from django.conf import settings

# Número mínimo de lecturas individuales consecutivas por encima del límite para activar el ventilador
SUSTAINED_THRESHOLD = 5

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, settings.MQTT_USER_PUB)


def analyze_data():
    # Consulta todos los datos de la última hora, los agrupa por estación y variable
    # Compara el promedio con los valores límite que están en la base de datos para esa variable.
    # Si el promedio se excede de los límites, se envia un mensaje de alerta.

    print("Calculando alertas...")

    data = Data.objects.filter(
        base_time__gte=datetime.now() - timedelta(hours=1))
    aggregation = data.annotate(check_value=Avg('avg_value')) \
        .select_related('station', 'measurement') \
        .select_related('station__user', 'station__location') \
        .select_related('station__location__city', 'station__location__state',
                        'station__location__country') \
        .values('check_value', 'station__user__username',
                'measurement__name',
                'measurement__max_value',
                'measurement__min_value',
                'station__location__city__name',
                'station__location__state__name',
                'station__location__country__name')
    alerts = 0
    for item in aggregation:
        alert = False

        variable = item["measurement__name"]
        max_value = item["measurement__max_value"] or 0
        min_value = item["measurement__min_value"] or 0

        country = item['station__location__country__name']
        state = item['station__location__state__name']
        city = item['station__location__city__name']
        user = item['station__user__username']

        if item["check_value"] > max_value or item["check_value"] < min_value:
            print("Alerta: check_value: {check_value} max_value: {max_value} min_value: {min_value}".format(check_value=item["check_value"], max_value=max_value, min_value=min_value))
            alert = True

        if alert:
            message = "ALERT {} {} {}".format(variable, min_value, max_value)
            topic = '{}/{}/{}/{}/in'.format(country, state, city, user)
            print(datetime.now(), "Sending alert to {} {}".format(topic, variable))
            # Wait for connection if client is disconnected
            retries = 0
            while not client.is_connected() and retries < 10:
                print("Esperando reconexión MQTT...")
                time.sleep(1)
                retries += 1
            client.publish(topic, message, qos=1)
            alerts += 1

    print(len(aggregation), "dispositivos revisados")
    print(alerts, "alertas enviadas")


def analyze_sustained_temperature():
    """
    Nuevo evento: detecta si las últimas N lecturas individuales de temperatura
    se han mantenido por encima del límite máximo configurado para esa variable.
    Consulta el registro más reciente de cada estación (patrón Blob) y revisa
    los últimos SUSTAINED_THRESHOLD valores del array 'values'.
    Si se cumple la condición sostenida, envía FAN ON al dispositivo para
    activar el ventilador. Si la temperatura vuelve a estar dentro del rango,
    envía FAN OFF para apagarlo.
    """
    print("Analizando temperatura sostenida...")

    # Consultar los registros de temperatura de la última hora,
    # ordenados por estación y del más reciente al más antiguo.
    records = Data.objects.filter(
        measurement__name='temperatura',
        base_time__gte=timezone.now() - timedelta(hours=1)
    ).select_related(
        'station', 'measurement',
        'station__user', 'station__location',
        'station__location__city', 'station__location__state',
        'station__location__country'
    ).order_by('station', '-time')

    # Agrupar por estación: tomamos solo el registro más reciente de cada una
    # (el blob más reciente contiene las lecturas individuales más actuales)
    latest_per_station = {}
    for record in records:
        sid = record.station_id
        if sid not in latest_per_station:
            latest_per_station[sid] = record

    fan_commands = 0
    for sid, record in latest_per_station.items():
        max_value = record.measurement.max_value
        if max_value is None:
            continue

        values = record.values  # Array con las lecturas individuales del blob
        if len(values) < SUSTAINED_THRESHOLD:
            print("  Estación {}: solo {} lecturas, se requieren {}".format(
                sid, len(values), SUSTAINED_THRESHOLD))
            continue

        # Tomar las últimas SUSTAINED_THRESHOLD lecturas individuales
        last_values = values[-SUSTAINED_THRESHOLD:]

        station = record.station
        country = station.location.country.name
        state = station.location.state.name
        city = station.location.city.name
        user = station.user.username
        topic = '{}/{}/{}/{}/in'.format(country, state, city, user)

        # Verificar si TODAS las últimas lecturas superan el máximo
        all_above = all(v > max_value for v in last_values)

        if all_above:
            message = "FAN ON"
            print(timezone.now(),
                  "Temperatura sostenida alta (últimas {} lecturas: {} > {}). Enviando {} a {}".format(
                      SUSTAINED_THRESHOLD, last_values, max_value, message, topic))
        else:
            message = "FAN OFF"
            print(timezone.now(),
                  "Temperatura dentro de rango (últimas {} lecturas: {}). Enviando {} a {}".format(
                      SUSTAINED_THRESHOLD, last_values, message, topic))

        # Esperar reconexión si es necesario
        retries = 0
        while not client.is_connected() and retries < 10:
            print("Esperando reconexión MQTT...")
            time.sleep(1)
            retries += 1
        client.publish(topic, message, qos=1)
        fan_commands += 1

    print("{} comandos de ventilador enviados".format(fan_commands))


def on_connect(client, userdata, flags, rc):
    '''
    Función que se ejecuta cuando se conecta al bróker.
    '''
    print("Conectando al broker MQTT...", mqtt.connack_string(rc))


def on_disconnect(client: mqtt.Client, userdata, rc):
    '''
    Función que se ejecuta cuando se desconecta del broker.
    Intenta reconectar al bróker.
    '''
    print("Desconectado con mensaje:" + str(mqtt.connack_string(rc)))
    print("Reconectando...")
    client.reconnect()


def setup_mqtt():
    '''
    Configura el cliente MQTT para conectarse al broker.
    '''

    print("Iniciando cliente MQTT...", settings.MQTT_HOST, settings.MQTT_PORT)
    global client
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, settings.MQTT_USER_PUB)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        if settings.MQTT_USE_TLS:
            client.tls_set(ca_certs=settings.CA_CRT_PATH,
                           tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)

        client.username_pw_set(settings.MQTT_USER_PUB,
                               settings.MQTT_PASSWORD_PUB)
        client.connect(settings.MQTT_HOST, settings.MQTT_PORT)
        client.loop_start()

    except Exception as e:
        print('Ocurrió un error al conectar con el bróker MQTT:', e)


def start_cron():
    '''
    Inicia el cron que se encarga de ejecutar la función analyze_data cada 5 minutos.
    '''
    print("Iniciando cron...")
    schedule.every(1).minutes.do(analyze_data)
    schedule.every(1).minutes.do(analyze_sustained_temperature)
    print("Servicio de control iniciado")
    while 1:
        schedule.run_pending()
        time.sleep(1)
