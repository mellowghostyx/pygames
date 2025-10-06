"""TODO
"""

import pytest
from src.pygames import hangman


@pytest.mark.parametrize('letter,wrong_guesses', (
    ('a', 'bcx5&'), ('x', 'yza8@'), ('g', 'hir3%'),
))
def test_secret_letter(letter: str, wrong_guesses: str):
    """Tests the `hangman._SecretLetter` class.

    Verifies that the `guess()` method in the `hangman._SecretLetter` class
    can take a 1-character string argument and correctly return a boolean
    value representing whether or not the guess matches the secret letter.

    Args:
        letter (str): A letter to initialize the `hangman._SecretLetter`
            object with.
        wrong_guesses (str): A sequence containing characters other than the
            value for the ``letter`` argument. Each character, as an argument,
            must result in the `guess()` method returning False.
    """

    secret_letter = hangman._SecretLetter(letter)

    for guess in wrong_guesses:
        assert secret_letter.guess(guess) == False
        assert secret_letter._hidden == True
        assert str(secret_letter) == '_'

    assert secret_letter.guess(letter) == True
    assert secret_letter._hidden == False
    assert str(secret_letter) == letter


@pytest.mark.parametrize('word,letter_once,letter_twice,letter_none', (
    ('statement', 'a', 'e', 'x'), ('psychology', 'p', 'y', 'z'),
    ('hibernation', 'h', 'i', 'q'),
))
def test_secret_word_guess_letter_count(
    word: str,
    letter_once: str,
    letter_twice: str,
    letter_none: str,
):
    """Tests if `_SecretWord.guess_letter()` returns the right letter count.

    Verifies that the `guess_letter()` method in the `hangman._SecretWord`
    class can take a letter argument and return the correct number of times
    that letter occurs in the secret word.

    Args:
        word (str): A word to initialized the `hangman._SecretWord` object
            with.
        letter_once (str): A letter that occurs in the secret word *once*.
        letter_twice (str): A letter that occurs in the secret word *twice*.
        letter_none (str): A letter that does not occur in the secret word at
            all.
    """

    secret_word = hangman._SecretWord(word)

    assert secret_word.guess_letter(letter_once) == 1
    assert secret_word.guess_letter(letter_twice) == 2
    assert secret_word.guess_letter(letter_none) == 0


@pytest.mark.parametrize('word,guesses,expected', (
    ('statement', 'aestx', 'state_e_t'), ('psychology', 'syhoz', '_sy_ho_o_y'),
    ('hibernation', 'hibnq', 'hib__n__i_n'),
))
def test_secret_word_guess_letter_str(word: str, guesses: str, expected: str):
    """Tests if `_SecretWord.guess_letter()` correctly changes __str__ value.

    Verifies that the `guess_letter()` method in the `hangman._SecretWord`
    class correctly changes how the secret word is presented when parsed
    into a string.

    Args:
        word (str): A word to initialized the `hangman._SecretWord` object
            with.
        guesses (str): A sequence containing all the letters that are to be
            guessed on for the word.
        expected (str): The value expected from parsing the secret word into a
            string, after trying all the guesses from ``guesses``.
    """

    secret_word = hangman._SecretWord(word)

    for guess in guesses:
        secret_word.guess_letter(guess)

    assert str(secret_word) == expected


@pytest.mark.parametrize('word,wrong_guesses', (
    ('statement', ('foobar', 'councilor', 'agreement')),
    ('psychology', ('foobar', 'government', 'physiology')),
    ('hibernation', ('foobar', 'achievement', 'alternation')),
))
def test_secret_word_guess_word(word: str, wrong_guesses: tuple):
    """TODO

    Args:
        word (str): A word to initialized the `hangman._SecretWord` object
            with.
        wrong_guesses (tuple): TODO
    """

    secret_word = hangman._SecretWord(word)

    # the expected value returned by `secret_word.__str__` before the correct
    # guess is given
    expected_str = '_' * len(word)

    for guess in wrong_guesses:
        assert secret_word.guess_word(guess) == False
        assert secret_word.hidden == True
        assert str(secret_word) == expected_str

    assert secret_word.guess_word(word) == True
    assert secret_word.hidden == False
    assert str(secret_word) == word


@pytest.mark.parametrize('word,lives,guesses,expected', (
    ('statement', 8, '', '_________ · 8 lives'),
    ('statement', 8, 'aestx', 'state_e_t · 7 lives · X'),
    ('psychology', 42, '', '__________ · 42 lives'),
    ('psychology', 42, 'bsyhoz', '_sy_ho_o_y · 40 lives · B Z'),
    ('hibernation', 13, '', '___________ · 13 lives'),
    ('hibernation', 13, 'hijvbnq', 'hib__n__i_n · 10 lives · J V Q'),
))
def test_game_state_summarize(
    word: str,
    lives: int,
    guesses: str,
    expected: str,
):
    """TODO

    Args:
        word (str): TODO
        lives (int): TODO
        guesses (str): TODO
        expected (str): TODO
    """

    game_state = hangman._GameState(word, lives)

    for guess in guesses:
        game_state.try_guess(guess)

    assert game_state.summarize() == expected


@pytest.mark.parametrize('word,invalid_guesses', (
    ('statement', ('5', '43', '@', '&%', 'b33f', 'huh?!')),
    ('psychology', ('8', '291', '#', '*^!', 'm3a7', 'whoa!')),
    ('hibernation', ('3', '14', '+', '$@()', 'g00s3', 'what?')),
))
def test_game_state_try_guess_invalid(word: str, invalid_guesses: tuple):
    """TODO

    Args:
        word (str): TODO
        invalid_guesses (str): TODO
    """

    game_state = hangman._GameState(word, 8)
    expected = "Please input a letter or word!"

    game_state.try_guess('') == expected

    for guess in invalid_guesses:
        assert game_state.try_guess(guess) == expected


@pytest.mark.parametrize('word,guess_word,guess_letter', (
    ('statement', 'councilor', 'x'), ('psychology', 'government', 'z'),
    ('hibernation', 'achievement', 'q'),
))
def test_game_state_try_guess_wrong(
    word: str,
    guess_word: str,
    guess_letter: str,
):
    """TODO

    Args:
        word (str): TODO
        guess_word (str): TODO
        guess_letter (str): TODO
    """

    game_state = hangman._GameState(word, 8)

    response = game_state.try_guess(guess_word)
    assert response == "Sorry, but that was not the correct word"

    response = game_state.try_guess(guess_word) # repeat word guess
    assert response == "You already made this guess!"

    response = game_state.try_guess(guess_letter)
    assert response == f"There are no letter {guess_letter.upper()}'s"

    response = game_state.try_guess(guess_letter) # repeat letter guess
    assert response == "You already made this guess!"


@pytest.mark.parametrize('word,guess_single,guess_double', (
    ('statement', 'a', 'e'), ('psychology', 'p', 'y'),
    ('hibernation', 'h', 'i'),
))
def test_game_state_try_guess_count(
    word: str,
    guess_single: str,
    guess_double: str,
):
    """TODO

    Args:
        word (str): TODO
        guess_single (str): TODO
        guess_double (str): TODO
    """

    game_state = hangman._GameState(word, 8)

    response = game_state.try_guess(guess_single)
    assert response == f"There is 1 letter {guess_single.upper()}"

    response = game_state.try_guess(guess_double)
    assert response == f"There are 2 letter {guess_double.upper()}'s"


@pytest.mark.parametrize('letter', ('a', 'A', 'b', 'B', 'x', 'X'))
def test_game_state_generate_count_message(letter: str):
    """TODO

    Args:
        letter (str): TODO
    """

    game_state = hangman._GameState('foobar', 8)
    letter_upper = letter.upper()

    message = game_state._generate_count_message(0, letter)
    assert message == f"There are no letter {letter_upper}'s"

    message = game_state._generate_count_message(1, letter)
    assert message == f"There is 1 letter {letter_upper}"

    message = game_state._generate_count_message(2, letter)
    assert message == f"There are 2 letter {letter_upper}'s"
