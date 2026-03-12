"""
player.py - Represents a player in the game
"""
from typing import List, Dict, Tuple, Optional

from card import Card

ELIMINATION_SCORE = 100
# If a player lands exactly on one of these scores, they get a bonus deduction
BONUS_SCORES = {50: 50, 100: 50}


class Player:
    """Represents a player - holds their hand and cumulative score"""

    def __init__(self, uid: str, display_name: str):
        self.uid = uid
        self.display_name = display_name
        self.hand: List[Card] = []
        self.score: int = 0
        self.is_eliminated: bool = False
        self.is_connected: bool = True

    # ── Hand management ──────────────────────────────────────────────────────

    def receive_cards(self, cards: List[Card]):
        """Adds a list of cards to the player's hand"""
        self.hand.extend(cards)

    def remove_cards(self, cards: List[Card]):
        """Removes specific cards from the player's hand (after discarding)"""
        for card in cards:
            if card not in self.hand:
                raise ValueError(f"Card {card} is not in {self.display_name}'s hand")
            self.hand.remove(card)

    def add_card(self, card: Card):
        """Adds a single card to the player's hand (after drawing)"""
        self.hand.append(card)

    @property
    def hand_sum(self) -> int:
        """Returns the total point value of all cards in hand"""
        return sum(c.points for c in self.hand)

    @property
    def hand_size(self) -> int:
        """Returns the number of cards in hand"""
        return len(self.hand)

    # ── Scoring ──────────────────────────────────────────────────────────────

    def add_score(self, points: int):
        """
        Adds points to the player's score and handles special cases:
        - Landing exactly on 50: deduct 50 (back to 0)
        - Landing exactly on 100: deduct 50 (saved at 50)
        - Reaching 100 or more: player is eliminated
        """
        self.score += points

        if self.score in BONUS_SCORES:
            self.score -= BONUS_SCORES[self.score]
            return

        if self.score >= ELIMINATION_SCORE:
            self.is_eliminated = True

    # ── Data for broadcast ───────────────────────────────────────────────────

    def public_info(self) -> dict:
        """Returns data visible to all players (does NOT include hand contents)"""
        return {
            "uid": self.uid,
            "display_name": self.display_name,
            "score": self.score,
            "hand_size": self.hand_size,
            "is_eliminated": self.is_eliminated,
            "is_connected": self.is_connected,
        }

    def private_info(self) -> dict:
        """Returns full data including hand - sent only to this player"""
        return {
            **self.public_info(),
            "hand": [c.to_dict() for c in self.hand],
            "hand_sum": self.hand_sum,
        }

    def __repr__(self):
        return f"Player({self.display_name}, score={self.score}, hand={self.hand})"
