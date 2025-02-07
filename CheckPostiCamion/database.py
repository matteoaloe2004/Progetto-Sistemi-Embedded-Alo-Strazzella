import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        # Connessione al database
        connection = mysql.connector.connect(
            host='localhost',  # Cambia se usi un server diverso
            user='root',       # Il tuo username
            password='',       # La tua password
            database='checkposti'  # Nome del database
        )

        if connection.is_connected():
            print("Connessione al database riuscita!")
            return connection

    except Error as e:
        print(f"Errore durante la connessione al database: {e}")
        return None

 # Funzione per la creazione delle tabelle
def create_tables():
    connection = get_db_connection()
    if connection is None:
        print("Connessione fallita. Non posso creare le tabelle.")
        return

    try:
        cursor = connection.cursor()

        # Creazione della tabella 'slots' se non esiste
        cursor.execute("SHOW TABLES LIKE 'slots'")
        if not cursor.fetchone():
            print("Tabella 'slots' non esiste, la creo.")
            cursor.execute("""
                CREATE TABLE slots (
                    id INT NOT NULL PRIMARY KEY,
                    status VARCHAR(50) NOT NULL
                )
            """)
            print("Tabella 'slots' creata con successo.")

    except Error as e:
        print(f"Errore durante la creazione delle tabelle: {e}")
    finally:
        cursor.close()
        connection.close()
        print("Connessione al database chiusa.")

 # Funzione per la creazione dei posti predefiniti
def create_default_slots():
    """
    Crea esattamente 15 posti con stato 'libero' se non sono già presenti.
    """
    connection = get_db_connection()
    if connection is None:
        print("Errore nella connessione al database.")
        return

    cursor = connection.cursor()

    try:
        # Recupera il numero di posti già presenti nella tabella
        cursor.execute("SELECT COUNT(*) FROM slots")
        count = cursor.fetchone()[0]

        if count < 15:
            # Se ci sono meno di 15 posti, inserisci i restanti posti
            for i in range(count + 1, 16):  # Aggiungi dal posto successivo fino al 15esimo
                cursor.execute("INSERT INTO slots (id, status) VALUES (%s, %s)", (i, 'libero'))
            connection.commit()
            print(f"Ho aggiunto i posti mancanti fino al posto 15.")
        else:
            print("I 15 posti sono già presenti nel database.")
    except Error as e:
        print(f"Errore durante l'inserimento dei posti: {str(e)}")
    

 
def insert_slot_status(slot_id, status):
    connection = get_db_connection()
    if connection is None:
        print("Connessione fallita. Non posso inserire i dati.")
        return

    try:
        cursor = connection.cursor()
        
        # Inserisci il nuovo stato del posto
        cursor.execute("""
            INSERT INTO slots (id, status) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE status = %s
        """, (slot_id, status, status))

        connection.commit()
        print(f"Stato del posto {slot_id} aggiornato a {status} nel database.")
    except Error as e:
        print(f"Errore durante l'inserimento del dato: {e}")
    finally:
        cursor.close()
        connection.close()
        print("Connessione al database chiusa.")


# Esegui il codice per creare le tabelle e i 15 posti predefiniti
if __name__ == "__main__":
    create_tables()         # Crea la tabella se non esiste
    create_default_slots()  # Crea i posti mancanti fino a 15, se necessario
