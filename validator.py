"""
validator.py - Validates all player moves according to Yaniv rules
"""
from typing import List, Dict, Tuple, Optional

from card import Card


class Validator:
    """Responsible for checking the legality of every action in the game"""

    # ── Discard validation ───────────────────────────────────────────────────

    @staticmethod
    def validate_discard(hand: List[Card], cards_to_discard: List[Card]) -> Tuple[bool, str]:
        """
        Checks whether the cards a player wants to discard are:
        1. Actually in their hand
        2. A legal combination

        Returns: (is_valid, explanation)
        """
        # Verify all cards exist in hand
        hand_copy = hand.copy()
        for card in cards_to_discard:
            if card not in hand_copy:
                return False, f"Card {card} is not in your hand"
            hand_copy.remove(card)

        if len(cards_to_discard) == 0:
            return False, "Must discard at least one card"

        # A single card is always a valid discard
        if len(cards_to_discard) == 1:
            return True, "Single card - valid"

        # Check for pair / three-of-a-kind / four-of-a-kind
        if Validator._is_same_value(cards_to_discard):
            return True, "Pair / set - valid"

        # Check for a sequence (run) of 3 or more
        if len(cards_to_discard) >= 3 and Validator._is_sequence(cards_to_discard):
            return True, "Sequence - valid"

        return False, "Invalid combination - must be a pair/set or a sequence of 3+"

    @staticmethod
    def _is_same_value(cards: List[Card]) -> bool:
        """Returns True if all cards share the same rank (Joker matches any rank)"""
        non_jokers = [c for c in cards if not c.is_joker]
        if not non_jokers:
            return True  # All Jokers
        ranks = set(c.rank for c in non_jokers)
        return len(ranks) == 1

    @staticmethod
    def _is_sequence(cards: List[Card]) -> bool:
        """Returns True if cards form a valid run (same suit, consecutive ranks)"""
        non_jokers = [c for c in cards if not c.is_joker]
        joker_count = len(cards) - len(non_jokers)

        if not non_jokers:
            return True  # All Jokers can form any sequence

        # All non-joker cards must share the same suit
        suits = set(c.suit for c in non_jokers)
        if len(suits) > 1:
            return False

        # Sort by rank order and count the gaps that Jokers must fill
        sorted_cards = sorted(non_jokers, key=lambda c: c.rank_order)
        orders = [c.rank_order for c in sorted_cards]

        gaps = 0
        for i in range(1, len(orders)):
            diff = orders[i] - orders[i - 1]
            if diff == 0:
                return False  # Duplicate ranks are not allowed
            gaps += diff - 1  # Each gap of 1 needs one Joker to fill

        return gaps <= joker_count

    # ── Draw from discard validation ─────────────────────────────────────────

    @staticmethod
    def validate_draw_from_discard(
        discard_pile: List[Card], card_to_take: Card
    ) -> Tuple[bool, str]:
        """
        Checks whether a player is allowed to take a specific card
        from the discard pile.

        Rules:
        - Single card: may only take that one card
        - Pair / set: may take any card from the pile
        - Sequence: may only take one of the two endpoint cards (not the middle)
        """
        if not discard_pile:
            return False, "Discard pile is empty"

        if card_to_take not in discard_pile:
            return False, f"Card {card_to_take} is not in the discard pile"

        if len(discard_pile) == 1:
            return True, "Single card - valid"

        if Validator._is_same_value(discard_pile):
            return True, "Pair/set - any card may be taken"

        if Validator._is_sequence(discard_pile):
            allowed = Validator._get_sequence_endpoints(discard_pile)
            if card_to_take in allowed:
                return True, "Endpoint of sequence - valid"
            return False, "In a sequence, only the two endpoint cards may be taken"

        return False, "Unrecognized discard pile format"

    @staticmethod
    def _get_sequence_endpoints(cards: List[Card]) -> List[Card]:
        """Returns the two outermost cards of a sequence (Jokers included as endpoints)"""
        non_jokers = [c for c in cards if not c.is_joker]
        if not non_jokers:
            return []
        sorted_cards = sorted(non_jokers, key=lambda c: c.rank_order)
        endpoints = [sorted_cards[0], sorted_cards[-1]]
        # Jokers at either end are also valid to take
        jokers = [c for c in cards if c.is_joker]
        return endpoints + jokers

    # ── Yaniv declaration validation ─────────────────────────────────────────

    @staticmethod
    def validate_yaniv(hand: List[Card]) -> Tuple[bool, str]:
        """Checks whether a player may declare Yaniv (hand sum must be 7 or less)"""
        total = sum(c.points for c in hand)
        if total <= 7:
            return True, f"Yaniv is valid - hand sum is {total}"
        return False, f"Cannot declare Yaniv - hand sum is {total} (must be 7 or less)"
