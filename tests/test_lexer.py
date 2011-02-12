import unittest
from bint import tokens, lexer


class BasicExpression(unittest.TestCase):
    
    def test_constant_expression(self):
        """ Tests whether constant expressions tokenise correctly.
        
        A constant expression is one such as 9, or "String".
        
        """ 
        constant_expressions = (
            ('9', [tokens.NumberToken(9)]),
            ('"Car"', [tokens.StringToken('Car')]),
            ('343', [tokens.NumberToken(343)]),
            ('"Two Cars"', [tokens.StringToken('Two Cars')]),
            ('end', [tokens.IdentifierToken('end')]),
            ('mod', [tokens.OpToken('mod')]),
            ('char_stuff2', [tokens.IdentifierToken('char_stuff2')]),
            ('+', [tokens.OpToken('+')]),
            ('\\', [tokens.OpToken('\\')])
        )

        self.compare(constant_expressions)

    def test_mod_variants(self):
        """ Test that strings containing mod or variants are parsed correctly.

        mod is an operator, but it appears like a valid identifier. This test
        ensures that it is treated correctly. 

        """
        modlike_expressions = (
            ('mod', [tokens.OpToken('mod')]),
            ('modern', [tokens.IdentifierToken('modern')]),
            (
                '9 mod 2', 
                [
                    tokens.NumberToken(9),
                    tokens.OpToken('mod'),
                    tokens.NumberToken(2)
                ]
            ),
            ('mod2', [tokens.IdentifierToken('mod2')])
        )

        self.compare(modlike_expressions)

    def test_escaped_strings(self):
        """ Tests whether examples of escaped quotes tokenise.

        Quotes are escaped by doubling, i.e. "He said ""Car"" " is a string
        'He said "Car" '

        """
        string_tests = (
            ('"He said ""Car""', [tokens.StringToken('He said "Car"')]),
            ('"Why so many """"quotes""""?"', [tokens.StringToken('Why so many'
            ' ""quotes""?')]),
            ('"""Starting quotes"', [tokens.StringToken('"Starting quotes')])
        )

        self.compare(string_tests)

    def test_expressions(self):
        """ Tests tokenisation of simple expressions. """
        expressions = (
            (
                '9 + 2\n',
                [
                    tokens.NumberToken(9), 
                    tokens.OpToken('+'),
                    tokens.NumberToken(2),
                    tokens.EndLineToken()
                ]
            ),
            (
                '(8 - 6)',
                [
                    tokens.OpToken('('),
                    tokens.NumberToken(8),
                    tokens.OpToken('-'),
                    tokens.NumberToken(6),
                    tokens.OpToken(')')
                ]
            ),
            (
                '32 mod 4',
                [
                    tokens.NumberToken(32),
                    tokens.OpToken('mod'),
                    tokens.NumberToken(4)
                ]
            )
        )

        self.compare(expressions)
        
    def test_statements(self):
        """ Tests some sample statements. """
        statements = (
            (
                'WHILE x < 4',
                [
                    tokens.IdentifierToken('WHILE'),
                    tokens.IdentifierToken('x'),
                    tokens.OpToken('<'),
                    tokens.NumberToken(4)
                ]
            ),
            (
                'IF y > c THEN',
                [
                    tokens.IdentifierToken('IF'),
                    tokens.IdentifierToken('y'),
                    tokens.OpToken('>'),
                    tokens.IdentifierToken('c'),
                    tokens.IdentifierToken('THEN')
                ]
            ),
            (
                'PRINT "stuff"',
                [
                    tokens.IdentifierToken('PRINT'),
                    tokens.StringToken('stuff')
                ]
            )
        )

        self.compare(statements)

    def compare(self, comparisons):
        """ Compares an tuple of tuples of the format (input, output) to the
        correct values. """
        my_lexer = lexer.BintLexer()
        for compare in comparisons:
            print('Testing {}'.format(compare[0]))
            actual_result = my_lexer.tokenise(compare[0])
            expected_result = compare[1]

            self.assertEqual(len(actual_result), len(expected_result))

            print('Comparing {} to {}'.format(actual_result,
                    expected_result))
            
            i = 0
            while i < len(actual_result):
                self.assertEqual(actual_result[i].value,
                        expected_result[i].value)
                i += 1
