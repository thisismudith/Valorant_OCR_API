import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect,  Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from end_game import Stats
from match import Match

app = FastAPI()
stats = Stats()
match = Match()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Remove any path from the URL
    allow_credentials=True,
    allow_methods=["*"],  # Use ["*"] to allow all methods, or specify the needed methods
    allow_headers=["*"],  # Use ["*"] to allow all headers, or specify the required headers
)

# --- Endpoints ---


# POST method for updating snapshot for match HUD
@app.post("/update-snapshot")
def update_snapshot(loc: Optional[str] = Query(None, description="The snapshot location")):
    return match.updateSnapshot(loc)


# GET method for end-game-stats
@app.get("/match-stats")
def match_stats(loc: Optional[str] = Query(None, description="The image location")):
    return stats.get_match_stats(loc)


# GET method for player-info for match HUD
@app.get("/player-info")
def player_info():
    return match.get_player_info_from_loading_screen()



# Match HUD (Web Socket)
active_connections: List[WebSocket] = []


async def connect_websocket(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)


# Function to remove a WebSocket connection
def disconnect_websocket(websocket: WebSocket):
    active_connections.remove(websocket)


@app.websocket("/update-during-round")
async def websocket_update_during_round(websocket: WebSocket):
    await connect_websocket(websocket)

    try:
        data = await websocket.receive_text()

        if data == "start":
        # Obtain player info from loading screen
            # match.get_player_info_from_loading_screen()
            firstTime = True

            # Loop snapshot updates
            print("Starting!")
            while True:
                await websocket.send_json(match.updateDuringRound(firstTime))
                if firstTime: firstTime = False

                try:
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    if message == "stop":
                        print("Stopping!")
                        break
                except asyncio.TimeoutError:
                    pass

    except WebSocketDisconnect:
        disconnect_websocket(websocket)