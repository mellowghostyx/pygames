import argparse
import pathlib
from dataclasses import dataclass
from types import FunctionType
from .hangman import Hangman


def _get_module_version():
    """Retrieves the version number of this application.

    Finds and returns the version number of the 'pygames' application, AKA:
    this application right here. When running from the PyGames source code,
    retrieves the version number from the pyproject TOML file. Otherwise, reads
    the version number from the package's metadata.

    Returns:
        str: The version number for PyGames.
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
    """A customized command line argument parser.

    A revised implementation of the ArgumentParser class in the 'argparse'
    module. Instead of automatically printing an error message and exiting when
    faced with an error, it will raise a 'BadArgumentError' that can be
    caught and handled separately. This makes it easier to test.
    """

    def error(self, message: str):
        raise BadArgumentError(message)


@dataclass
class _AppOption:
    """An optional argument for a command-line application.

    Configuration data for an optional command-line argument that is to be
    provided by a command-line application.

    Attributes:
        flags (str): The flags representing this option in the command
            line. Typically this consists of a short flag: a single hyphen
            followed by a single letter, and a long flag: two hyphens followed
            by one or more words, with multiple words being delimited by a
            single hyphen.
        config (dict): Additional configuration details for this option, which
            are to be registered by the command-line parser for this option.
    """

    flags: tuple
    config: dict


@dataclass
class _Subcommand:
    """A subcommand for a command-line application.

    Configuration data for a subcommand that is to be provided by a command-line application.

    Attributes:
        name (str): The name for the subcommand.
        function (FunctionType): The function to run when the subcommand is
            called.
        options (tuple): A collection of _AppOption objects representing the
            command-line options that are to be registered to the subcommand.
    """

    name: str
    function: FunctionType
    options: tuple


class Application:
    """The PyGames application itself, wrapped into a single class."""

    global __version__

    _OPTIONS = (
        _AppOption(('-v', '--version'), {
            'action': 'version',
            'version': f"%(prog)s {__version__}",
        }),
    )
    _GAMES = (
        _Subcommand('hangman', Hangman.lazy_launch, (
            _AppOption(('-l', '--lives'), {
                'type': int,
                'default': 8,
                'help': "number of lives to start with (default: %(default)s)",
            }),
        )),
    )

    def __init__(self):
        self._parser = _ArgumentParser(
            prog='pygames',
            usage="%(prog)s [options] [command] ...",
            description="A collection of small CLI games written in Python"
        )

        for option in self._OPTIONS:
            self._parser.add_argument(*option.flags, **option.config)

        subparsers = self._parser.add_subparsers(
            prog=self._parser.prog,
            required=True
        )

        for game in self._GAMES:
            self._add_subcommand(subparsers, game)

    def run(self, *argv): # HACK: optimize!
        """Runs PyGames with the provided arguments.

        Interprets the provided `argv` strings as command-line arguments, and
        runs the corresponding PyGames action from those arguments.

        Args:
            argv: A sequence of strings representing the individual tokens in
                one or more command-line arguments.

        Raises:
            BadArgumentError: One or more arguments are invalid.
        """

        args = vars(self._parser.parse_args(argv))
        launch_func = args.pop('function')

        try:
            launch_func(**args)
        except ValueError as e:
            raise BadArgumentError(f"invalid config: {e}")

    def _add_subcommand(
        self,
        subparsers: argparse._SubParsersAction,
        game: _Subcommand,
    ):
        """Adds the provided subcommand to the argument parser.

        Args:
            subparsers (argparse._SubParsersAction): A pointer to the
                configuration data for all subparsers added to the main
                argument parser. The subcommand, and any other arguments tied
                to it, must be interpreted through a dedicated subparser,
                hence why this object is required.
            game (_Subcommand): Configuration data for the subcommand.
        """

        subparser = subparsers.add_parser(
            game.name,
            usage="%(prog)s [options]",
            help=f"play {game.name}",
            description=f"Play {game.name}"
        )

        for option in game.options:
            subparser.add_argument(*option.flags, **option.config)

        subparser.set_defaults(function=game.function)
