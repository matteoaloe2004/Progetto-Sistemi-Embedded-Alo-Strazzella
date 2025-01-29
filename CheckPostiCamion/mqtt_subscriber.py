import paho.mqtt.client as mqtt
import mysql.connector
import json

# Configura il database MySQL
def get_db_connection():
    """
    Restituisce una connessione al database MySQL.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="checkposti"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Errore di connessione al database: {e}")
        return None

def update_slot(slot_id, status):
    """
    Aggiorna lo stato di uno slot nel database.
    """
    connection = get_db_connection()
    if not connection:
        print("Connessione al database fallita. Impossibile aggiornare lo slot.")
        return

    try:
        cursor = connection.cursor()
        query = "UPDATE slots SET status = %s WHERE id = %s"
        cursor.execute(query, (status, slot_id))
        connection.commit()
        print(f"Slot {slot_id} aggiornato con stato {status}.")
    except mysql.connector.Error as e:
        print(f"Errore durante l'aggiornamento dello slot: {e}")
    finally:
        cursor.close()
        connection.close()

# Funzione chiamata quando ci si connette al broker MQTT
def on_connect(client, userdata, flags, reason_code):
    """
    Callback per la connessione al broker MQTT.
    """
    if reason_code == 0:
        print("Connesso al broker MQTT con successo.")
        client.subscribe("vem/slots")
    else:
        print(f"Errore nella connessione al broker MQTT. Codice: {reason_code}")

# Funzione chiamata quando viene ricevuto un messaggio MQTT
def on_message(client, userdata, msg):
    """
    Callback per la gestione dei messaggi MQTT.
    """
    try:
        # Decodifica il payload JSON
        payload = json.loads(msg.payload)
        slot_id = payload.get("slotID")
        status = payload.get("status")

        if slot_id is None or status is None:
            print("Payload non valido. SlotID o Status mancante.")
            return

        # Aggiorna lo stato dello slot
        update_slot(slot_id, status)
    except json.JSONDecodeError:
        print("Errore nel decodificare il payload JSON.")
    except Exception as e:
        print(f"Errore durante la gestione del messaggio MQTT: {e}")

# Configura il client MQTT
client = mqtt.Client()
client.username_pw_set("Your_Username", "Your_Password")
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)  # Connessione SSL

# Collega le callback
client.on_connect = on_connect
client.on_message = on_message

try:
    # Connessione al broker MQTT
    client.connect("833019dc465b486ba94ff7236c3f9795.s1.eu.hivemq.cloud", 8883)
    print("Tentativo di connessione al broker MQTT...")
    client.loop_forever()
except Exception as e:
    print(f"Errore nella connessione al broker MQTT: {e}")
