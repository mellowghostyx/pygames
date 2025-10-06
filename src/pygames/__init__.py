from ._application import Application, BadArgumentError


def run_cli():
    """Launches PyGames in the command-line.

    Runs the PyGames application in the command-line, using command-line
    arguments `argv` as the arguments for the `Application.run()` method, and
    responding to any BadArgumentErrors with a brief error message and an
    early exit. This is intended for bundling the application with Poetry,
    which prefers (but does not necessarily require) executable packages to
    organize the executable section of their code into a single function.

    Note:
        This is mainly intended for running the application *as* an
        application, particularly one installed via pipx.
    """

    # sys is only needed if this method is called (i.e. if package is used
    # as an executable), otherwise it should not be included in the package
    import sys

    app = Application()

    try:
        app.run(*sys.argv[1:])
    except BadArgumentError as e:
        sys.stderr.write(f"error: {e}\n")
        exit(1)
