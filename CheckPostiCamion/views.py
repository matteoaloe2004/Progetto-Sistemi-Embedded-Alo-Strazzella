from flask import Blueprint, jsonify, render_template, request, redirect
from database import get_db_connection

# Blueprint per le viste
views = Blueprint("views", __name__)

@views.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # IMPORTANTE: Restituisce i risultati come dizionari
    cursor.execute("SELECT * FROM slots")
    slots = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", slots=slots)   

@views.route("/get_slots", methods=["GET"])
def get_slots():
    """
    Ottieni tutti i posti dalla tabella 'slots' e restituisci i dati come JSON.
    """
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Errore nella connessione al database'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM slots")  # Recupera tutti i posti dalla tabella
        slots = cursor.fetchall()
        return jsonify(slots)  # Restituisce i dati come JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@views.route("/sospendi/<int:posto_id>", methods=["POST"])
def sospendi_posto(posto_id):
    """
    Sospendi o riattiva un posto specifico in base al suo ID.
    """
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Errore nella connessione al database'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        # Controlla se il posto esiste
        cursor.execute("SELECT * FROM slots WHERE id = %s", (posto_id,))
        posto = cursor.fetchone()

        if posto:
            # Cambia il valore della colonna 'sospeso'
            cursor.execute("UPDATE slots SET sospeso = NOT sospeso WHERE id = %s", (posto_id,))
            connection.commit()

            # Ottieni il nuovo valore aggiornato
            cursor.execute("SELECT sospeso, status FROM slots WHERE id = %s", (posto_id,))
            updated_posto = cursor.fetchone()

            return jsonify({
                'sospeso': updated_posto['sospeso'],
                'stato': updated_posto['status']
            })
        else:
            return jsonify({'error': 'Posto non trovato'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@views.route("/reset", methods=["POST"])
def reset_slot():
    """
    Reimposta lo stato di uno slot specifico (impostandolo a 0).
    """
    slot_id = request.form.get("slot")

    if not slot_id:
        return jsonify({'error': 'ID dello slot non fornito'}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Errore nella connessione al database'}), 500

    cursor = connection.cursor()
    try:
        # Aggiorna lo stato dello slot
        cursor.execute("UPDATE slots SET status = 0 WHERE id = %s", (slot_id,))
        connection.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return redirect("/")
