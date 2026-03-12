"""
play.py - Terminal-based Yaniv game: one human player vs the computer
Run with: python play.py
"""
from typing import List, Dict, Tuple, Optional

import random
from card import Card
from deck import Deck
from player import Player
from validator import Validator
from game import Game


# ── Display helpers ──────────────────────────────────────────────────────────

SUIT_SYMBOLS = {
    'Hearts': '♥', 'Diamonds': '♦',
    'Clubs': '♣', 'Spades': '♠', None: '🃏'
}

def card_str(card: Card) -> str:
    """Returns a human-readable string for a single card"""
    if card.is_joker:
        return "[Joker🃏]"
    sym = SUIT_SYMBOLS[card.suit]
    return f"[{card.rank}{sym}]"

def hand_str(hand: List[Card]) -> str:
    """Returns a numbered display of a full hand"""
    parts = [f"{i+1}:{card_str(c)}" for i, c in enumerate(hand)]
    return "  ".join(parts)

def print_separator():
    print("\n" + "─" * 50 + "\n")

def print_game_status(game: Game, human: Player, computer: Player):
    """Prints the current game state to the terminal"""
    print_separator()
    print(f"🃏 Discard pile: {hand_str(game.deck.top_discard)}")
    print(f"🂠 Draw pile: {len(game.deck.draw_pile)} cards remaining")
    print()
    print(f"🤖 Computer: {computer.hand_size} cards | Score: {computer.score}")
    print(f"👤 Your hand: {hand_str(human.hand)}")
    print(f"   Hand sum: {human.hand_sum} | Score: {human.score}")


# ── Input helpers ────────────────────────────────────────────────────────────

def ask_cards_to_discard(hand: List[Card]) -> List[Card]:
    """Asks the player which cards to discard and validates the choice"""
    while True:
        print("\nWhich cards do you want to discard? (enter numbers separated by commas, e.g. 1,3)")
        raw = input(">>> ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in raw.split(",")]
            if any(i < 0 or i >= len(hand) for i in indices):
                print("❌ Invalid number - try again")
                continue
            chosen = [hand[i] for i in indices]
            valid, reason = Validator.validate_discard(hand, chosen)
            if not valid:
                print(f"❌ {reason}")
                continue
            return chosen
        except ValueError:
            print("❌ Invalid input - numbers only please")

def ask_draw_source(game: Game, human: Player):
    """Asks the player where to draw from - deck or discard pile"""
    discard = game.deck.top_discard
    print(f"\nWhere do you want to draw from?")
    print(f"  1: Closed draw pile 🂠")
    print(f"  2: Discard pile {hand_str(discard)}")

    while True:
        choice = input(">>> ").strip()
        if choice == "1":
            return "deck"
        elif choice == "2":
            if len(discard) == 1:
                return discard[0]
            # Multiple cards on discard pile - player must choose which one
            print("Which card do you want to take?")
            for i, c in enumerate(discard):
                print(f"  {i+1}: {card_str(c)}")
            while True:
                try:
                    idx = int(input(">>> ").strip()) - 1
                    card = discard[idx]
                    valid, reason = Validator.validate_draw_from_discard(discard, card)
                    if not valid:
                        print(f"❌ {reason}")
                        continue
                    return card
                except (ValueError, IndexError):
                    print("❌ Invalid input")
        else:
            print("❌ Enter 1 or 2")

def ask_yaniv_or_discard(human: Player) -> str:
    """Asks the player if they want to declare Yaniv (only shown when eligible)"""
    can_yaniv, _ = Validator.validate_yaniv(human.hand)
    if can_yaniv:
        print(f"\n🌟 Your hand sum is {human.hand_sum} - you can declare Yaniv!")
        print("  1: Declare Yaniv!")
        print("  2: Keep playing")
        while True:
            choice = input(">>> ").strip()
            if choice == "1":
                return "yaniv"
            elif choice == "2":
                return "discard"
            else:
                print("❌ Enter 1 or 2")
    return "discard"


# ── Computer AI (simple strategy) ───────────────────────────────────────────

def computer_discard(hand: List[Card]) -> List[Card]:
    """
    Computer chooses which cards to discard.
    Strategy: prefer sets > sequences > discard highest single card.
    """
    from collections import Counter

    # Try to discard a pair or set
    counts = Counter(c.rank for c in hand if not c.is_joker)
    for rank, count in counts.items():
        if count >= 2:
            same = [c for c in hand if c.rank == rank][:count]
            return same

    # Try to discard a sequence
    by_suit = {}
    for c in hand:
        if not c.is_joker:
            by_suit.setdefault(c.suit, []).append(c)
    for suit, cards in by_suit.items():
        sorted_cards = sorted(cards, key=lambda c: c.rank_order)
        for i in range(len(sorted_cards) - 2):
            trio = sorted_cards[i:i+3]
            orders = [c.rank_order for c in trio]
            if orders[2] - orders[0] == 2:
                return trio

    # Fall back to discarding the single highest-value card
    heaviest = max(hand, key=lambda c: c.points)
    return [heaviest]

def computer_turn(game: Game, computer: Player):
    """Executes a full computer turn - discard then draw"""
    print("\n🤖 Computer's turn...")

    # Declare Yaniv if hand sum is very low
    if Validator.validate_yaniv(computer.hand)[0] and computer.hand_sum <= 3:
        print(f"🤖 Computer declares Yaniv! (hand sum: {computer.hand_sum})")
        return "yaniv"

    # Discard phase
    to_discard = computer_discard(computer.hand)
    print(f"🤖 Discards: {hand_str(to_discard)}")
    game.discard(computer.uid, to_discard)

    # Draw phase - computer always draws from the deck (simple strategy)
    game.draw_from_deck(computer.uid)
    print(f"🤖 Draws a card from the deck")

    return "continue"


# ── Human turn ───────────────────────────────────────────────────────────────

def human_turn(game: Game, human: Player) -> str:
    """Executes a full human turn. Returns 'yaniv' or 'continue'."""

    # Step 1: Declare Yaniv or discard cards
    action = ask_yaniv_or_discard(human)
    if action == "yaniv":
        return "yaniv"

    cards = ask_cards_to_discard(human.hand)
    print(f"✅ Discarded: {hand_str(cards)}")
    game.discard(human.uid, cards)

    # Step 2: Draw a card
    source = ask_draw_source(game, human)
    if source == "deck":
        game.draw_from_deck(human.uid)
        print(f"✅ Drew a card from the deck")
    else:
        game.draw_from_discard(human.uid, source)
        print(f"✅ Took: {card_str(source)}")

    return "continue"


# ── Round resolution ─────────────────────────────────────────────────────────

def resolve_yaniv_display(result: dict, human: Player, computer: Player):
    """Prints the result of a Yaniv declaration"""
    print_separator()
    declarer_name = "You" if result["declarer"] == human.uid else "The computer"
    print(f"🌟 {declarer_name} declared Yaniv! (hand sum: {result['declarer_sum']})")

    print(f"\n📋 All hands revealed:")
    print(f"   👤 You:      {hand_str(human.hand)} = {human.hand_sum} points")
    print(f"   🤖 Computer: {hand_str(computer.hand)} = {computer.hand_sum} points")

    if result["is_assaf"]:
        print(f"\n💥 Assaf! {declarer_name} receives a 30-point penalty!")

    print(f"\n📊 Round scores:")
    for uid, pts in result["round_scores"].items():
        name = "You" if uid == human.uid else "Computer"
        print(f"   {name}: +{pts} points")

    print(f"\n📊 Cumulative scores:")
    print(f"   👤 You:      {human.score}")
    print(f"   🤖 Computer: {computer.score}")

    if result.get("eliminated"):
        for uid in result["eliminated"]:
            name = "You" if uid == human.uid else "The computer"
            print(f"\n💀 {name} reached 100 points and is eliminated!")


# ── Main game loop ───────────────────────────────────────────────────────────

def play_round(game: Game, human: Player, computer: Player) -> bool:
    """
    Runs a complete round.
    Returns True if the game is over, False if another round should begin.
    """
    while True:
        active = game._active_players()
        current = active[game.current_turn_index % len(active)]
        print_game_status(game, human, computer)

        if current.uid == human.uid:
            result_action = human_turn(game, human)
        else:
            result_action = computer_turn(game, computer)

        if result_action == "yaniv":
            result = game.declare_yaniv(current.uid)
            resolve_yaniv_display(result, human, computer)

            if result.get("game_over"):
                return True

            print("\nPress Enter to start the next round...")
            input()
            return False


def main():
    print("=" * 50)
    print("       Welcome to Yaniv! 🃏")
    print("=" * 50)

    name = input("\nWhat is your name? ").strip() or "Player"

    human    = Player("human", name)
    computer = Player("computer", "Computer")

    game = Game("local_game")
    game.add_player(human)
    game.add_player(computer)
    game.start_game()

    print(f"\nGame started! Good luck, {name}! 🎮")

    while True:
        game_over = play_round(game, human, computer)
        if game_over:
            print_separator()
            if game.winner.uid == human.uid:
                print(f"🏆 Congratulations {name}! You won!")
            else:
                print("🤖 The computer won. Better luck next time!")
            break

    print("\nThanks for playing Yaniv! Goodbye 👋")


if __name__ == "__main__":
    main()
