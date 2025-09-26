import argparse
import pathlib
from dataclasses import dataclass
from types import FunctionType
from .hangman import Hangman

def _get_module_version():
    """Retrieves the version number of this application.

    Finds and returns the version number of the "pygames" application, AKA:
    this application right here. When running from the PyGames source code,
    retrieves the version number from the pyproject TOML file. Otherwise, reads
    the version number from the package's metadata.

    Returns:
        str: the version number for PyGames.
    """

    pyproject_file = pathlib.Path(__file__).parents[2] / "pyproject.toml"

    if pyproject_file.exists():
        # tomllib only needed when running from the source code
        import tomllib

        with open(pyproject_file, "rb") as f:
            return tomllib.load(f)['project']['version']

    # importlib only needed when running from a package
    from importlib import metadata

    return metadata.version('pygames')


__version__ = _get_module_version()


class BadArgumentError(Exception):
    """Error from using an invalid command-line argument."""


class _ArgumentParser(argparse.ArgumentParser):
    """Customized command line argument parser.

    A revised implementation of the ArgumentParser class in the "argparse"
    module. Instead of automatically printing an error message and exiting when
    faced with an error, it will raise a "BadArgumentError" that can be
    caught and handled separately. This makes it easier to test.
    """

    def error(self, message: str):
        raise BadArgumentError(message)


@dataclass
class _AppOption:
    """Optional argument for a command line application.

    Configuration data for an optional command-line argument that is to be
    provided by a command-line application.

    Attributes:
        flag_short (str): a short flag representing this option in the command
            line, consisting of a hyphen and a single letter.
        flag_long (str): a full-length flag representing this option in the
            command line, consisting of 2 hyphens and at least 1 word. Note that multiple words are to be delimited with a single hyphen.
        config (dict): additional configuration details for this option, which
            are to be registered by the command-line parser for this option.
    """

    flag_short: str
    flag_long: str
    config: dict


@dataclass
class _AppGame:
    """Game accessible from this application as a command-line subcommand.

    A subcommand for a command-line application, representing a particular game
    for the command-line.

    Attributes:
        name (str): the name for the subcommand.
        function (FunctionType): the function to run when the subcommand is
            used.
        options (tuple): collection of _AppOption objects representing the
            command-line options that are to be registered for this
            subcommand.
    """

    name: str
    function: FunctionType
    options: tuple


class Application:
    """TODO"""

    global __version__

    _OPTIONS = (
        _AppOption('-v', '--version', {
            'action': 'version', 'version': f"%(prog)s {__version__}",
        }),
    )
    _GAMES = (
        _AppGame('hangman', Hangman.lazy_launch, (
            _AppOption('-l', '--lives', {
                'type': int, 'default': 8,
                'help': "number of lives to start with (default: %(default)s)",
            }),
        )),
    )

    def __init__(self):
        self._parser = _ArgumentParser(
            prog='pygames', usage="%(prog)s [options] [command] ...",
            description="A collection of small CLI games written in Python"
        )

        for option in self._OPTIONS:
            self._add_option(self._parser, option)

        subparsers = self._parser.add_subparsers(
            prog=self._parser.prog, required=True
        )

        for game in self._GAMES:
            self._add_game(subparsers, game)

    def run(self, *argv): # HACK: optimize!
        """TODO

        Args:
            argv: TODO

        Raises:
            ArgumentError: The provided arguments are invalid.
        """

        args = vars(self._parser.parse_args(argv))
        launch_func = args.pop('function')
        launch_func(**args)

    def _add_game(self, subparsers, game: _AppGame):
        """TODO
        """

        subparser = subparsers.add_parser(
            game.name, usage="%(prog)s [options]", help=f"play {game.name}",
            description=f"Play {game.name}"
        )

        for option in game.options:
            self._add_option(subparser, option)

        subparser.set_defaults(function=game.function)

    def _add_option(self, parser, option: _AppOption):
        """TODO
        """

        parser.add_argument(
            option.flag_short, option.flag_long, **option.config
        )
