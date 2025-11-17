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

"""TODO"""

import itertools
from enum import Enum


class _Mark(Enum):
    Nought = 1
    Cross = 2

    def __str__(self):
        return ('O' if self == _Mark.Nought else 'X')


class _GameState:
    def __init__(self):
        self._grid = [[None for _ in range(3)] for _ in range(3)]
        self.winner: _Mark | None = None

    def add_mark(self, index: int, mark: _Mark) -> bool:
        """TODO

        Args:
            index (int): TODO
            mark (Mark): TODO

        Returns:
            bool: Whether or not the specified space is already taken.
        """

        y = (index-1) // 3
        x = (index-1) % 3

        if self._grid[y][x]:
            return True

        self._grid[y][x] = mark
        self.check_for_win()

        return False

    def check_for_win(self):
        """TODO
        """

        # check rows for win
        self.winner = self.winner or self._find_three_row(self._grid)

        # check columns for win
        self.winner = self.winner or self._find_three_row(zip(*self._grid))

        if self.winner:
            return None

        # check diagonals for win
        diagonal = (
            tuple(self._grid[x][x] for x in range(3)),
            tuple(self._grid[x][2-x] for x in range(3)),
        )

        self.winner = self._find_three_row(diagonal)

    def get_grid(self) -> str:
        """TODO
        """

        rows = (' | '.join((str(x or '-') for x in row)) for row in self._grid)
        return '\n'.join(rows)

    @staticmethod # CHECK???
    def _find_three_row(rows: list | tuple | zip) -> _Mark | None:
        """TODO
        """

        for row in rows:
            if all(row) and len(set(row)) == 1:
                return row[0]


def _prompt_move(game_state: _GameState, player: _Mark) -> bool:
    """TODO
    """

    print(game_state.get_grid())

    # TODO


def main(endless: bool = False):
    """TODO
    """

    player_order = [_Mark.Cross, _Mark.Nought]

    while True:
        game_state = _GameState
        players = itertools.cycle(player_order)

        while game_state.winner:
            if _prompt_move(game_state, next(players)):
                return None

        # print(f'The winner is {game_state.winner}')

        player_order.reverse() # HACK: There may be a cheaper way to do this
