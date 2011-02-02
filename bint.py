#!/usr/bin/python
import logging
import sys
from bint import parser, elements
class Bint:
    """This class interprets and runs a small segment of basic."""

    def __init__(self, filename):
        self.variables = {}
        logging.info('About to parse %s', filename) 
        self.program = parser.BintParser(filename).parse()
        print(self.program)

    def run(self):
        """ Runs a program that has been loaded into this Bint instance. """
        for statement in self.program:
            statement.run(self)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

Bint(sys.argv[1]).run()
