from flask import Flask
from views import views
import threading
import paho.mqtt.client as mqtt
import json
from database import create_default_slots, insert_slot_status  # Assicurati che questa funzione sia correttamente implementata

# Configurazione MQTT
MQTT_BROKER_HOST = "833019dc465b486ba94ff7236c3f9795.s1.eu.hivemq.cloud"
MQTT_BROKER_PORT = 8883
MQTT_TOPIC = "vem/slots"
MQTT_USER = "MqttTest1"
MQTT_PASSWORD = "MqttTest1"

# Funzione per la connessione al broker MQTT
def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connesso a {MQTT_BROKER_HOST} con codice {reason_code}")
    client.subscribe(MQTT_TOPIC)

# Funzione per la gestione dei messaggi ricevuti
def on_message(client, userdata, msg):
    print(f"Messaggio ricevuto su {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        print(f"Dati ricevuti: {data}")  # Aggiungi questa stampa di debug
        slot_id = data.get("slotID")
        status = data.get("status")
        if slot_id is not None and status is not None:
            insert_slot_status(slot_id, status)  # Assicurati che questa funzione sia definita
            print(f"Stato aggiornato: Slot {slot_id} -> {status}")
    except json.JSONDecodeError as e:
        print(f"Errore di parsing JSON: {e}")

# Creazione dell'app Flask
app = Flask(__name__)

# Imposta il blueprint
app.register_blueprint(views, url_prefix="/")

# Configura il client MQTT
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connessione al broker MQTT
def mqtt_thread():
    mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    mqtt_client.loop_forever()  # loop_forever è un blocco che gestisce i messaggi in modo continuo

# Avvio di MQTT in un thread separato
mqtt_threading = threading.Thread(target=mqtt_thread)
mqtt_threading.daemon = True  # Questo assicura che il thread si chiuda quando l'app Flask si chiude
mqtt_threading.start()

# Avvio dell'app Flask
if __name__ == "__main__":
    create_default_slots()
    app.run(debug=True, port=8000)
