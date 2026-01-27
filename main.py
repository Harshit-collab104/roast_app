from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services.games.clash_royale import ClashRoyale
from services.ai_engine import generate_roast_stream
from services.games.valorant import Valorant
app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

class RoastRequest(BaseModel):
    game_id:str
    player_id:str

Games={
    "clash_royale": ClashRoyale(),
    "valorant":Valorant()
}


@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")

@app.post("/api/roast")
async def roast_player(request:RoastRequest):
    if request.game_id not in Games:
        raise HTTPException(status_code=404,detail="Unsupported Game ID")
    
    handler=Games[request.game_id]

    try:
        raw_data=handler.get_player_data(request.player_id)

        context=handler.format_data(raw_data)

        return StreamingResponse(
            generate_roast_stream(request.game_id,context,"Roast this player mercilessly!"),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0", port=8000,reload=True)