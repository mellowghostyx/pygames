import argparse
import pathlib
from dataclasses import dataclass
from types import FunctionType
from .hangman import Hangman

def _get_module_version():
    pyproject_file = pathlib.Path(__file__).parents[2] / "pyproject.toml"

    if pyproject_file.exists():
        import tomllib

        with open(pyproject_file, "rb") as f:
            return tomllib.load(f)['project']['version']

    from importlib import metadata

    return metadata.version('pygames')


__version__ = _get_module_version()


class ArgumentError(Exception):
    """Error from using an invalid command-line argument."""


class _ArgumentParser(argparse.ArgumentParser):
    """TODO"""

    def error(self, message: str):
        raise ArgumentError(message)


@dataclass
class _AppOption:
    """TODO"""

    flag_short: str | None
    flag_long: str
    config: dict


@dataclass
class _AppGame:
    """TODO"""

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

    def run(self, argv): # HACK: optimize!
        """TODO"""

        args = vars(self._parser.parse_args(argv))
        launch_func = args.pop('function')
        launch_func(**args)

    def _add_game(self, subparsers, game: _AppGame):
        """TODO"""

        subparser = subparsers.add_parser(
            game.name, usage="%(prog)s [options]", help=f"play {game.name}",
            description=f"Play {game.name}"
        )

        for option in game.options:
            self._add_option(subparser, option)

        subparser.set_defaults(function=game.function)

    def _add_option(self, parser, option: _AppOption):
        """TODO"""

        if not option.flag_short:
            parser.add_argument(option.flag_long, **option.config)
            return

        parser.add_argument(
            option.flag_short, option.flag_long, **option.config
        )
