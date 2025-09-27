#!/usr/bin/env python3

# Copyright (c) 2025 MellowGhostyx
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
