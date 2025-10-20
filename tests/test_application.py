import pytest
from types import FunctionType

from src import pygames
from src.pygames import hangman, magic_8_ball


@pytest.fixture
def fresh_app() -> pygames.Application:
    """Creates a new `Application` object.

    Returns:
        pygames.Application: The aforementioned object.
    """

    return pygames.Application()


@pytest.mark.parametrize('argv,expected_action,expected_kwargs', (
    ('hangman', hangman.main, {'endless': False, 'lives': 8}),
    ('hangman -e', hangman.main, {'endless': True, 'lives': 8}),
    ('hangman -l 73', hangman.main, {'endless': False, 'lives': 73}),
    ('hangman -e -l 3', hangman.main, {'endless': True, 'lives': 3}),
    ('magic-8-ball', magic_8_ball.main, {'endless': False}),
    ('magic-8-ball -e', magic_8_ball.main, {'endless': True}),
))
def test_application_parse_arguments_basic(
    fresh_app,
    argv: str,
    expected_action: FunctionType,
    expected_kwargs: dict,
):
    """Tests if `Application._parse_arguments()` works correctly.

    Verifies that the `_parse_arguments()` method in the `pygames.Application`
    class returns the correct data values corresponding to the provided
    command-line arguments.

    Args:
        argv (str): A series of argument tokens provided as they would be
            typed-out into the terminal/command-line. Each token must be
            separated by a whitespace character.
        expected_action (FunctionType): The first of two values expected to be
            returned by the method; represents the primary action of the
            subcommand called in the ``argv`` arguments.
        expected_kwargs (dict): The last of two values expected to be returned
            by the method; contains keyword arguments for the function
            expected to be returned alongside this value (i.e. the one that is
            expected to match ``expected_action``). The values given to each
            key in this dictionary should correspond either to values
            specified in the ``argv`` arguments, or some sort of default value.
    """

    action, kwargs = fresh_app._parse_arguments(tuple(argv.split()))

    assert action == expected_action
    assert kwargs == expected_kwargs


@pytest.mark.parametrize('argv,expected', (
    ('', 'the following arguments are required'),
    ('foo', 'invalid choice'),
    ('hangman --foo', 'unrecognized arguments'),
    ('hangman -l abc', 'invalid int value'),
    ('hangman -l -1', 'invalid config'),
))
def test_application_run_error(fresh_app, argv: str, expected: str):
    """Tests if `Application.run()` raises the right errors for bad arguments.

    Verifies that the `run()` method in the `pygames.Application` class raises
    a `pygames.BadArgumentError` exception with an appropriate correct error
    message when given an invalid set of command-line arguments.

    Args:
        argv (str): A series of argument tokens provided as they would be
            typed-out into the terminal/command-line. Each token must be
            separated by a whitespace character.
        expected (str): The error message expected from the raised
            `pygames.BadArgumentError` value.
    """

    with pytest.raises(pygames.BadArgumentError, match=expected):
        fresh_app.run(*argv.split())
