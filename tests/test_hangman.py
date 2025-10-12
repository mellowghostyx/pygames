import pytest
from src.pygames import hangman


@pytest.fixture
def secret_word() -> hangman._SecretWord:
    return hangman._SecretWord('application')


@pytest.fixture
def game_state() -> hangman._GameState:
    return hangman._GameState('application', 8)


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


@pytest.mark.parametrize('guess,expected', (
    ('a', 2), ('p', 2), ('l', 1), ('i', 2), ('c', 1),
    ('t', 1), ('o', 1), ('n', 1), ('x', 0), ('y', 0),
))
def test_secret_word_guess_letter_count(
    secret_word,
    guess: str,
    expected: int,
):
    """Tests if `_SecretWord.guess_letter()` returns the right letter count.

    Verifies that the `guess_letter()` method in the `hangman._SecretWord`
    class can take a letter argument and return the correct number of times
    that letter occurs in the secret word.

    Args:
        guess (str): The letter to use as a guess for the secret word.
        expected (int): The value expected to be returned by the method; the
            number of times the letter *actually* occurs in the secret word.
    """

    assert expected == secret_word.guess_letter(guess)


@pytest.mark.parametrize('guesses,expected', (
    ('', '___________'), ('aio', 'a___i_a_io_'), ('pcn', '_pp__c____n'),
    ('ltxy', '___l___t___'), ('qwz', '___________'),
))
def test_secret_word_guess_letter_str(
    secret_word,
    guesses: str,
    expected: str,
):
    """Tests if `_SecretWord.guess_letter()` correctly changes __str__ value.

    Verifies that the `guess_letter()` method in the `hangman._SecretWord`
    class correctly changes how the secret word is presented when parsed
    into a string.

    Args:
        guesses (str): A sequence of letters that are to be used as guesses
            for the secret word.
        expected (str): The value expected to be returned by the method; the
            secret word (as a string) with only the letters correctly guessed
            on the secret word revealed, with all other letters replaced with
            underscores.
    """

    for guess in guesses:
        secret_word.guess_letter(guess)

    assert expected == str(secret_word)


@pytest.mark.parametrize('guess', ('foobar', 'generation', 'applications'))
def test_secret_word_guess_word_wrong(secret_word, guess: str):
    """Tests if `_SecretWord.guess_word()` responds correctly to wrong guesses.

    Verifies that the `guess_word()` method in the `hangman._SecretWord` class
    Does the following in response to an incorrect guess:

    1. returns False
    2. keeps the `hidden` attribute as True
    3. does not reveal the secret word when parsed into a string

    Args:
        guess (tuple): A sequence of strings containing the words to use as
            guesses for the secret word. None of the words in this sequence
            can match the secret word.
    """

    assert not secret_word.guess_word(guess)
    assert secret_word.hidden
    assert str(secret_word) == '_' * len(secret_word._slots)


def test_secret_word_guess_word_right(secret_word):
    """Tests if `_SecretWord.guess_word()` responds correctly to right guesses.

    Verifies that the `guess_word()` method in the `hangman._SecretWord` class
    Does the following in response to a *correct* guess:

    1. returns True
    2. changes the `hidden` attribute to False
    3. reveals the secret word when parsed into a string

    Args:
        None
    """

    assert secret_word.guess_word(secret_word._word)
    assert not secret_word.hidden
    assert str(secret_word) == secret_word._word


@pytest.mark.parametrize('guesses,expected', (
    ('', '___________ · 8 lives'),
    ('lctn', '___l_c_t__n · 8 lives'),
    ('apix', 'app_i_a_i__ · 7 lives · X'),
    ('xyz', '___________ · 5 lives · X Y Z'),
))
def test_game_state_summarize(game_state, guesses: str, expected: str):
    """Tests if `_GameState.summarize()` works correctly.

    Verifies that the `summarize()` method in the `hangman._GameState` class
    returns the expected 1-line summary after the provided guesses are tried.

    Args:
        guesses (str): A sequence of letters to use as guesses for the secret
            word.
        expected (str): The value expected to be returned by the method; A
            1-line summary of the game state, listing the secret word (with
            unguessed letters replaced with underscores), the number of lives
            remaining, and any wrong letter guesses made (if applicable).
    """

    for guess in guesses:
        game_state.try_guess(guess)

    assert game_state.summarize() == expected


@pytest.mark.parametrize('guess', ('5', '43','@', '&%', 'g00s3', 'huh?!'))
def test_game_state_try_guess_invalid(game_state, guess: str):
    """Tests if `_GameState.try_guess()` responds correctly to invalid guesses.

    Verifies that the `try_guess()` method in the `hangman._GameState` class
    returns the "Please input a letter or word!" message when provided an
    invalid guess value.

    Args:
        guess (str): A guess to try on the secret word; must contain at *least*
            one character not in the Latin alphabet.
    """

    for _ in range(2):
        # NOTE: This message should return for invalid guess values, even if
        # the value was repeated
        assert game_state.try_guess(guess) == "Please input a letter or word!"

    assert game_state.lives == 8 # lives value should not decrease


@pytest.mark.parametrize('guess', ('a', 'x', 'foobar'))
def test_game_state_try_guess_repeated(game_state, guess: str):
    """Tests if `_GameState.try_guess()` responds correctly to repeat guesses.

    Verifies that the `try_guess()` method in the `hangman._GameState` class
    returns the "You already made this guess!" message when provided a repeat
    guess value (i.e. a value that was already passed to the method).

    Args:
        guess (str): A guess to try on the secret word; must contain *only*
            letters in the Latin alphabet.
    """

    game_state.try_guess(guess)
    expected_lives = game_state.lives

    assert game_state.try_guess(guess) == "You already made this guess!"
    assert game_state.lives == expected_lives # lives value should not decrease


@pytest.mark.parametrize('guess,expected,lowers_lives', (
    ('foobar', "Sorry, but that was not the correct word", True),
    ('z', "There are no letter Z's", True),
    ('n', "There is 1 letter N", False),
    ('p', "There are 2 letter P's", False),
))
def test_game_state_try_guess_regular(
    game_state,
    guess: str,
    expected: str,
    lowers_lives: bool,
):
    # """TODO

    # Args:
    #     guess (str): TODO
    #     expected (str): TODO
    #     lowers_lives (bool): TODO
    # """

    assert game_state.try_guess(guess) == expected
    assert lowers_lives == (game_state.lives == 7)

@pytest.mark.parametrize('letter', ('a', 'b', 'x'))
def test_game_state_generate_count_message(game_state, letter: str):
    # """TODO

    # Args:
    #     letter (str): TODO
    # """

    letter_upper = letter.upper()

    expected_messages = (
        f"There are no letter {letter_upper}'s",
        f"There is 1 letter {letter_upper}",
        f"There are 2 letter {letter_upper}'s",
    )

    for i, expected in enumerate(expected_messages):
        actual_lower = game_state._generate_count_message(i, letter)
        actual_upper = game_state._generate_count_message(i, letter_upper)

        assert actual_lower == actual_upper
        assert actual_upper == expected
