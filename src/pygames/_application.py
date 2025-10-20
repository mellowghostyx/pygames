import argparse
import inspect
import pathlib
from dataclasses import dataclass
from types import FunctionType, ModuleType

from . import hangman
from . import magic_8_ball

def _get_module_version():
    """Retrieves the version number of this application.

    Finds and returns the version number of the 'pygames' application, AKA:
    this application right here. When running from the PyGames source code,
    retrieves the version number from the pyproject TOML file. Otherwise, reads
    the version number from the package's metadata.

    Returns:
        str: The version number for PyGames.
    """

    # NOTE: This method is not unit-testable: a major part of this function
    # relies on the package environment created by pipx when installing the
    # application. This cannot be adequately replicated through unit tests (at
    # least as far as I know).

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


class Application:
    """The PyGames application itself, wrapped into a single class."""

    _OPTION_HELP = {
        'endless': "automatically start a new game after the previous",
        'lives': "number of lives to start with (default: %(default)s)",
    }

    def __init__(self):
        global __version__

        self._parser = _ArgumentParser(
            prog='pygames',
            usage="%(prog)s [options] [command] ...",
            description="A collection of small CLI games written in Python",
        )

        self._parser.add_argument(
            '-v', '--version',
            action='version',
            version=f'%(prog)s {__version__}',
        )

        subparsers = self._parser.add_subparsers(
            prog=self._parser.prog,
            required=True,
        )

        for module in (hangman, magic_8_ball):
            self._add_subcommand(subparsers, module)

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

        action, kwargs = self._parse_arguments(argv)

        try:
            action(**kwargs)
        except ValueError as e:
            raise BadArgumentError(f"invalid config: {e}")

    def _add_subcommand(
        self,
        subparsers: argparse._SubParsersAction,
        module: ModuleType,
    ):
        """TODO"""

        main_function: FunctionType = getattr(module, 'main')
        name_final_dot = module.__name__.rfind('.')

        subparser = subparsers.add_parser(
            module.__name__[name_final_dot+1:].replace('_', '-'),
            usage="%(prog)s [options]",
            help=main_function.__doc__.lower(), # HACK
            description=main_function.__doc__,
        )

        for parameter in inspect.signature(main_function).parameters.values():
            flags, config = self._get_arg_info(parameter)
            subparser.add_argument(*flags, **config)

        subparser.set_defaults(function=main_function)

    def _get_arg_info(self, parameter: inspect.Parameter) -> (tuple, dict):
        """TODO"""

        flags = (
            f'-{parameter.name[0]}',
            f'--{parameter.name.replace('_', '-')}',
        )

        config = dict()

        if parameter.annotation == bool:
            # HACK
            action_value = 'store_false' if parameter.default else 'store_true'
            config['action'] = action_value
        else:
            config['type'] = parameter.annotation # HACK
            config['default'] = parameter.default # HACK

        config['help'] = self._OPTION_HELP[parameter.name]

        return (flags, config)

    def _parse_arguments(self, argv: tuple) -> (FunctionType, dict):
        """Takes CLI arguments and returns the expected function and options.

        Parses a sequence of command-line argument tokens and returns both a
        function corresponding to a subcommand called in the provided
        arguments, and a dictionary listing all arguments specified for the
        function in the provided arguments.

        Args:
            argv (tuple): A sequence of argument tokens, representing those
                inputed to the terminal or command-line for a CLI application.

        Returns:
            tuple: Consists of the primary function/action called by the
                subcommand (if applicable), and a dictionary itemizing any
                and all options specified by the provided ``argv`` arguments.
        """

        args = vars(self._parser.parse_args(argv))
        action = args.pop('function')

        return (action, args)
