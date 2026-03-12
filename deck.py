"""
deck.py - Manages the draw pile and discard pile
"""
from typing import List, Dict, Tuple, Optional

import random
from card import Card, SUITS, RANKS


class Deck:
    """Manages the closed draw pile and the open discard pile"""

    def __init__(self):
        self.draw_pile: List[Card] = []
        self.discard_pile: List[Card] = []  # cards from the last discard action
        self._build()

    def _build(self):
        """Builds and shuffles a fresh 54-card deck (52 + 2 Jokers)"""
        cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        cards.append(Card('Joker', None))
        cards.append(Card('Joker', None))
        random.shuffle(cards)
        self.draw_pile = cards
        self.discard_pile = []

    def deal(self, num_cards: int) -> List[Card]:
        """Deals a number of cards from the top of the draw pile"""
        if len(self.draw_pile) < num_cards:
            self._reshuffle()
        dealt = self.draw_pile[:num_cards]
        self.draw_pile = self.draw_pile[num_cards:]
        return dealt

    def draw_from_deck(self) -> Card:
        """Draws one card from the closed draw pile"""
        if not self.draw_pile:
            self._reshuffle()
        return self.draw_pile.pop(0)

    def draw_from_discard(self, card: Card) -> Card:
        """
        Takes a specific card from the discard pile.
        Raises an error if the card is not currently in the discard pile.
        """
        if card not in self.discard_pile:
            raise ValueError(f"Card {card} is not in the discard pile")
        self.discard_pile.remove(card)
        return card

    def add_to_discard(self, cards: List[Card]):
        """Replaces the discard pile with the newly discarded cards"""
        self.discard_pile = cards

    def _reshuffle(self):
        """Reshuffles the discard pile into a new draw pile when deck runs out"""
        if not self.discard_pile:
            raise RuntimeError("No cards left in deck or discard pile")
        # Keep the top discard card visible, shuffle the rest back
        top = self.discard_pile[-1]
        self.draw_pile = self.discard_pile[:-1]
        random.shuffle(self.draw_pile)
        self.discard_pile = [top]

    @property
    def top_discard(self) -> List[Card]:
        """Returns the currently visible cards on the discard pile"""
        return self.discard_pile

    def discard_pile_to_dict(self) -> List[dict]:
        """Converts discard pile to a list of dicts for network transmission"""
        return [c.to_dict() for c in self.discard_pile]
