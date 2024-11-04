from fastapi import FastAPI, Query
from typing import Optional
from app.end_game import Stats

app = FastAPI()
stats = Stats()


# HUD
@app.post("/update-snapshot")
def update_snapshot(loc: Optional[str] = Query(None, description="The snapshot location")):
    return stats.updateSnapshot(loc)


@app.get("/player-info")
def player_info():
    return stats.get_player_info_from_loading_screen()


@app.get("/update-during-round")
def update_during_round():
    stats.updateSnapshot()
    return stats.updateDuringRound()


# End Game Stats
@app.get("/match-stats")
def match_stats(loc: Optional[str] = Query(None, description="The image location")):
    return stats.get_match_stats(loc)

