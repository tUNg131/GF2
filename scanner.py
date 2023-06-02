"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

import re


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """
    def __init__(self, type):
        """Initialise symbol properties."""
        self.type = type
        self.id = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """
    CLOCK = 0
    SWITCH = 1
    AND = 2
    NAND = 3
    OR = 4
    NOR = 5
    DTYPE = 6
    XOR = 7

    MONITOR = 8

    COMMA = 9
    EQUAL = 10

    NAME = 11
    CONNECTION = 12

    EOL = 13
    EOF = 14

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.names = names

        def gen():
            with open(path, 'r') as f:
                for line in f:
                    for w in line.split(" "):
                        w = w.lower()
                        if w[-1] == ',':
                            yield Symbol(self.get_type(w[:-1]))
                            yield Symbol(self.COMMA)
                        else:
                            yield Symbol(self.get_type(w))
                    yield Symbol(self.EOL)
                yield Symbol(self.EOF)

        self.symbols = gen()

    def get_type(self, w):
        if w == 'clk':
            return self.CLOCK
        elif w == 'sw':
            return self.SWITCH
        elif w == 'and':
            return self.AND
        elif w == 'nand':
            return self.NAND
        elif w == 'or':
            return self.OR
        elif w == 'nor':
            return self.NOR
        elif w == 'dtype':
            return self.DTYPE
        elif w == 'xor':
            return self.XOR
        elif w == 'mnt':
            return self.MONITOR
        elif w == '=':
            return self.EQUAL
        # device.output
        elif re.match(r"^[a-zA-Z_]{1}\w*\.\w*$", w):
            return self.CONNECTION
        # device(n)
        elif re.match(r"^[a-zA-Z_]{1}\w*\(\d+\)$", w):
            return self.NAME
        raise RuntimeError(f"Invalid symbol: {w}")

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        return next(self.symbols)
