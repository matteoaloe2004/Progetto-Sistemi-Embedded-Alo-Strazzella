// Oggetto per tenere traccia degli slot sospesi
const suspendedSlots = new Set();

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
    // Se lo slot è sospeso, non fare nulla
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

        updateSlot(slotId, status); // Aggiorna solo lo slot specifico
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

            // Aggiungi l'evento click per il bottone sospendi
            document.querySelectorAll('.suspend-btn').forEach(button => {
                button.addEventListener('click', function () {
                    const slotId = this.getAttribute('data-id');
                    if (suspendedSlots.has(slotId)) {
                        // Se lo slot è già sospeso, attivalo (accendi il pulsante)
                        suspendedSlots.delete(slotId);
                        this.innerText = "Sospendi";
                        console.log(`Slot ${slotId} ripristinato`);
                    } else {
                        // Se lo slot non è sospeso, sospendilo (spegnere il pulsante)
                        suspendedSlots.add(slotId);
                        this.innerText = "Ripristina";
                        console.log(`Slot ${slotId} sospeso`);
                    }
                });
            });
        })
        .catch(error => console.error("Errore nel caricamento dei posti:", error));
}

// Caricamento iniziale dei posti
loadSlots();
