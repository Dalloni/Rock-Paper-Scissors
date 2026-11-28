"""
Computer Sciences I - Proyecto 2026-III
Equipo: <numero de equipo>
Juego: Piedra, Papel o Tijera (Rock Paper Scissors)
Integrantes: <nombre 1>, <nombre 2>, <nombre 3>

Modulo: opponent.py
Estructura de datos: Lista enlazada (historial de jugadas del jugador)
Objetivo: detectar patrones en el historial y jugar la contra-jugada.

Este modulo NO depende de pygame ni de game.py, para poder probarlo solo.

Interfaz publica (lo unico que necesita game.py):
    opponent = Opponent()
    ai_move = opponent.choose_move()               # "R", "P" o "S"
    opponent.register_round(player_move, result)   # aprende de la ronda

Convencion de 'result': siempre desde el punto de vista del JUGADOR HUMANO
    WIN  -> el jugador gano la ronda
    LOSE -> el jugador perdio la ronda
    DRAW -> empate
"""

import random

# ----------------------------------------------------------------------
# Constantes
# ----------------------------------------------------------------------
ROCK, PAPER, SCISSORS = "R", "P", "S"
MOVES = (ROCK, PAPER, SCISSORS)

WIN, LOSE, DRAW = "WIN", "LOSE", "DRAW"

# BEATS[x] = la jugada a la que x le gana
BEATS = {ROCK: SCISSORS, PAPER: ROCK, SCISSORS: PAPER}
# COUNTER[x] = la jugada que le gana a x
COUNTER = {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}

MIN_ROUNDS = 3          # rondas minimas antes de confiar en un detector
CONFIDENCE_THRESHOLD = 0.5   # por debajo de esto se juega aleatorio


def determine_result(player_move, ai_move):
    """Devuelve WIN, LOSE o DRAW desde el punto de vista del jugador.

    TODO: implementarla usando BEATS.
    """
    raise NotImplementedError


# ----------------------------------------------------------------------
# Lista enlazada (NO usar list, deque ni collections para el historial)
# ----------------------------------------------------------------------
class Node:
    """Nodo con la jugada del jugador y el resultado de esa ronda."""

    def __init__(self, move, result):
        self.move = move
        self.result = result
        self.next = None


class LinkedList:
    """Lista enlazada simple con punteros a head y tail."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, move, result):
        """Agrega un nodo al final en O(1).

        TODO: crear el Node, manejar el caso de lista vacia, actualizar
        tail y size.
        """
        raise NotImplementedError

    def __iter__(self):
        """Recorre la lista de head a tail devolviendo cada Node.

        TODO: recorrer con un puntero 'current' y usar yield.
        """
        raise NotImplementedError

    def __len__(self):
        return self.size

    def get_last(self, n):
        """Devuelve una lista Python con los ultimos n nodos (en orden).

        TODO: pensar como hacerlo sin recorrer dos veces si es posible
        (pista: saltar los primeros size - n nodos).
        Si n > size, devolver todos los nodos.
        """
        raise NotImplementedError

    def clear(self):
        """Vacia la lista."""
        self.head = None
        self.tail = None
        self.size = 0


# ----------------------------------------------------------------------
# Detectores de patrones
# Cada uno recibe la LinkedList y devuelve (jugada_predicha, confianza)
# o None si no tiene suficientes datos.
# 'jugada_predicha' es lo que se ESPERA que juegue el jugador (no la contra-jugada).
# 'confianza' es un float entre 0 y 1.
# ----------------------------------------------------------------------
def frequency_detector(history):
    """Predice la jugada mas frecuente del jugador.

    TODO: recorrer la lista contando R/P/S (diccionario de contadores).
    confianza = conteo_de_la_mas_frecuente / history.size
    """
    raise NotImplementedError


def reaction_detector(history):
    """Predice que jugara el jugador segun el resultado de su ULTIMA ronda.

    Ejemplo: si en la ultima ronda perdio, mirar que jugo cada vez que,
    en el pasado, la ronda anterior termino en LOSE.

    TODO:
      1. Obtener el resultado de la ultima ronda (history.tail.result).
      2. Recorrer la lista con DOS punteros (prev y current): cada vez que
         prev.result == ultimo_resultado, contar current.move.
      3. Devolver la jugada mas contada y su confianza.
    """
    raise NotImplementedError


def sequence_detector(history, length=2):
    """Predice la siguiente jugada a partir de las ultimas 'length' jugadas.

    Ejemplo: si las ultimas 2 fueron R,P, buscar en el pasado cada vez que
    aparecio R,P y contar que vino despues.

    TODO: recorrer la lista buscando la subsecuencia y contar el sucesor.
    """
    raise NotImplementedError


def cycle_detector(history):
    """Detecta si el jugador rota en ciclo (R->P->S->R...) o al reves.

    TODO: revisar los pasos consecutivos del historial; si (casi) todos
    avanzan +1 en MOVES, predecir el siguiente del ciclo (idem para -1).
    """
    raise NotImplementedError


# ----------------------------------------------------------------------
# Oponente (junta todo)
# ----------------------------------------------------------------------
class Opponent:
    def __init__(self, rng=None):
        self.history = LinkedList()
        # rng inyectable para poder hacer tests reproducibles
        self.rng = rng if rng is not None else random.Random()
        self.detectors = [
            frequency_detector,
            reaction_detector,
            sequence_detector,
            cycle_detector,
        ]

    def register_round(self, player_move, result):
        """Guarda la ronda en el historial.

        TODO: llamar a self.history.append(...)
        """
        raise NotImplementedError

    def predict_player_move(self):
        """Corre todos los detectores y devuelve (jugada, confianza) del mejor,
        o None si ninguno tiene datos.

        TODO: iterar sobre self.detectors, ignorar los None y quedarse con
        la mayor confianza.
        """
        raise NotImplementedError

    def choose_move(self):
        """Devuelve la jugada de la IA: "R", "P" o "S".

        TODO:
          - Si hay menos de MIN_ROUNDS rondas -> aleatoria.
          - Predecir con predict_player_move().
          - Si la confianza < CONFIDENCE_THRESHOLD -> aleatoria.
          - Si no -> COUNTER[prediccion].
        """
        raise NotImplementedError

    def reset(self):
        """Borra el historial (usar solo si el profesor pide reiniciar)."""
        self.history.clear()
