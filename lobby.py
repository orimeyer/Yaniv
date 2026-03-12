"""
lobby.py - Manages connected players and open games
"""
from typing import List, Dict, Tuple, Optional

import uuid
from game import Game
from player import Player


class Lobby:
    """Manages all active games and connected players"""

    def __init__(self):
        self.connected_players: Dict[str, Player] = {}  # uid -> Player
        self.games: Dict[str, Game] = {}                # game_id -> Game

    # ── Player management ────────────────────────────────────────────────────

    def player_connected(self, uid: str, display_name: str) -> Player:
        """Called when a player connects - adds them to the lobby"""
        player = Player(uid, display_name)
        player.is_connected = True
        self.connected_players[uid] = player
        return player

    def player_disconnected(self, uid: str):
        """Called when a player disconnects"""
        if uid in self.connected_players:
            self.connected_players[uid].is_connected = False

    def get_connected_players(self) -> List[dict]:
        """Returns a list of currently connected players for display"""
        return [
            p.public_info()
            for p in self.connected_players.values()
            if p.is_connected
        ]

    # ── Game management ──────────────────────────────────────────────────────

    def create_game(self, creator_uid: str) -> Game:
        """Creates a new game and adds the creator as the first player"""
        if creator_uid not in self.connected_players:
            raise ValueError("Player is not connected")

        game_id = str(uuid.uuid4())[:8]
        game = Game(game_id)
        self.games[game_id] = game

        # The creator automatically joins the game they created
        creator = self.connected_players[creator_uid]
        game.add_player(creator)

        return game

    def join_game(self, game_id: str, uid: str) -> Game:
        """Adds a connected player to an existing open game"""
        if game_id not in self.games:
            raise ValueError(f"Game {game_id} does not exist")
        if uid not in self.connected_players:
            raise ValueError("Player is not connected")

        game = self.games[game_id]
        if game.status != "waiting":
            raise ValueError("This game has already started")

        player = self.connected_players[uid]
        game.add_player(player)
        return game

    def get_open_games(self) -> List[dict]:
        """Returns a list of games that are still open for players to join"""
        result = []
        for game in self.games.values():
            if game.status == "waiting":
                result.append({
                    "game_id": game.game_id,
                    "players": [p.public_info() for p in game.players],
                    "player_count": len(game.players),
                })
        return result

    def remove_finished_games(self):
        """Cleans up completed games from memory"""
        self.games = {
            gid: g for gid, g in self.games.items()
            if g.status != "finished"
        }
