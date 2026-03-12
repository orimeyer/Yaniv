"""
card.py - Represents a single playing card
"""

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

RANK_POINTS = {
    'A': 1, '2': 2, '3': 3, '4': 4, '5': 5,
    '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10
}

# Maps each rank to its position index (used for sequence validation)
RANK_ORDER = {rank: i for i, rank in enumerate(RANKS)}


class Card:
    """Represents a single playing card"""

    def __init__(self, rank: str, suit: str):
        """
        rank: 'A', '2', ..., 'K', or 'Joker'
        suit: 'Hearts', 'Diamonds', 'Clubs', 'Spades', or None for Joker
        """
        self.rank = rank
        self.suit = suit
        self.is_joker = (rank == 'Joker')

    @property
    def points(self) -> int:
        """Returns the point value of this card"""
        if self.is_joker:
            return 0
        return RANK_POINTS[self.rank]

    @property
    def rank_order(self) -> int:
        """Returns the rank index, used for sequence checking"""
        if self.is_joker:
            return -1
        return RANK_ORDER[self.rank]

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __repr__(self):
        if self.is_joker:
            return "Joker"
        return f"{self.rank}_{self.suit[0]}"  # e.g. 7_H, K_D

    def to_dict(self) -> dict:
        """Converts card to a dictionary (used for network transmission)"""
        return {"rank": self.rank, "suit": self.suit}

    @staticmethod
    def from_dict(data: dict) -> "Card":
        """Creates a Card object from a dictionary"""
        return Card(data["rank"], data["suit"])
