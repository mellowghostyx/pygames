#!/usr/bin/env python3

import random
import requests


class _SecretLetter:
    def __init__(self, letter: str):
        self.letter = str(letter)
        self.hidden = True

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

        if str(letter) == self.letter:
            self.hidden = False
            return True

        return False

    def __str__(self):
        return '_' if self.hidden else self.letter


class _SecretWord:
    def __init__(self, word: str):
        self.word = str(word)
        self.slots = [_SecretLetter(letter) for letter in self.word]
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

        for n in range(0, len(self.slots)):
            if self.slots[n].guess(letter): count += 1

        if not any([slot.hidden for slot in self.slots]):
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

        if str(word) == self.word:
            self.hidden = False
            return True

        return False

    def __str__(self):
        if not self.hidden:
            return self.word

        return ''.join([str(slot) for slot in self.slots])

class _GameState:
    def __init__(self, secret_word: str, lives: int):
        self.secret_word = _SecretWord(secret_word)
        self.lives = lives
        self.guesses = set()

        # String representation of all the wrong (letter) guesses made so far
        self._wrong_guesses = ''

    def summarize(self) -> str:
        """TODO"""

        summary = f"{self.secret_word} · {self.lives} lives"

        if self._wrong_guesses:
            summary += f" · {self._wrong_guesses}"

        return summary

    def try_guess(self, guess: str) -> str:
        """TODO

        Args:
            guess (str): The guess to try.
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

        Uses the provided "count" and "letter" values to construct a message,
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
    _WORDLIST_URL = 'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt'

    def __init__(self):
        all_words = requests.get(self._WORDLIST_URL).text.rstrip().split()
        self._wordlist = tuple(filter(lambda x: 5 <= len(x) <= 12, all_words))

    def launch(self, lives: int = 8):
        if not isinstance(lives, int):
            raise TypeError(f"expected int, given {type(lives).__name__}")

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

    @classmethod
    def lazy_launch(cls, lives: int = 8):
        cls().launch(lives)

if __name__ == '__main__':
    Hangman.lazy_launch()
