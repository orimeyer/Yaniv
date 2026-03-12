"""
tests.py - Unit tests for all Yaniv game logic
Run with: python tests.py
"""

from card import Card
from deck import Deck
from player import Player
from validator import Validator
from game import Game


def test(name: str, condition: bool):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {status}: {name}")


# ── Card tests ───────────────────────────────────────────────────────────────

print("\n=== Card Tests ===")
c = Card('7', 'Hearts')
test("7 of Hearts has value 7", c.points == 7)
test("Not a Joker", not c.is_joker)
test("Repr format", repr(c) == "7_H")

joker = Card('Joker', None)
test("Joker has 0 points", joker.points == 0)
test("is_joker is True", joker.is_joker)

k = Card('K', 'Spades')
test("King = 10 points", k.points == 10)
a = Card('A', 'Clubs')
test("Ace = 1 point", a.points == 1)

# ── Deck tests ───────────────────────────────────────────────────────────────

print("\n=== Deck Tests ===")
deck = Deck()
test("Full deck has 54 cards (52 + 2 Jokers)", len(deck.draw_pile) == 54)

hand = deck.deal(5)
test("Dealing 5 cards returns 5 cards", len(hand) == 5)
test("49 cards remain after dealing 5", len(deck.draw_pile) == 49)

drawn = deck.draw_from_deck()
test("Drawing one card returns a Card object", isinstance(drawn, Card))

deck.add_to_discard([Card('5', 'Hearts'), Card('5', 'Diamonds')])
test("Discard pile updated correctly", len(deck.top_discard) == 2)

# ── Validator discard tests ──────────────────────────────────────────────────

print("\n=== Validator - Discard Tests ===")

hand = [Card('7', 'Hearts'), Card('7', 'Diamonds'), Card('7', 'Clubs'),
        Card('3', 'Spades'), Card('K', 'Hearts')]

valid, _ = Validator.validate_discard(hand, [Card('7', 'Hearts')])
test("Single card discard is valid", valid)

valid, _ = Validator.validate_discard(hand, [Card('7', 'Hearts'), Card('7', 'Diamonds')])
test("Pair discard is valid", valid)

valid, _ = Validator.validate_discard(hand, [Card('7', 'Hearts'), Card('7', 'Diamonds'), Card('7', 'Clubs')])
test("Three-of-a-kind discard is valid", valid)

valid, _ = Validator.validate_discard(hand, [Card('7', 'Hearts'), Card('3', 'Spades')])
test("Mixed rank discard is rejected", not valid)

valid, _ = Validator.validate_discard(hand, [Card('2', 'Hearts')])
test("Card not in hand is rejected", not valid)

# Sequence tests
hand2 = [Card('4', 'Hearts'), Card('5', 'Hearts'), Card('6', 'Hearts'),
         Card('K', 'Diamonds'), Card('2', 'Spades')]
valid, _ = Validator.validate_discard(hand2, [Card('4', 'Hearts'), Card('5', 'Hearts'), Card('6', 'Hearts')])
test("Valid sequence discard", valid)

hand3 = [Card('4', 'Hearts'), Card('5', 'Diamonds'), Card('6', 'Hearts')]
valid, _ = Validator.validate_discard(hand3, [Card('4', 'Hearts'), Card('5', 'Diamonds'), Card('6', 'Hearts')])
test("Mixed-suit sequence is rejected", not valid)

hand4 = [Card('4', 'Hearts'), Card('Joker', None), Card('6', 'Hearts')]
valid, _ = Validator.validate_discard(hand4, [Card('4', 'Hearts'), Card('Joker', None), Card('6', 'Hearts')])
test("Sequence with Joker is valid", valid)

# ── Validator draw from discard tests ────────────────────────────────────────

print("\n=== Validator - Draw from Discard Tests ===")

# Single card
discard = [Card('9', 'Hearts')]
valid, _ = Validator.validate_draw_from_discard(discard, Card('9', 'Hearts'))
test("Taking a single card from discard is valid", valid)

# Pair - any card may be taken
discard = [Card('5', 'Hearts'), Card('5', 'Diamonds')]
valid, _ = Validator.validate_draw_from_discard(discard, Card('5', 'Hearts'))
test("Taking first card of a pair is valid", valid)
valid, _ = Validator.validate_draw_from_discard(discard, Card('5', 'Diamonds'))
test("Taking second card of a pair is valid", valid)

# Sequence - only endpoints allowed
discard = [Card('4', 'Hearts'), Card('5', 'Hearts'), Card('6', 'Hearts')]
valid, _ = Validator.validate_draw_from_discard(discard, Card('4', 'Hearts'))
test("Taking low endpoint of sequence (4) is valid", valid)
valid, _ = Validator.validate_draw_from_discard(discard, Card('6', 'Hearts'))
test("Taking high endpoint of sequence (6) is valid", valid)
valid, _ = Validator.validate_draw_from_discard(discard, Card('5', 'Hearts'))
test("Taking middle of sequence (5) is rejected", not valid)

# ── Validator Yaniv tests ────────────────────────────────────────────────────

print("\n=== Validator - Yaniv Tests ===")

hand = [Card('A', 'Hearts'), Card('2', 'Diamonds'), Card('3', 'Spades'), Card('Joker', None)]  # sum = 6
valid, _ = Validator.validate_yaniv(hand)
test("Yaniv with sum of 6 is valid", valid)

hand2 = [Card('A', 'Hearts'), Card('Joker', None)]  # sum = 1
valid, _ = Validator.validate_yaniv(hand2)
test("Yaniv with sum of 1 is valid", valid)

hand3 = [Card('5', 'Hearts'), Card('4', 'Diamonds'), Card('3', 'Spades')]  # sum = 12
valid, _ = Validator.validate_yaniv(hand3)
test("Yaniv with sum of 12 is rejected", not valid)

hand4 = [Card('3', 'Hearts'), Card('4', 'Diamonds')]  # sum = 7 exactly
valid, _ = Validator.validate_yaniv(hand4)
test("Yaniv with sum of exactly 7 is valid", valid)

# ── Player scoring tests ─────────────────────────────────────────────────────

print("\n=== Player - Scoring Tests ===")

p = Player("u1", "Dan")
p.add_score(30)
test("Adding 30 points", p.score == 30)

p2 = Player("u2", "Michal")
p2.add_score(50)
test("Landing exactly on 50 resets to 0", p2.score == 0)

p3 = Player("u3", "Yossi")
p3.score = 70
p3.add_score(30)
test("Landing exactly on 100 drops to 50", p3.score == 50)

p4 = Player("u4", "Ron")
p4.score = 80
p4.add_score(25)
test("Reaching 105 eliminates the player", p4.is_eliminated)

# ── Full game flow tests ─────────────────────────────────────────────────────

print("\n=== Game Tests ===")

game = Game("test_game")
p1 = Player("u1", "Dan")
p2 = Player("u2", "Michal")
game.add_player(p1)
game.add_player(p2)
game.start_game()

test("Game status is 'active' after starting", game.status == "active")
test("Player 1 received 5 cards", len(p1.hand) == 5)
test("Player 2 received 5 cards", len(p2.hand) == 5)
test("Discard pile is not empty at start", len(game.deck.top_discard) >= 1)

# Test a discard action
active = game._active_players()
current = active[game.current_turn_index]
card_to_discard = current.hand[0]
state = game.discard(current.uid, [card_to_discard])
test("Discard action returns a state update", state["event"] == "state_update")
test("Phase advances to 'draw' after discard", game._phase == "draw")

# Test a draw action
state = game.draw_from_deck(current.uid)
test("Draw action returns a state update", state["event"] == "state_update")
test("Phase resets to 'discard' after drawing", game._phase == "discard")

print("\n=== Summary ===")
print("All tests completed. Check for any ❌ above.")
