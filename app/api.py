from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
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

@app.get("/hi")
def hi():
    return {"Hello": "World"}

# HUD
@app.post("/update-snapshot")
def update_snapshot(loc: Optional[str] = Query(None, description="The snapshot location")):
    return match.updateSnapshot(loc)


@app.get("/player-info")
def player_info():
    return match.get_player_info_from_loading_screen()


@app.get("/update-during-round")
def update_during_round():
    return match.updateDuringRound()


# End Game Stats
@app.get("/match-stats")
def match_stats(loc: Optional[str] = Query(None, description="The image location")):
    return stats.get_match_stats(loc)