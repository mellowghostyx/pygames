import argparse
import inspect
import pytest
from types import CodeType, FunctionType, ModuleType

from src.pygames import _application
from src.pygames import hangman
from src.pygames import magic_8_ball


@pytest.fixture
def fresh_app() -> _application.Application:
    """Creates a new `Application` object.

    Returns:
        pygames.Application: The aforementioned object.
    """

    return _application.Application()


@pytest.fixture
def subparsers() -> argparse._SubParsersAction:
    """Creates a new `argparse._SubParsersAction` object.

    Returns:
        argparse._SubParsersAction: The aforementioned object.
    """

    parser = _application._ArgumentParser(
        prog='foobar',
        usage="%(prog)s [options]",
        description="Lorem ipsum dolor sit amet.",
    )

    return parser.add_subparsers(
        prog=self._parser.prog,
        required=True,
    )


@pytest.fixture
def main_function() -> FunctionType:
    """Creates a new `main()` function.

    Defines a new function named `main` with three parameters:

    - `foo`: string value
    - `bar`: optional boolean value that defaults to False
    - `baz`: optional integer value that defaults to 8

    Returns:
        FunctionType: The aforementioned function.
    """

    def main(foo: str, bar: bool = False, baz: int = 5):
        """Lorem ipsum dolor sit amet."""
        pass

    return main


@pytest.fixture
def game_module(main_function) -> ModuleType:
    """Creates a new `ModuleType` object with a `main()` function.

    Returns:
        ModuleType: The aforementioned module/object.
    """

    game = ModuleType('foobar', "Lorem ipsum dolor sit amet.")
    game.main = main_function


@pytest.fixture
def parameters(main_function) -> tuple:
    """Creates a tuple of three `inspect.Parameter` objects.

    Returns:
        tuple: The aforementioned collection of parameter objects.
    """

    return tuple(inspect.signature(main_function).parameters.values())


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

    with pytest.raises(_application.BadArgumentError, match=expected):
        fresh_app.run(*argv.split())


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


# def test_application_add_subcommand(fresh_app, subparsers, game_module):
#     """TODO"""

#     fresh_app._add_subcommand(subparsers, game_module)

#     subcommands: dict = subparsers._get_positional_actions[0].choices
#     assert 'foobar' in subcommands.keys()

#     actual = subcommands['foobar']
#     assert actual.description == "Lorem ipsum dolor sit amet."

#     # TODO


def test_application_create_argument_data(fresh_app, parameters):
    """TODO
    """

    short_flags = set()

    actual = []

    for parameter in parameters:
        _, config = fresh_app._create_argument_data(short_flags, parameter)
        actual.append(config)

    assert tuple(actual) == (
        {'type': str},
        {'action': 'store_true'},
        {'type': int, 'default': 5},
    )


@pytest.mark.parametrize('short_flags,expected', (
    (set(), (('foo',), ('-b', '--bar'), ('-B', '--baz'))),
    ({'-b'}, (('foo',), ('-B', '--bar'), ('--baz',))),
    ({'-b', '-B'}, (('foo',), ('--bar',), ('--baz',))),
))
def test_application_create_argument_flags(
    fresh_app,
    parameters,
    short_flags: set,
    expected: tuple,
):
    """TODO

    Args:
        short_flags (set): TODO
        expected (tuple): TODO
    """

    actual = []

    for parameter in parameters:
        actual.append(fresh_app._create_argument_flags(short_flags, parameter))

    assert tuple(actual) == expected
