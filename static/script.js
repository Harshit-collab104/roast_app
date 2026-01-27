let selectedGame = "clash_royale";

document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".game-btn");
    const input = document.getElementById("playerTag");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            // Remove active from all
            buttons.forEach(btn => btn.classList.remove("active"));

            // Activate clicked
            button.classList.add("active");

            selectedGame = button.dataset.game;

            // Update placeholder
            if (selectedGame === "valorant") {
                input.placeholder = "Enter Riot ID (e.g. TenZ#0000)";
            } else {
                input.placeholder = "Enter Player Tag (e.g. #2P090...)";
            }

            console.log("Game selected:", selectedGame);
        });
    });
});

async function getRoast() {
    const tag = document.getElementById("playerTag").value;
    const resultBox = document.getElementById("result-area");
    const roastText = document.getElementById("roastText");
    const btn = document.getElementById("roastBtn");

    if (!tag) {
        alert("Please enter a player tag!");
        return;
    }

    resultBox.classList.remove("hidden");
    roastText.innerText = "Generating the spirits of bad gameplay... 🔥";
    btn.disabled = true;

    try {
        const response = await fetch("/api/roast", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: selectedGame,
                player_id: tag
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "API Error");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        roastText.innerText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            roastText.innerText += decoder.decode(value);
        }
    } catch (error) {
        roastText.innerText = "Error: " + error.message;
    } finally {
        btn.disabled = false;
    }
}
