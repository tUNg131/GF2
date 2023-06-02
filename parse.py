"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

import itertools
from scanner import Symbol


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self._names = names
        self._devices = devices
        self._network = network
        self._monitors = monitors
        self._scanner = scanner

    def parse_network(self):
        """Parse the circuit definition file."""

        device_id = itertools.count(0)

        symbols = []
        EOF_flag = False
        while not EOF_flag:
            while True:
                sym = self._scanner.get_symbol()

                if sym.type in (Symbol.NL, Symbol.EOF):
                    EOF_flag = True
                    break
                symbols.append(sym)

            first = symbols[0]
            if first.type == Symbol.NAME:
                if len(symbols) != 3:
                    raise RuntimeError

                if symbols[1].type != Symbol.EQUALS:
                    raise RuntimeError

                if symbols[2].type != Symbol.NAME:
                    raise RuntimeError
                
                first_device_id, first_port_id = self._devices.get_signal_ids(
                    self._names.get_name_string(first.id))
                
                second = symbols[2]
                second_device_id, second_port_id = self._devices.get_signal_ids(
                    self._names.get_name_string(second.id))

                self._network.make_connection(
                    first_device_id, first_port_id, second_device_id, second_port_id)
            elif first.type == Symbol.DEF:
                expecting_comma = False
                for sym in symbols[1:]:
                    if expecting_comma:
                        if sym.type != Symbol.COMMA:
                            raise RuntimeError("Expecting comma")
                        expecting_comma = False
                        continue

                    if first.type == Symbol.AND:
                        self._devices.make_gate(next(device_id), self._devices.AND, sym.data)
                    elif first.type == Symbol.NAND:
                        self._devices.make_gate(next(device_id), self._devices.NAND, sym.data)
                    elif first.type == Symbol.OR:
                        self._devices.make_gate(next(device_id), self._devices.OR, sym.data)
                    elif first.type == Symbol.NOR:
                        self._devices.make_gate(next(device_id), self._devices.NOR, sym.data)
                    elif first.type == Symbol.XOR:
                        if first.data != 2:
                            raise RuntimeError
                        self._devices.make_gate(next(device_id), self._devices.XOR, 2)
                    elif first.type == Symbol.CLK:
                        # Clock_half_period is an integer > 0
                        if not isinstance(first.data, int) or first.data <= 0:
                            raise RuntimeError
                        self._devices.make_clock(next(device_id), self._devices.CLOCK, first.data)
                    elif first.type == Symbol.SW:
                        self._devices.make_switch(next(device_id), self._devices.SWITCH, bool(first.data))
                    elif first.type == Symbol.DTYPE:
                        self._devices.make_d_type(next(device_id))
                    else:
                        raise RuntimeError
                if not expecting_comma:
                    raise RuntimeError("end of line has to expect comma")
            elif first.type == Symbol.MONITOR:
                pass
            symbols = []

        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True
