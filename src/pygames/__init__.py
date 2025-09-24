from .application import Application, ArgumentError

def run_cli():
    """TODO
    """

    # sys is only needed if this method is called (i.e. if package is used
    # as an executable), otherwise it should not be included
    import sys

    app = Application()

    try:
        app.run(*sys.argv[1:])
    except ArgumentError as e:
        sys.stderr.write(f"error: {e}\n")
        exit(1)
