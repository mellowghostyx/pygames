#!/usr/bin/env python3

import random

class _Card:
    RANK = tuple('ace 2 3 4 5 6 7 8 9 10 jack queen king'.split())
    SUIT = ('spades', 'hearts', 'clubs', 'diamonds')

    def __init__(self, rank: str, suit: str):
        if rank not in self.RANK:
            raise ValueError(f"{rank} not a valid plyaing card rank")

        if suit not in self.SUIT:
            raise ValueError(f"{suit} not a valid plyaing card suit")

        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class _HangmanRound:
    def __init__(self, bet: int, cards: list):
        self.bet = bet
        # TODO
