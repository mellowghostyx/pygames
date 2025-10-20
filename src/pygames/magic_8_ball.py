#!/usr/bin/env python3

# Copyright (c) 2025 MellowGhostyx
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""TODO"""

import random

_ANSWERS = (
    "It is certain",
    "It is decidedly so",
    "Without a doubt",
    "Yes definitely",
    "You may rely on it",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes",
    "Reply hazy, try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful",
)


def main(endless: bool = False):
    """Ask the magic 8 ball a question."""

    global _ANSWERS

    try:
        input("Your question: ") # NOTE: does not *actually* need the answer
    except EOFError:
        print("\nGoodbye!")
        return

    print("The magic 8-ball says:", random.choice(_ANSWERS))

    if endless:
        print() # newline
        main(True)


if __name__ == '__main__':
    import argparse
    import inspect

    parser = argparse.ArgumentParser(
        prog=__file__.split('/')[-1],
        usage="%(prog)s [options]",
        description=main.__doc__,
    )

    for parameter in inspect.signature(main).parameters.values():
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

        # config['help'] = self._OPTION_HELP[parameter.name]

        parser.add_argument(*flags, **config)

    args = vars(parser.parse_args())
    main(**args)
