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

"""A command-line implementation of the game 'Hangman'.

A version of the game 'Hangman' made for the command-line interface, wrapped
into a single class. The game can be played through the `Hangman` class
contained in this module, like so: ::

    game = Hangman()
    game.launch()

Alternatively, you can play the game by executing this file, i.e. by
running `python hangman.py`. If you are on a Unix-based system, you can
also convert this file into an executable via `chmod +x hangman.py`, then
run the file directly.
"""

import random
import requests


class _SecretLetter:
    """A hidden letter, only to be revealed with a correct guess.

    A letter that will only reveal itself once guessed correctly. When parsed
    into a string, it will only contain the hidden letter if it was guessed
    correctly; otherwise, the string will only contain an underscore.
    """

    def __init__(self, letter: str):
        self._letter = letter
        self._hidden = True

    def guess(self, letter: str) -> bool:
        """Tries to guess the secret letter with the provided guess.

        Compares the provided letter with the secret letter. If they match,
        returns True and makes the secret word visible when converted
        into a string. Otherwise, returns False.

        Args:
            letter (str): The letter to use as your guess.

        Returns:
            bool: Whether or not the guess was correct.
        """

        if letter == self._letter:
            self._hidden = False
            return True

        return False

    def __str__(self):
        return '_' if self._hidden else self._letter


class _SecretWord:
    """A hidden word, only to be revealed with a correct guess.

    A word where each letter is hidden, only to be revealed with either a
    correct guess to the letter, or a correct guess to the entire word. When
    parsed into a string, each letter will only be provided if they were
    correctly guessed; otherwise they will be represented with an underscore.
    If the entire word is guessed correctly, every letter will be revealed.

    Attributes:
        hidden (bool): Whether or not the secret word is hidden. Starts out
            as True, and automatically becomes False if all letters in the secret word have been revealed via correct guesses. This value can
            be changed manually to force the secret word to be revealed.
    """

    def __init__(self, word: str):
        self._word = word
        self._slots = [_SecretLetter(letter) for letter in self._word]
        self.hidden = True

    def guess_letter(self, letter: str) -> int:
        """Tries to guess a letter in the secret word with the provided letter.

        Compares the provided letter with all letters in the secret word. Any
        letters that the guessed letter matches are revealed in the secret
        word, making them visible when the secret word is converted into a
        string. Returns the number of matches found.

        Args:
            letter (str): The letter to use as your guess.

        Returns:
            int: The number of letters in the secret word that match your
                guess.
        """

        count = 0

        for n in range(0, len(self._slots)):
            if self._slots[n].guess(letter): count += 1

        if not any([slot._hidden for slot in self._slots]):
            self.hidden = False

        return count

    def guess_word(self, word: str) -> bool:
        """Tries to guess the entire secret word with the provided word.

        Compares the provided word with the secret word. If they match, returns True and makes the entire secret word visible when the secret
        word is converted into a string. Otherwise, returns False.

        Args:
            word (str): The word to use as your guess.

        Returns:
            bool: Whether or not the guess was correct.
        """

        if word == self._word:
            self.hidden = False
            return True

        return False

    def __str__(self):
        if not self.hidden:
            return self._word

        return ''.join([str(slot) for slot in self._slots])


class _GameState:
    """Game state manager for a single game of Hangman."""

    def __init__(self, secret_word: str, lives: int):
        self.secret_word = _SecretWord(secret_word)
        self.lives = lives
        self.guesses = set()

        # String representation of all the wrong (letter) guesses made so far
        self._wrong_guesses = ''

    def summarize(self) -> str:
        """Generates a string of relevant data about the current game state.

        Provides the secret word (with unguessed letters hidden and replaced
        with underscores), the number of lives remaining, and a list of wrong
        letter guesses (if applicable), all in a single string with interpuncts
        separating them.

        Returns:
            str: The aforementioned string of relevant game stats.
        """

        summary = f"{self.secret_word} · {self.lives} lives"

        if self._wrong_guesses:
            summary += f" · {self._wrong_guesses}"

        return summary

    def try_guess(self, guess: str) -> str:
        """Modifies the game state according to the provided guess.

        Tries to guess the secret word with the provided guess, then generates
        a string message stating the validity and successfulness of the
        provided guess, and changes the game state accordingly.

        Note:
            A correct word guess returns an empty string, as no message is
            provided from such a guess in-game

        Args:
            guess (str): The guess to try.

        Returns:
            str: A message explaining whether or not the guess was valid
                and/or correct. If the guess is invalid, it explains why it is
                invalid; If the guess is valid but incorrect, it states as
                such; if the guess is a correct letter, it describes how many
                instances there are of that letter in the secret word.
        """

        # return early if the guess matches the secret word
        if self.secret_word.guess_word(guess): return ""

        if not (guess and guess.isascii() and guess.isalpha()):
            return "Please input a letter or word!"

        if guess in self.guesses:
            return "You already made this guess!"

        self.guesses.add(guess)

        if len(guess) != 1:
            self.lives -= 1
            return "Sorry, but that was not the correct word"

        count = self.secret_word.guess_letter(guess)

        if not count:
            self.lives -= 1
            if self._wrong_guesses: self._wrong_guesses += " " # HACK
            self._wrong_guesses += guess.upper()

        return self._generate_count_message(count, guess)

    def _generate_count_message(self, count: int, letter: str) -> str:
        """Creates a string stating the number of matches for the given guess.

        Uses the provided `count` and `letter` values to construct a message,
        describing the letter as occuring in the secret word a certain number
        of times, with the count value as that number.

        Args:
            count (int): The number of times the letter occurs in the secret
                word.
            letter (str): A letter that may (or may not) exist in the secret
                word.

        Returns:
            str: A sentence-long message describing [letter] as occuring in
                the secret word [count] many times.
        """

        if int(count) == 0:
            count = 'no'

        is_plural = count != 1
        copula = 'are' if is_plural else 'is'
        num_marker = "'s"  if is_plural else ''

        return f"There {copula} {count} letter {letter.upper()}{num_marker}"


class Hangman:
    """Runner for a command-line implementation of Hangman."""

    _WORDLIST_URL = 'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt'

    def __init__(self):
        all_words = requests.get(self._WORDLIST_URL).text.rstrip().split()
        self._wordlist = tuple(filter(lambda x: 5 <= len(x) <= 12, all_words))

    def launch(self, endless: bool = False, lives: int = 8):
        """Starts a fresh game of Hangman.

        Launches a game of Hangman with a randomly selected word as the secret
        word, and the provided lives to start with.

        Args:
            endless (bool): Whether or not to automatically start a new game
                after the previous one ends (default: False).
            lives (int): The number of lives to start off with (default: 8).

        Raises:
            TypeError: the value of ``lives`` must be an integer (`int`).
            ValueError: the value of ``lives`` cannot be less than 1; cannot
                start with less than 1 life.
        """

        # error checking
        if not isinstance(lives, int):
            raise TypeError(f"expected int, given {type(lives).__name__}")
        elif lives < 1:
            raise ValueError("cannot start with less than 1 life")

        original_lives = lives
        game_state = _GameState(random.choice(self._wordlist), lives)

        while game_state.lives and game_state.secret_word.hidden:
            print(game_state.summarize())

            try:
                guess = input("your guess: ")
            except EOFError: # return early if user hits CTRL+D / EOF
                print('\nGoodbye!')
                return None

            result_msg = game_state.try_guess(guess.lower())
            if result_msg: print(result_msg)
            print() # newline

        game_state.secret_word.hidden = False
        print("You win!" if game_state.lives else "Game over!")
        print(f"The secret word was \"{game_state.secret_word}\"")

        if endless:
            print() # newline
            self.launch(True, original_lives)


def main(endless: bool = False, lives: int = 8):
    """Play a game of hangman."""

    Hangman().launch(endless, lives)


if __name__ == '__main__':
    import argparse
    import inspect

    parser = argparse.ArgumentParser(
        prog=__file__.split('/')[-1],
        usage="%(prog)s [options]",
        description=main.__doc__,
    )

    for parameter in inspect.signature(main).parameters.values():
        flags = (
            f'-{parameter.name[0]}',
            f'--{parameter.name.replace('_', '-')}',
        )

        config = dict()

        if parameter.annotation == bool:
            # HACK
            action_value = 'store_false' if parameter.default else 'store_true'
            config['action'] = action_value
        else:
            config['type'] = parameter.annotation # HACK
            config['default'] = parameter.default # HACK

        # config['help'] = self._OPTION_HELP[parameter.name]

        parser.add_argument(*flags, **config)

    args = vars(parser.parse_args())
    main(**args)
