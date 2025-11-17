import argcomplete
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

        argcomplete.autocomplete(self._parser)

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

    @classmethod
    def _add_subcommand(
        cls,
        subparsers: argparse._SubParsersAction,
        module: ModuleType,
    ):
        """TODO

        Args:
            subparsers (argparse._SubParsersAction): TODO
            module (ModuleType): TODO
        """

        main_function: FunctionType = getattr(module, 'main')
        function_docstring = main_function.__doc__ or ''
        short_summary = function_docstring[:function_docstring.find('\n')+1]

        subparser = subparsers.add_parser(
            module.__name__[module.__name__.rfind('.')+1:].replace('_', '-'),
            usage="%(prog)s [options]",
            help=short_summary.lower(),
            description=short_summary,
        )

        # used to keep track of all the 1-letter flags used by the arguments
        # registered for this subcommand, so that no two arguments share the
        # same short flag
        short_flags = set()

        for parameter in inspect.signature(main_function).parameters.values():
            flags, config = cls._create_argument_data(short_flags, parameter)
            subparser.add_argument(*flags, **config)

        subparser.set_defaults(function=main_function)

    @classmethod
    def _create_argument_data(
        cls,
        short_flags: set,
        parameter: inspect.Parameter,
    ) -> (tuple, dict):
        """TODO

        Args:
            short_flags (set): TODO
            parameter (inspect.Parameter): TODO

        Returns:
            tuple: TODO
            dict: TODO
        """

        flags = cls._create_argument_flags(short_flags, parameter)
        config = dict()

        if parameter.name in cls._OPTION_HELP.keys():
            config['help'] = cls._OPTION_HELP[parameter.name]

        has_annotation = parameter.annotation != inspect.Parameter.empty
        has_default = parameter.default != inspect.Parameter.empty

        if has_default and parameter.annotation == bool:
            action_value = 'store_false' if parameter.default else 'store_true'
            config['action'] = action_value

            return (flags, config)

        if has_annotation: config['type'] = parameter.annotation
        if has_default: config['default'] = parameter.default

        return (flags, config)

    @staticmethod
    def _create_argument_flags(
        short_flags: set,
        parameter: inspect.Parameter,
    ) -> tuple:
        """TODO

        Args:
            short_flags (set): A collection of all 1-letter argument flags that
                have been registered for other arguments. This is used to
                prevent returning a short (1 letter long) flag that is already
                registered for another argument. Note that if this method adds
                a new short flag to the return value, the short flag will also
                be added to this collection.
            parameter (inspect.Parameter): TODO

        Returns:
            tuple: Contains all the argument flags that are to be registered
                for the provided parameter; Typically consists of one or two
                string values representing each of the flags.
        """

        argument_name = parameter.name.replace('_', '-')

        # A parameter with no default value will be parsed into a positional
        # argument; all positional arguments must be given its full-length,
        # non-hyphenated name as its flag.
        if parameter.default == inspect.Parameter.empty:
            return (argument_name,)

        long_flag = f'--{argument_name}'
        short_flag = f'-{argument_name[0]}'

        # Make the short flag use an uppercase letter if the lowercase variant
        # is already in use
        if short_flag in short_flags:
            short_flag = short_flag.upper()

        # If both the lowercase and uppercase short flag forms are already in
        # use, return only a long flag
        if short_flag in short_flags:
            return (long_flag,)

        short_flags.add(short_flag)
        return (short_flag, long_flag)

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
            FunctionType: The primary function/action called by the
                subcommand (if applicable).
            dict: Contains any and all options specified by the provided
                ``argv`` arguments.
        """

        args = vars(self._parser.parse_args(argv))
        action = args.pop('function')

        return (action, args)
