"""Reglas, jugadores, rondas y partida al mejor de cinco.

Jugadas: "R", "P", "S".  Resultados (desde el jugador): WIN, LOSE, DRAW.
"""
from dataclasses import dataclass
from opponent import Opponent, MOVES, WIN, LOSE, DRAW, determine_result


@dataclass
class Player:
    name: str = "Jugador"


class AIPlayer:
    def __init__(self, opponent=None):
        self.name = "IA"
        self.opponent = opponent if opponent is not None else Opponent()

    @property
    def history(self):
        """Historial (lista enlazada) que mantiene el Opponent."""
        return self.opponent.history


@dataclass(frozen=True)
class Round:
    player_move: str
    ai_move: str
    result: str  # WIN, LOSE o DRAW, desde el punto de vista del jugador

    @staticmethod
    def resolve(player_move, ai_move):
        return determine_result(player_move, ai_move)


class Match:
    TARGET_WINS = 3

    def __init__(self, player=None, ai_player=None):
        self.player = player if player is not None else Player()
        self.ai = ai_player if ai_player is not None else AIPlayer()
        self.rounds = []
        self.player_wins = 0
        self.ai_wins = 0
        self.ties = 0

    @property
    def finished(self):
        return max(self.player_wins, self.ai_wins) >= self.TARGET_WINS

    @property
    def winner(self):
        if not self.finished:
            return None
        return self.player.name if self.player_wins >= self.TARGET_WINS else self.ai.name

    def play_round(self, player_move):
        if self.finished:
            raise RuntimeError("La partida ya termino")
        if player_move not in MOVES:
            raise ValueError("Movimiento no valido")
        # La IA SOLO ve rondas anteriores, nunca la jugada actual.
        ai_move = self.ai.opponent.choose_move()
        result = Round.resolve(player_move, ai_move)
        current = Round(player_move, ai_move, result)
        self.rounds.append(current)
        if result == WIN:
            self.player_wins += 1
        elif result == LOSE:
            self.ai_wins += 1
        else:
            self.ties += 1
        self.ai.opponent.register_round(player_move, result)
        return current