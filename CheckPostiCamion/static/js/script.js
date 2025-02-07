// Oggetto per tenere traccia degli slot sospesi
const suspendedSlots = new Set();

// Mappa per tenere traccia dello stato precedente degli slot sospesi
const previousStates = new Map();

// Connessione al broker MQTT
const client = mqtt.connect('wss://833019dc465b486ba94ff7236c3f9795.s1.eu.hivemq.cloud:8884/mqtt', {
    username: "MqttTest1",
    password: "MqttTest1",
});

client.on('connect', function () {
    console.log('Connesso al broker MQTT');
    client.subscribe('vem/slots', function (err) {
        if (!err) {
            console.log('Sottoscritto al topic vem/slots');
        }
    });
});

// Funzione per aggiornare la visualizzazione dello stato di un posto
function updateSlot(slotId, status) {
    // Se lo slot è sospeso, ignora completamente l'aggiornamento
    if (suspendedSlots.has(slotId)) {
        return;
    }

    const slotElement = document.querySelector(`#slot-${slotId}`);
    const ledElement = document.querySelector(`#led-${slotId}`);

    if (slotElement && ledElement) {
        if (status === "1") {
            slotElement.innerText = "Occupato";
            ledElement.style.backgroundColor = "red"; // LED rosso
        } else {
            slotElement.innerText = "Libero";
            ledElement.style.backgroundColor = "green"; // LED verde
        }
        
        // Aggiorna lo stato precedente solo se il posto non è sospeso
        previousStates.set(slotId, status);
    } else {
        console.error(`Elemento non trovato per slot ID: ${slotId}`);
    }
}

// Gestione della ricezione di messaggi MQTT
client.on('message', function (topic, message) {
    const msg = message.toString().trim();
    
    // Parsing del messaggio in formato "id: 1 Status :1"
    const match = msg.match(/id:\s*(\d+)\s*Status\s*:\s*(\d+)/);
    if (match) {
        const slotId = match[1];
        const status = match[2];

        // Se lo slot NON è sospeso, aggiorna la UI normalmente
        updateSlot(slotId, status);
    } else {
        console.error("Formato del messaggio non valido:", msg);
    }
});

// Funzione per caricare i posti iniziali dal database
function loadSlots() {
    fetch('/get_slots')
        .then(response => response.json())
        .then(slots => {
            const tableBody = document.querySelector("#parking tbody");
            tableBody.innerHTML = ""; // Pulisce la tabella

            slots.forEach(slot => {
                // Salva lo stato iniziale nello storage locale
                previousStates.set(slot.id, slot.status);

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${slot.id}</td>
                    <td id="slot-${slot.id}">${slot.status === "1" ? "Occupato" : "Libero"}</td>
                    <td>
                        <div id="led-${slot.id}" class="led" style="background-color: ${slot.status === "1" ? "red" : "green"};"></div>
                    </td>
                    <td>
                        <button class="suspend-btn" data-id="${slot.id}">Sospendi</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // Aggiungi l'evento click per il bottone sospendi/ripristina
            document.querySelectorAll('.suspend-btn').forEach(button => {
                button.addEventListener('click', function () {
                    const slotId = this.getAttribute('data-id');
                    const slotElement = document.querySelector(`#slot-${slotId}`);
                    const ledElement = document.querySelector(`#led-${slotId}`);

                    if (suspendedSlots.has(slotId)) {
                        //  Ripristina lo stato precedente
                        suspendedSlots.delete(slotId);
                        this.innerText = "Sospendi";
                        console.log(`Slot ${slotId} ripristinato`);

                        // Recupera lo stato precedente e lo applica
                        const previousStatus = previousStates.get(slotId);
                        slotElement.innerText = previousStatus === "1" ? "Occupato" : "Libero";
                        ledElement.style.backgroundColor = previousStatus === "1" ? "red" : "green";
                    } else {
                        // Sospende lo slot (colore giallo + "Sospeso")
                        suspendedSlots.add(slotId);
                        this.innerText = "Ripristina";
                        console.log(`Slot ${slotId} sospeso`);

                        // Salva lo stato attuale prima di sospendere
                        if (!previousStates.has(slotId)) {
                            previousStates.set(slotId, slotElement.innerText === "Occupato" ? "1" : "0");
                        }

                        slotElement.innerText = "Sospeso";
                        ledElement.style.backgroundColor = "yellow"; // LED giallo per slot sospeso
                    }
                });
            });
        })
        .catch(error => console.error("Errore nel caricamento dei posti:", error));
}

// Caricamento iniziale dei posti
loadSlots();
