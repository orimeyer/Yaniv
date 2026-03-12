"""
game.py - Manages a full Yaniv game session
"""
from typing import List, Dict, Tuple, Optional

from card import Card
from deck import Deck
from player import Player
from validator import Validator

CARDS_PER_PLAYER = 5
ASSAF_PENALTY = 30


class GameError(Exception):
    """Raised when a player attempts an illegal game action"""
    pass


class Game:
    """Manages a complete Yaniv game - rounds, turns, and scoring"""

    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: List[Player] = []
        self.deck = Deck()
        self.current_turn_index: int = 0
        self.round_number: int = 0
        self.status: str = "waiting"   # waiting | active | finished
        self.winner: Optional[Player] = None
        self._phase: str = "discard"   # discard | draw (sub-phases within a turn)

    # ── Player management ────────────────────────────────────────────────────

    def add_player(self, player: Player):
        """Adds a player to the game before it starts"""
        if self.status != "waiting":
            raise GameError("Cannot add players after the game has started")
        if len(self.players) >= 6:
            raise GameError("Game is full (maximum 6 players)")
        self.players.append(player)

    def start_game(self):
        """Starts the game and deals the first round"""
        if len(self.players) < 2:
            raise GameError("At least 2 players are required to start")
        self.status = "active"
        self._start_round()

    # ── Round management ─────────────────────────────────────────────────────

    def _start_round(self):
        """Starts a new round - shuffles and deals cards to all active players"""
        self.round_number += 1
        self.deck = Deck()
        self._phase = "discard"

        active_players = self._active_players()
        for player in active_players:
            player.hand = []
            player.receive_cards(self.deck.deal(CARDS_PER_PLAYER))

        # Flip one card to start the discard pile
        first_card = self.deck.draw_from_deck()
        self.deck.add_to_discard([first_card])

        # Rotate the starting player each round
        self.current_turn_index = self.current_turn_index % len(active_players)

    def _active_players(self) -> List[Player]:
        """Returns all players who have not been eliminated"""
        return [p for p in self.players if not p.is_eliminated]

    # ── Player actions ───────────────────────────────────────────────────────

    def discard(self, uid: str, cards: List[Card]) -> dict:
        """
        Player discards one or more cards.
        Returns an updated game state for broadcasting.
        """
        player = self._get_current_player(uid)
        if self._phase != "discard":
            raise GameError("It is currently the draw phase, not the discard phase")

        valid, reason = Validator.validate_discard(player.hand, cards)
        if not valid:
            raise GameError(reason)

        player.remove_cards(cards)
        self.deck.add_to_discard(cards)
        self._phase = "draw"

        return self._build_state_update()

    def draw_from_deck(self, uid: str) -> dict:
        """Player draws a card from the closed draw pile"""
        player = self._get_current_player(uid)
        if self._phase != "draw":
            raise GameError("It is currently the discard phase, not the draw phase")

        card = self.deck.draw_from_deck()
        player.add_card(card)
        self._end_turn()

        return self._build_state_update(drawn_by=uid)

    def draw_from_discard(self, uid: str, card: Card) -> dict:
        """Player draws a specific card from the discard pile"""
        player = self._get_current_player(uid)
        if self._phase != "draw":
            raise GameError("It is currently the discard phase, not the draw phase")

        valid, reason = Validator.validate_draw_from_discard(
            self.deck.top_discard, card
        )
        if not valid:
            raise GameError(reason)

        taken = self.deck.draw_from_discard(card)
        player.add_card(taken)
        self._end_turn()

        return self._build_state_update(drawn_by=uid)

    def declare_yaniv(self, uid: str) -> dict:
        """
        Player declares Yaniv.
        Returns the full round result including any Assaf penalty.
        """
        player = self._get_current_player(uid)
        if self._phase != "discard":
            raise GameError("Yaniv can only be declared during the discard phase")

        valid, reason = Validator.validate_yaniv(player.hand)
        if not valid:
            raise GameError(reason)

        return self._resolve_yaniv(declarer=player)

    # ── Yaniv resolution ─────────────────────────────────────────────────────

    def _resolve_yaniv(self, declarer: Player) -> dict:
        """Calculates the result of a Yaniv declaration, including Assaf checks"""
        active = self._active_players()
        declarer_sum = declarer.hand_sum

        # Assaf: another player has an equal or lower hand sum
        assaf_players = [
            p for p in active
            if p.uid != declarer.uid and p.hand_sum <= declarer_sum
        ]
        is_assaf = len(assaf_players) > 0

        # Apply scores for this round
        round_scores = {}
        for player in active:
            if player.uid == declarer.uid:
                points = ASSAF_PENALTY + declarer_sum if is_assaf else 0
            else:
                points = player.hand_sum
            round_scores[player.uid] = points
            player.add_score(points)

        # Check for newly eliminated players
        eliminated = [p for p in active if p.is_eliminated]

        # Check if the game is over (only one player remaining)
        remaining = self._active_players()
        if len(remaining) == 1:
            self.winner = remaining[0]
            self.status = "finished"

        result = {
            "event": "yaniv_result",
            "declarer": declarer.uid,
            "declarer_sum": declarer_sum,
            "is_assaf": is_assaf,
            "assaf_players": [p.uid for p in assaf_players],
            "round_scores": round_scores,
            "eliminated": [p.uid for p in eliminated],
            "players": [p.public_info() for p in self.players],
            "game_over": self.status == "finished",
            "winner": self.winner.uid if self.winner else None,
        }

        # Start the next round if the game continues
        if self.status != "finished":
            self._start_round()

        return result

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_current_player(self, uid: str) -> Player:
        """Returns the current player and verifies it is their turn"""
        active = self._active_players()
        if not active:
            raise GameError("No active players")
        current = active[self.current_turn_index % len(active)]
        if current.uid != uid:
            raise GameError(f"It is not your turn - it is {current.display_name}'s turn")
        return current

    def _end_turn(self):
        """Advances the turn to the next active player"""
        active = self._active_players()
        self.current_turn_index = (self.current_turn_index + 1) % len(active)
        self._phase = "discard"

    def _build_state_update(self, drawn_by: str = None) -> dict:
        """Builds a state snapshot to broadcast to all players (no hand contents)"""
        active = self._active_players()
        return {
            "event": "state_update",
            "current_turn": active[self.current_turn_index % len(active)].uid,
            "phase": self._phase,
            "discard_pile": self.deck.discard_pile_to_dict(),
            "players_public": [p.public_info() for p in self.players],
            "drawn_by": drawn_by,
            "round_number": self.round_number,
        }

    def get_private_state(self, uid: str) -> dict:
        """Returns a full state snapshot including the requesting player's hand"""
        player = next((p for p in self.players if p.uid == uid), None)
        if not player:
            raise GameError(f"Player {uid} not found")
        state = self._build_state_update()
        state["my_hand"] = player.private_info()
        return state
