import pytest
from src.pygames import hangman


@pytest.mark.parametrize('letter,wrong_guesses', (
    ('a', 'bcx5&'), ('x', 'yza8@'), ('g', 'hir3%'),
))
def test_secret_letter(letter, wrong_guesses):
    secret_letter = hangman._SecretLetter(letter)

    for guess in wrong_guesses:
        assert secret_letter.guess(guess) == False
        assert secret_letter._hidden == True
        assert str(secret_letter) == '_'

    assert secret_letter.guess(letter) == True
    assert secret_letter._hidden == False
    assert str(secret_letter) == letter


@pytest.mark.parametrize('word,letter_1,letter_2,letter_0', (
    ('statement', 'a', 'e', 'x'), ('psychology', 'p', 'y', 'z'),
    ('hibernation', 'h', 'i', 'q'),
))
def test_secret_word_guess_letter_count(word, letter_1, letter_2, letter_0):
    secret_word = hangman._SecretWord(word)

    assert secret_word.guess_letter(letter_1) == 1
    assert secret_word.guess_letter(letter_2) == 2
    assert secret_word.guess_letter(letter_0) == 0


@pytest.mark.parametrize('word,guesses,expected', (
    ('statement', 'aestx', 'state_e_t'), ('psychology', 'syhoz', '_sy_ho_o_y'),
    ('hibernation', 'hibnq', 'hib__n__i_n'),
))
def test_secret_word_guess_letter_str(word, guesses, expected):
    secret_word = hangman._SecretWord(word)

    for guess in guesses:
        secret_word.guess_letter(guess)

    assert str(secret_word) == expected


@pytest.mark.parametrize('word,wrong_guesses', (
    ('statement', ('foobar', 'councilor', 'agreement')),
    ('psychology', ('foobar', 'government', 'physiology')),
    ('hibernation', ('foobar', 'achievement', 'alternation')),
))
def test_secret_word_guess_word_simple(word, wrong_guesses):
    secret_word = hangman._SecretWord(word)

    for guess in wrong_guesses:
        assert secret_word.guess_word(guess) == False

    assert secret_word.guess_word(word) == True


@pytest.mark.parametrize('word,lives,guesses,expected', (
    ('statement', 8, '', '_________ · 8 lives'),
    ('statement', 8, 'aestx', 'state_e_t · 7 lives · X'),
    ('psychology', 42, '', '__________ · 42 lives'),
    ('psychology', 42, 'bsyhoz', '_sy_ho_o_y · 40 lives · B Z'),
    ('hibernation', 13, '', '___________ · 13 lives'),
    ('hibernation', 13, 'hijvbnq', 'hib__n__i_n · 10 lives · J V Q'),
))
def test_game_state_summarize(word, lives, guesses, expected):
    game_state = hangman._GameState(word, lives)

    for guess in guesses:
        game_state.try_guess(guess)

    assert game_state.summarize() == expected


@pytest.mark.parametrize('word,invalid_guesses', (
    ('statement', ('5', '43', '@', '&%', 'b33f', 'huh?!')),
    ('psychology', ('8', '291', '#', '*^!', 'm3a7', 'whoa!')),
    ('hibernation', ('3', '14', '+', '$@()', 'g00s3', 'what?')),
))
def test_game_state_try_guess_invalid(word, invalid_guesses):
    game_state = hangman._GameState(word, 8)
    expected = "Please input a letter or word!"

    game_state.try_guess('') == expected

    for guess in invalid_guesses:
        assert game_state.try_guess(guess) == expected


@pytest.mark.parametrize('word,guess_word,guess_letter', (
    ('statement', 'councilor', 'x'), ('psychology', 'government', 'z'),
    ('hibernation', 'achievement', 'q'),
))
def test_game_state_try_guess_wrong(word, guess_word, guess_letter):
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
def test_game_state_try_guess_count(word, guess_single, guess_double):
    game_state = hangman._GameState(word, 8)

    response = game_state.try_guess(guess_single)
    assert response == f"There is 1 letter {guess_single.upper()}"

    response = game_state.try_guess(guess_double)
    assert response == f"There are 2 letter {guess_double.upper()}'s"


@pytest.mark.parametrize('letter', ('a', 'A', 'b', 'B', 'x', 'X'))
def test_game_state_generate_count_message(letter):
    game_state = hangman._GameState('foobar', 8)
    letter_upper = letter.upper()

    message = game_state._generate_count_message(0, letter)
    assert message == f"There are no letter {letter_upper}'s"

    message = game_state._generate_count_message(1, letter)
    assert message == f"There is 1 letter {letter_upper}"

    message = game_state._generate_count_message(2, letter)
    assert message == f"There are 2 letter {letter_upper}'s"
