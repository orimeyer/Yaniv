"""
gui.py - Graphical interface for the Yaniv card game
Run with: python gui.py
"""
from typing import List, Dict, Tuple, Optional

import tkinter as tk
from tkinter import messagebox
from card import Card
from deck import Deck
from player import Player
from validator import Validator
from game import Game

# ── Color palette ────────────────────────────────────────────────────────────

BG_COLOR        = "#076324"   # Green felt table
CARD_BG         = "#FFFDF0"   # Warm white card face
CARD_SELECTED   = "#FFE680"   # Yellow highlight when selected
RED_SUIT        = "#CC0000"
BLACK_SUIT      = "#111111"
BTN_COLOR       = "#1a5c2e"
BTN_HOVER       = "#2a7c3e"
BTN_YANIV       = "#8B0000"
BTN_YANIV_HOVER = "#CC0000"
TEXT_LIGHT      = "#FFFFFF"
SCORE_BG        = "#054d1c"

SUIT_SYMBOLS = {
    'Hearts': '♥', 'Diamonds': '♦',
    'Clubs': '♣', 'Spades': '♠', None: '🃏'
}


def card_color(card: Card) -> str:
    """Returns the text color for a card (red for hearts/diamonds, black otherwise)"""
    if card.is_joker:
        return "#8B008B"
    if card.suit in ('Hearts', 'Diamonds'):
        return RED_SUIT
    return BLACK_SUIT


def card_label(card: Card) -> str:
    """Returns the display text for a card face"""
    if card.is_joker:
        return "🃏\nJoker"
    sym = SUIT_SYMBOLS[card.suit]
    return f"{card.rank}\n{sym}"


# ── Card widget ──────────────────────────────────────────────────────────────

class CardWidget(tk.Frame):
    """A clickable graphical card widget"""

    def __init__(self, parent, card: Card, on_click=None, face_up=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.card = card
        self.on_click = on_click
        self.selected = False
        self.face_up = face_up

        self.config(
            width=70, height=100,
            relief="raised", bd=2,
            bg=CARD_BG if face_up else "#1a5c8b",
            cursor="hand2" if on_click else "arrow"
        )
        self.pack_propagate(False)

        if face_up:
            self.label = tk.Label(
                self,
                text=card_label(card),
                bg=CARD_BG,
                fg=card_color(card),
                font=("Arial", 15, "bold"),
                justify="center"
            )
        else:
            # Face-down card shows a back design
            self.label = tk.Label(
                self,
                text="🂠",
                bg="#1a5c8b",
                fg="#FFFFFF",
                font=("Arial", 28),
                justify="center"
            )

        self.label.pack(expand=True)

        if on_click:
            self.bind("<Button-1>", self._clicked)
            self.label.bind("<Button-1>", self._clicked)

    def _clicked(self, event=None):
        if self.on_click:
            self.on_click(self)

    def set_selected(self, selected: bool):
        """Toggles the visual selection state of the card"""
        self.selected = selected
        new_bg = CARD_SELECTED if selected else CARD_BG
        self.config(bg=new_bg, relief="sunken" if selected else "raised")
        self.label.config(bg=new_bg)


# ── Styled button ────────────────────────────────────────────────────────────

class FancyButton(tk.Button):
    """A styled button with hover color effect"""

    def __init__(self, parent, text, command, color=BTN_COLOR, hover=BTN_HOVER, **kwargs):
        super().__init__(
            parent, text=text, command=command,
            bg=color, fg=TEXT_LIGHT,
            font=("Arial", 11, "bold"),
            relief="flat", bd=0,
            padx=16, pady=8,
            cursor="hand2",
            activebackground=hover,
            activeforeground=TEXT_LIGHT,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg=hover))
        self.bind("<Leave>", lambda e: self.config(bg=color))


# ── Main application window ──────────────────────────────────────────────────

class YanivGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Yaniv Card Game 🃏")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.game: Game = None
        self.human: Player = None
        self.computer: Player = None
        self.selected_cards: List[CardWidget] = []
        self.phase = "discard"   # discard | draw
        self.player_name = ""

        self._show_welcome()

    # ── Welcome screen ───────────────────────────────────────────────────────

    def _show_welcome(self):
        self._clear()
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True, pady=60, padx=80)

        tk.Label(frame, text="🃏", font=("Arial", 60), bg=BG_COLOR).pack()
        tk.Label(frame, text="Yaniv", font=("Arial", 32, "bold"),
                 bg=BG_COLOR, fg=TEXT_LIGHT).pack(pady=10)

        tk.Label(frame, text="Your name:", font=("Arial", 14),
                 bg=BG_COLOR, fg=TEXT_LIGHT).pack(pady=(20, 4))

        self.name_entry = tk.Entry(frame, font=("Arial", 14), width=18,
                                   justify="center", bd=2, relief="groove")
        self.name_entry.insert(0, "Player")
        self.name_entry.pack()
        self.name_entry.bind("<Return>", lambda e: self._start_game())

        FancyButton(frame, "▶  Start Game", self._start_game).pack(pady=20)

    # ── Game initialization ──────────────────────────────────────────────────

    def _start_game(self):
        self.player_name = self.name_entry.get().strip() or "Player"
        self.human    = Player("human", self.player_name)
        self.computer = Player("computer", "🤖 Computer")
        self.game     = Game("local")
        self.game.add_player(self.human)
        self.game.add_player(self.computer)
        self.game.start_game()
        self.selected_cards = []
        self.phase = "discard"
        self._build_main_ui()
        self._refresh()

    # ── Main game UI layout ──────────────────────────────────────────────────

    def _build_main_ui(self):
        self._clear()

        # Score bar at the top
        top = tk.Frame(self.root, bg=SCORE_BG)
        top.pack(fill="x")

        self.lbl_computer_score = tk.Label(
            top, text="", font=("Arial", 12, "bold"),
            bg=SCORE_BG, fg=TEXT_LIGHT, padx=16, pady=6)
        self.lbl_computer_score.pack(side="left")

        tk.Label(top, text="Yaniv 🃏", font=("Arial", 14, "bold"),
                 bg=SCORE_BG, fg="#FFD700").pack(side="left", expand=True)

        self.lbl_human_score = tk.Label(
            top, text="", font=("Arial", 12, "bold"),
            bg=SCORE_BG, fg=TEXT_LIGHT, padx=16, pady=6)
        self.lbl_human_score.pack(side="right")

        # Computer's hand area (cards shown face-down)
        self.computer_area = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        self.computer_area.pack(fill="x")

        tk.Label(self.computer_area, text="🤖 Computer's hand",
                 font=("Arial", 11), bg=BG_COLOR, fg=TEXT_LIGHT).pack()
        self.computer_cards_frame = tk.Frame(self.computer_area, bg=BG_COLOR)
        self.computer_cards_frame.pack(pady=4)

        # Middle area: draw pile and discard pile
        mid = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        mid.pack()

        # Closed draw pile
        deck_frame = tk.Frame(mid, bg=BG_COLOR)
        deck_frame.pack(side="left", padx=30)
        tk.Label(deck_frame, text="Draw pile", font=("Arial", 10),
                 bg=BG_COLOR, fg=TEXT_LIGHT).pack()
        self.deck_card = CardWidget(deck_frame, Card("2", "Hearts"),
                                    on_click=self._draw_deck, face_up=False)
        self.deck_card.pack()
        self.lbl_deck_count = tk.Label(deck_frame, text="",
                                       font=("Arial", 9), bg=BG_COLOR, fg=TEXT_LIGHT)
        self.lbl_deck_count.pack()

        # Discard pile (face-up, clickable)
        discard_frame = tk.Frame(mid, bg=BG_COLOR)
        discard_frame.pack(side="left", padx=30)
        tk.Label(discard_frame, text="Discard pile", font=("Arial", 10),
                 bg=BG_COLOR, fg=TEXT_LIGHT).pack()
        self.discard_frame_inner = tk.Frame(discard_frame, bg=BG_COLOR)
        self.discard_frame_inner.pack()

        # Status message
        self.lbl_status = tk.Label(
            self.root, text="", font=("Arial", 13, "bold"),
            bg=BG_COLOR, fg="#FFD700", pady=4)
        self.lbl_status.pack()

        # Human player's hand
        self.human_area = tk.Frame(self.root, bg=BG_COLOR, pady=6)
        self.human_area.pack(fill="x")
        tk.Label(self.human_area, text="👤 Your hand",
                 font=("Arial", 11), bg=BG_COLOR, fg=TEXT_LIGHT).pack()
        self.human_cards_frame = tk.Frame(self.human_area, bg=BG_COLOR)
        self.human_cards_frame.pack(pady=4)

        # Action buttons
        btn_frame = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        btn_frame.pack()

        self.btn_discard = FancyButton(btn_frame, "Discard selected cards ✋",
                                       self._discard_selected)
        self.btn_discard.pack(side="left", padx=8)

        self.btn_yaniv = FancyButton(btn_frame, "Declare Yaniv! 🌟",
                                     self._declare_yaniv,
                                     color=BTN_YANIV, hover=BTN_YANIV_HOVER)
        self.btn_yaniv.pack(side="left", padx=8)

    # ── UI refresh ───────────────────────────────────────────────────────────

    def _refresh(self):
        """Redraws the entire UI to reflect the current game state"""
        h = self.human
        c = self.computer

        # Update score labels
        self.lbl_human_score.config(text=f"{h.display_name}: {h.score} pts")
        self.lbl_computer_score.config(text=f"Computer: {c.score} pts")

        # Redraw computer's hand (face-down)
        for w in self.computer_cards_frame.winfo_children():
            w.destroy()
        for _ in c.hand:
            CardWidget(self.computer_cards_frame, Card("2", "Hearts"),
                       face_up=False).pack(side="left", padx=3)

        # Redraw discard pile (face-up, clickable)
        for w in self.discard_frame_inner.winfo_children():
            w.destroy()
        for card in self.game.deck.top_discard:
            CardWidget(self.discard_frame_inner, card,
                       on_click=self._draw_discard_card).pack(side="left", padx=2)

        # Update draw pile count
        self.lbl_deck_count.config(text=f"{len(self.game.deck.draw_pile)} cards")

        # Redraw human's hand (face-up, selectable)
        for w in self.human_cards_frame.winfo_children():
            w.destroy()
        self.selected_cards = []
        for card in h.hand:
            cw = CardWidget(self.human_cards_frame, card,
                            on_click=self._toggle_select)
            cw.pack(side="left", padx=4)

        self._update_buttons()

    def _update_buttons(self):
        """Enables or disables buttons depending on whose turn it is and the current phase"""
        active = self.game._active_players()
        current = active[self.game.current_turn_index % len(active)]
        is_my_turn = (current.uid == self.human.uid)

        if not is_my_turn:
            self.lbl_status.config(text="⏳ Computer is thinking...")
            self.btn_discard.config(state="disabled")
            self.btn_yaniv.config(state="disabled")
        elif self.phase == "discard":
            self.lbl_status.config(text="Select cards to discard, then click 'Discard' — or declare Yaniv")
            self.btn_discard.config(state="normal")
            can_yaniv = Validator.validate_yaniv(self.human.hand)[0]
            self.btn_yaniv.config(state="normal" if can_yaniv else "disabled")
        else:  # draw phase
            self.lbl_status.config(text="Click the draw pile or a card from the discard pile")
            self.btn_discard.config(state="disabled")
            self.btn_yaniv.config(state="disabled")

    # ── Player actions ───────────────────────────────────────────────────────

    def _toggle_select(self, card_widget: CardWidget):
        """Selects or deselects a card in the human player's hand"""
        active = self.game._active_players()
        current = active[self.game.current_turn_index % len(active)]
        if current.uid != self.human.uid or self.phase != "discard":
            return

        card_widget.set_selected(not card_widget.selected)
        if card_widget.selected:
            self.selected_cards.append(card_widget)
        else:
            self.selected_cards = [cw for cw in self.selected_cards if cw is not card_widget]

    def _discard_selected(self):
        """Discards all currently selected cards"""
        if not self.selected_cards:
            messagebox.showwarning("No cards selected", "Please select at least one card to discard")
            return

        cards = [cw.card for cw in self.selected_cards]
        try:
            self.game.discard(self.human.uid, cards)
            self.phase = "draw"
            self._refresh()
        except Exception as e:
            messagebox.showwarning("Illegal move", str(e))

    def _draw_deck(self, widget=None):
        """Handles clicking the draw pile"""
        active = self.game._active_players()
        current = active[self.game.current_turn_index % len(active)]
        if current.uid != self.human.uid or self.phase != "draw":
            return
        self.game.draw_from_deck(self.human.uid)
        self.phase = "discard"
        self._refresh()
        self._computer_turn_if_needed()

    def _draw_discard_card(self, card_widget: CardWidget):
        """Handles clicking a card on the discard pile"""
        active = self.game._active_players()
        current = active[self.game.current_turn_index % len(active)]
        if current.uid != self.human.uid or self.phase != "draw":
            return
        try:
            self.game.draw_from_discard(self.human.uid, card_widget.card)
            self.phase = "discard"
            self._refresh()
            self._computer_turn_if_needed()
        except Exception as e:
            messagebox.showwarning("Illegal move", str(e))

    def _declare_yaniv(self):
        """Handles the human player declaring Yaniv"""
        try:
            result = self.game.declare_yaniv(self.human.uid)
            self._show_yaniv_result(result)
        except Exception as e:
            messagebox.showwarning("Cannot declare Yaniv", str(e))

    # ── Computer AI ──────────────────────────────────────────────────────────

    def _computer_turn_if_needed(self):
        """Schedules the computer's turn if it is next"""
        active = self.game._active_players()
        current = active[self.game.current_turn_index % len(active)]
        if current.uid != self.computer.uid:
            return
        # Short delay so the player can see what happened before the computer moves
        self.root.after(900, self._do_computer_turn)

    def _do_computer_turn(self):
        """Executes the computer's discard decision"""
        # Declare Yaniv if hand sum is very low
        if Validator.validate_yaniv(self.computer.hand)[0] and self.computer.hand_sum <= 4:
            result = self.game.declare_yaniv(self.computer.uid)
            self._show_yaniv_result(result)
            return

        # Choose cards to discard
        to_discard = self._computer_choose_discard()
        try:
            self.game.discard(self.computer.uid, to_discard)
        except Exception:
            # Fallback: discard the first card in hand
            self.game.discard(self.computer.uid, [self.computer.hand[0]])

        self._refresh()
        self.root.after(600, self._do_computer_draw)

    def _do_computer_draw(self):
        """Executes the computer's draw decision"""
        self.game.draw_from_deck(self.computer.uid)
        self.phase = "discard"
        self._refresh()

    def _computer_choose_discard(self) -> List[Card]:
        """
        Computer's card selection logic.
        Prefers sets, then sequences, then discards the highest single card.
        """
        from collections import Counter
        hand = self.computer.hand

        # Prefer discarding a set (pair / three-of-a-kind)
        counts = Counter(c.rank for c in hand if not c.is_joker)
        for rank, count in counts.items():
            if count >= 2:
                same = [c for c in hand if c.rank == rank][:count]
                valid, _ = Validator.validate_discard(hand, same)
                if valid:
                    return same

        # Try to discard a sequence
        by_suit = {}
        for c in hand:
            if not c.is_joker:
                by_suit.setdefault(c.suit, []).append(c)
        for suit, cards in by_suit.items():
            sc = sorted(cards, key=lambda c: c.rank_order)
            for i in range(len(sc) - 2):
                trio = sc[i:i+3]
                valid, _ = Validator.validate_discard(hand, trio)
                if valid:
                    return trio

        # Default: discard the single highest-value card
        heaviest = max(hand, key=lambda c: c.points)
        return [heaviest]

    # ── Round result popup ───────────────────────────────────────────────────

    def _show_yaniv_result(self, result: dict):
        """Shows a popup window with the round result"""
        win = tk.Toplevel(self.root)
        win.title("Yaniv Result")
        win.configure(bg=BG_COLOR)
        win.grab_set()  # Block interaction with the main window

        declarer_name = self.player_name if result["declarer"] == "human" else "The computer"

        tk.Label(win, text=f"🌟 {declarer_name} declared Yaniv!",
                 font=("Arial", 18, "bold"), bg=BG_COLOR, fg="#FFD700",
                 pady=10).pack()

        # Show both players' hands
        hands_frame = tk.Frame(win, bg=BG_COLOR)
        hands_frame.pack(pady=10)

        for player in [self.human, self.computer]:
            pf = tk.Frame(hands_frame, bg=BG_COLOR, padx=20)
            pf.pack(side="left")
            name = self.player_name if player.uid == "human" else "🤖 Computer"
            tk.Label(pf, text=f"{name} ({player.hand_sum} pts)",
                     font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_LIGHT).pack()
            cards_f = tk.Frame(pf, bg=BG_COLOR)
            cards_f.pack()
            for card in player.hand:
                CardWidget(cards_f, card).pack(side="left", padx=2)

        # Assaf penalty message
        if result["is_assaf"]:
            tk.Label(win, text=f"💥 Assaf! {declarer_name} receives a 30-point penalty!",
                     font=("Arial", 13, "bold"), bg=BG_COLOR, fg="#FF6666",
                     pady=6).pack()

        # Round score breakdown
        score_frame = tk.Frame(win, bg=SCORE_BG, pady=10, padx=20)
        score_frame.pack(fill="x", pady=10)
        tk.Label(score_frame, text="Round scores:",
                 font=("Arial", 12, "bold"), bg=SCORE_BG, fg=TEXT_LIGHT).pack()
        for uid, pts in result["round_scores"].items():
            name = self.player_name if uid == "human" else "Computer"
            player = self.human if uid == "human" else self.computer
            tk.Label(score_frame,
                     text=f'{name}: +{pts} pts  (total: {player.score})',
                     font=("Arial", 11), bg=SCORE_BG, fg=TEXT_LIGHT).pack()

        # Elimination notice
        if result.get("eliminated"):
            for uid in result["eliminated"]:
                name = self.player_name if uid == "human" else "The computer"
                tk.Label(win, text=f"💀 {name} reached 100 points and is eliminated!",
                         font=("Arial", 12, "bold"), bg=BG_COLOR, fg="#FF4444").pack()

        # Game over or next round button
        if result.get("game_over"):
            winner_name = self.player_name if result["winner"] == "human" else "The computer"
            tk.Label(win, text=f"🏆 {winner_name} wins the game!",
                     font=("Arial", 16, "bold"), bg=BG_COLOR,
                     fg="#FFD700", pady=8).pack()
            FancyButton(win, "New Game 🔄",
                        lambda: [win.destroy(), self._show_welcome()]).pack(pady=10)
        else:
            def next_round():
                win.destroy()
                self.selected_cards = []
                self.phase = "discard"
                self._refresh()
                self._computer_turn_if_needed()
            FancyButton(win, "Next Round ▶", next_round).pack(pady=10)

    # ── Utility ──────────────────────────────────────────────────────────────

    def _clear(self):
        """Removes all widgets from the root window"""
        for w in self.root.winfo_children():
            w.destroy()


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    print("הקוד רץ בתוך ה-Container! הנה רשימת הקבצים בתיקייה:")
    print(os.listdir('.'))
    root = tk.Tk()
    root.geometry("680x620")
    app = YanivGUI(root)
    root.mainloop()
