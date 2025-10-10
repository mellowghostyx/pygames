import pytest
from types import FunctionType

from src import pygames

HANGMAN_LAUNCH = pygames.hangman.Hangman.lazy_launch


@pytest.fixture
def fresh_app() -> pygames.Application:
    """TODO

    Returns:
        pygames.Application: TODO
    """

    return pygames.Application()


@pytest.mark.parametrize('argv,expected_action,expected_kwargs', (
    ('hangman', HANGMAN_LAUNCH, {'lives': 8}),
    ('hangman -l 73', HANGMAN_LAUNCH, {'lives': 73}),
))
def test_application_parse_arguments(
    fresh_app,
    argv: str,
    expected_action: FunctionType,
    expected_kwargs: dict,
):
    """TODO

    Args:
        argv (str): TODO
        expected_action (FunctionType): TODO
        expected_kwargs (dict): TODO
    """

    action, kwargs = fresh_app._parse_arguments(argv.split())

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
    """TODO

    Args:
        argv (str): TODO
        expected (str): TODO
    """

    with pytest.raises(pygames.BadArgumentError, match=expected):
        fresh_app.run(*argv.split())
