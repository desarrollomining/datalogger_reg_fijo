document.addEventListener("DOMContentLoaded", () => {
    const app = document.getElementById("app");

    const header = document.createElement("div");
    header.className = "page-header";

    const title = document.createElement("h1");
    title.innerText = "Control Regadío Fijo 2";

    header.appendChild(title);
    app.appendChild(header);

    const topActions = document.createElement("div");
    topActions.className = "top-actions";

    const actions = [
        { label: "Encender todos", action: "ON", class: "btn-on" },
        { label: "Apagar todos", action: "OFF", class: "btn-off" },
        { label: "Sincronizar todos", action: "SETS", class: "btn-sets" }
    ];

    actions.forEach(({ label, action, class: cls }) => {
        const btn = document.createElement("button");
        btn.className = `btn-valvula ${cls}`;
        btn.innerText = label;

        btn.addEventListener("click", async () => {
            const command = buildAllCommand(action);
            await sendCommand(command, btn);
        });

        topActions.appendChild(btn);
    });

    app.appendChild(topActions);

    const grid = document.createElement("div");
    grid.className = "valvulas-grid";

    for (let i = 1; i <= 12; i++) {
        const card = document.createElement("div");
        card.className = "valvula-card";

        const title = document.createElement("h5");
        title.className = "valvula-title";
        title.innerText = `Válvula ${i}`;

        const buttons = document.createElement("div");
        buttons.className = "valvula-buttons";

        const actions = [
            { label: "Encender", action: "ON" },
            { label: "Apagar", action: "OFF" },
            { label: "Sincronizar", action: "SETS" },
            { label: "Live", action: "LIVE" },
            { label: "Reset", action: "SETR" }
        ];

        actions.forEach(({ label, action }) => {
            const btn = document.createElement("button");
            btn.className = `btn-valvula btn-${action.toLowerCase()}`;
            btn.innerText = label;

            btn.addEventListener("click", async () => {
                const command = buildCommand(i, action);
                await sendCommand(command, btn);
            });

            buttons.appendChild(btn);
        });

        card.appendChild(title);
        card.appendChild(buttons);
        grid.appendChild(card);
    }

    app.appendChild(grid);

    const logContainer = document.createElement("div");
    logContainer.className = "log-console";
    logContainer.id = "logConsole";
    logContainer.innerText = "Esperando logs...\n";

    const logWrapper = document.createElement("div");
    logWrapper.className = "valvula-card";

    const logTitle = document.createElement("h5");
    logTitle.className = "valvula-title";
    logTitle.innerText = "Log SERIAL";

    logWrapper.appendChild(logTitle);
    logWrapper.appendChild(logContainer);

    app.appendChild(logWrapper);
});

function buildBitArray(valveIndex, value) {
    const bits = Array(12).fill("x");
    bits[valveIndex - 1] = value;
    return bits.join("");
}

function buildCommand(valveIndex, action) {
    switch (action) {
        case "ON":
            return buildBitArray(valveIndex, "1");

        case "OFF":
            return buildBitArray(valveIndex, "0");

        case "SETS":
            return `SETS:${buildBitArray(valveIndex, "1")}`;

        case "LIVE":
            return `LIVE:${buildBitArray(valveIndex, "1")}`;

        case "SETR":
            return `SETR:${buildBitArray(valveIndex, "1")}`;

        default:
            throw new Error("Acción desconocida");
    }
}

async function sendCommand(command, button) {
    try {
        button.disabled = true;

        const response = await fetch("/write", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ data: command })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Error desconocido");
        }

        console.log("Comando enviado:", command);

    } catch (error) {
        console.error("Error:", error.message);
        alert(error.message);
    } finally {
        button.disabled = false;
    }
}

async function fetchLog() {
    try {
        const response = await fetch("/log");
        const result = await response.json();

        const consoleDiv = document.getElementById("logConsole");
        consoleDiv.innerText = result.join("\n");

        consoleDiv.scrollTop = consoleDiv.scrollHeight;

    } catch (err) {
        console.error("Error leyendo log:", err);
    }
}

setInterval(fetchLog, 1000); 

function buildAllCommand(action) {
    const bits = Array(12).fill(
        action === "OFF" ? "0" : "1"
    ).join("");

    switch (action) {
        case "ON":
            return bits;

        case "OFF":
            return bits;

        case "SETS":
            return `SETS:${bits}`;

        default:
            throw new Error("Acción desconocida");
    }
}