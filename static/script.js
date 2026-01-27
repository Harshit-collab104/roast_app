let selectedGame='clash_royale';

document.addEventListener('DOMContentLoaded',()=>{
    const buttons=document.querySelectorAll('.game-btn');


    buttons.forEach(button=>{
        button.addEventListener('click',()=>{
            if(button.classList.contains('disabled')) return;

            buttons.forEach(btn=>btn.classList.remove('active'));

            button.classList.add('active');

            selectedGame=button.getAttribute('data-game');

            console.log("Game switched to:", selectedGame);
        });
    });
});

async function getRoast() {
    const tag=document.getElementById('playerTag').value;
    const resultBox=document.getElementById('result-area');
    const roastText=document.getElementById('roastText');
    const btn=document.getElementById('roastBtn');

    if(!tag){
        return alert("Please enter a tag!");
    }        
    resultBox.classList.remove('hidden');
    roastText.innerText="Generating the spirits of bad gameplay... 🔥";
    btn.disabled=true;
    console.log("Sending data:", { game_id: selectedGame, player_id: tag });
    try {
        const response=await fetch('/api/roast',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({game_id:selectedGame, player_id:tag})
        });
        if(!response.ok){
            const err =await response.json();
            console.error("Error response:", err);
            const errorMessage = typeof err.detail === 'object' 
                ? JSON.stringify(err.detail, null, 2) 
                : err.detail;
            throw new Error(errorMessage);
        }

        const reader=response.body.getReader();
        const decoder=new TextDecoder();
        roastText.innerText="";

        while(true){
            const {done, value}=await reader.read();
            if(done) break;
            const chunk=decoder.decode(value);
            roastText.innerText+=chunk;
        }
    }
    catch (error) {
        roastText.innerText="Error: " + error.message;
    }
    finally {
        btn.disabled=false;
    }
}