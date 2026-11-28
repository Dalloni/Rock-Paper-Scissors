"""
Computer Sciences I - Proyecto 2026-III
Equipo: <numero de equipo>
Juego: Piedra, Papel o Tijera
Integrantes: <nombre 1>, <nombre 2>, <nombre 3>

Tests unitarios para opponent.py. Ejecutar con:
    python -m unittest tests.py -v
(o simplemente: python tests.py)
"""

import random
import unittest

from opponent import (
    ROCK, PAPER, SCISSORS, MOVES, WIN, LOSE, DRAW,
    COUNTER, determine_result,
    Node, LinkedList,
    frequency_detector, reaction_detector, sequence_detector, cycle_detector,
    Opponent,
)


def build_history(moves, results=None):
    """Helper: arma una LinkedList desde una cadena como 'RPS'."""
    hist = LinkedList()
    for i, m in enumerate(moves):
        r = results[i] if results else DRAW
        hist.append(m, r)
    return hist


# ----------------------------------------------------------------------
# Reglas basicas
# ----------------------------------------------------------------------
class TestDetermineResult(unittest.TestCase):
    def test_player_wins(self):
        self.assertEqual(determine_result(ROCK, SCISSORS), WIN)
        self.assertEqual(determine_result(PAPER, ROCK), WIN)
        self.assertEqual(determine_result(SCISSORS, PAPER), WIN)

    def test_player_loses(self):
        self.assertEqual(determine_result(ROCK, PAPER), LOSE)
        self.assertEqual(determine_result(PAPER, SCISSORS), LOSE)
        self.assertEqual(determine_result(SCISSORS, ROCK), LOSE)

    def test_draw(self):
        for m in MOVES:
            self.assertEqual(determine_result(m, m), DRAW)


# ----------------------------------------------------------------------
# Lista enlazada
# ----------------------------------------------------------------------
class TestLinkedList(unittest.TestCase):
    def test_empty_list(self):
        lst = LinkedList()
        self.assertEqual(len(lst), 0)
        self.assertIsNone(lst.head)
        self.assertIsNone(lst.tail)
        self.assertEqual(list(lst), [])

    def test_append_one(self):
        lst = LinkedList()
        lst.append(ROCK, WIN)
        self.assertEqual(len(lst), 1)
        self.assertIs(lst.head, lst.tail)
        self.assertEqual(lst.head.move, ROCK)
        self.assertEqual(lst.head.result, WIN)

    def test_append_keeps_order(self):
        lst = build_history("RPS")
        self.assertEqual([n.move for n in lst], ["R", "P", "S"])
        self.assertEqual(lst.head.move, "R")
        self.assertEqual(lst.tail.move, "S")
        self.assertIsNone(lst.tail.next)

    def test_iter_can_be_repeated(self):
        lst = build_history("RP")
        self.assertEqual(len(list(lst)), 2)
        self.assertEqual(len(list(lst)), 2)

    def test_get_last(self):
        lst = build_history("RPSRP")
        self.assertEqual([n.move for n in lst.get_last(2)], ["R", "P"])
        self.assertEqual([n.move for n in lst.get_last(3)], ["S", "R", "P"])

    def test_get_last_more_than_size(self):
        lst = build_history("RP")
        self.assertEqual(len(lst.get_last(10)), 2)

    def test_clear(self):
        lst = build_history("RPS")
        lst.clear()
        self.assertEqual(len(lst), 0)
        self.assertIsNone(lst.head)


# ----------------------------------------------------------------------
# Detectores
# ----------------------------------------------------------------------
class TestFrequencyDetector(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(frequency_detector(LinkedList()))

    def test_most_frequent(self):
        move, conf = frequency_detector(build_history("RRRPS"))
        self.assertEqual(move, ROCK)
        self.assertAlmostEqual(conf, 3 / 5)

    def test_always_same(self):
        move, conf = frequency_detector(build_history("PPPPPP"))
        self.assertEqual(move, PAPER)
        self.assertAlmostEqual(conf, 1.0)


class TestReactionDetector(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(reaction_detector(LinkedList()))

    def test_plays_rock_after_losing(self):
        # El jugador siempre juega R despues de perder.
        moves = "SRPRSR"
        results = [LOSE, DRAW, LOSE, DRAW, LOSE, DRAW]
        # Ultimo resultado = DRAW, asi que forzamos que termine en LOSE:
        moves += "P"
        results += [LOSE]
        hist = build_history(moves, results)
        move, conf = reaction_detector(hist)
        self.assertEqual(move, ROCK)
        self.assertGreater(conf, 0.5)


class TestSequenceDetector(unittest.TestCase):
    def test_not_enough_data_returns_none(self):
        self.assertIsNone(sequence_detector(build_history("R")))

    def test_repeating_pattern(self):
        # Patron RRP repetido: tras R,P siempre viene R.
        hist = build_history("RRPRRPRRPRP")
        move, conf = sequence_detector(hist, length=2)
        self.assertEqual(move, ROCK)
        self.assertGreater(conf, 0.5)


class TestCycleDetector(unittest.TestCase):
    def test_forward_cycle(self):
        # R -> P -> S -> R -> P ...  el siguiente es S
        move, conf = cycle_detector(build_history("RPSRP"))
        self.assertEqual(move, SCISSORS)
        self.assertGreater(conf, 0.5)

    def test_backward_cycle(self):
        # R -> S -> P -> R -> S ...  el siguiente es P
        move, conf = cycle_detector(build_history("RSPRS"))
        self.assertEqual(move, PAPER)
        self.assertGreater(conf, 0.5)


# ----------------------------------------------------------------------
# Oponente completo: simulaciones contra jugadores con comportamiento conocido
# ----------------------------------------------------------------------
def simulate(player_strategy, rounds=60, seed=42):
    """Juega 'rounds' rondas IA vs estrategia y devuelve (wins_ia, total).

    player_strategy(i, last_move, last_result) -> "R" | "P" | "S"
    """
    ai = Opponent(rng=random.Random(seed))
    ai_wins = 0
    last_move, last_result = None, None
    for i in range(rounds):
        ai_move = ai.choose_move()
        player_move = player_strategy(i, last_move, last_result)
        result = determine_result(player_move, ai_move)
        if result == LOSE:       # el jugador perdio => gano la IA
            ai_wins += 1
        ai.register_round(player_move, result)
        last_move, last_result = player_move, result
    return ai_wins, rounds


class TestOpponentBasics(unittest.TestCase):
    def test_choose_move_is_valid(self):
        ai = Opponent(rng=random.Random(1))
        for _ in range(20):
            self.assertIn(ai.choose_move(), MOVES)

    def test_register_round_grows_history(self):
        ai = Opponent()
        ai.register_round(ROCK, WIN)
        ai.register_round(PAPER, LOSE)
        self.assertEqual(len(ai.history), 2)

    def test_counters_obvious_pattern(self):
        ai = Opponent(rng=random.Random(1))
        for _ in range(10):
            ai.register_round(ROCK, DRAW)
        self.assertEqual(ai.choose_move(), COUNTER[ROCK])  # Papel


class TestOpponentSimulations(unittest.TestCase):
    def test_vs_always_rock(self):
        wins, total = simulate(lambda i, m, r: ROCK, rounds=60)
        self.assertGreaterEqual(wins / total, 0.8)

    def test_vs_cycle(self):
        wins, total = simulate(lambda i, m, r: MOVES[i % 3], rounds=60)
        self.assertGreaterEqual(wins / total, 0.7)

    def test_vs_win_stay_lose_shift(self):
        def strat(i, last_move, last_result):
            if last_move is None:
                return ROCK
            if last_result == WIN:
                return last_move
            # si no gano, cambia a la siguiente jugada del ciclo
            return MOVES[(MOVES.index(last_move) + 1) % 3]
        wins, total = simulate(strat, rounds=100)
        self.assertGreaterEqual(wins / total, 0.5)

    def test_vs_random_is_not_exploitable(self):
        # Contra un jugador aleatorio la IA no deberia ganar mucho mas del 33%.
        rng = random.Random(7)
        wins, total = simulate(lambda i, m, r: rng.choice(MOVES), rounds=300)
        self.assertLess(wins / total, 0.45)


if __name__ == "__main__":
    unittest.main(verbosity=2)
