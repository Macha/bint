from bint.elements import *
import logging

class InvalidExpressionException(Exception): pass
class InvalidStatementException(Exception): pass

class BintParser:
    """ This class parses a bint file into a python object. """

    def __init__(self, filename):
        self.statement_matches = [
            ('IF', self.read_if),
            ('WHILE', self.read_while),
            ('LET', self.read_let),
            ('INPUT', self.read_input),
            ('PRINT', self.read_print)
        ]

        with open(filename) as source:
            self.lines = source.readlines()
            self.current_line = 0
            self.statements = []
            

    def parse(self):
        """ Parses the currently loaded file. """
        while self.current_line < len(self.lines):
            logging.debug('\n\nParsing line %s\n%s', self.current_line,
                    self.lines[self.current_line].strip())
            statement = self.read_statement()
            if statement is not None:
                self.statements.append(statement)
        
        return self.statements


    def read_statement(self):
        """ Reads a statement of a unknown type. """
        parse_line = self.lines[self.current_line].strip()
        
        # Yes, I know this sucks, and there probably is a better way to handle
        # it
        for special in [',', '+', '-', '*', '\\', '<=', '>=', '<>', '<=', '>=']:
            parse_line = self.lines[self.current_line] = parse_line.replace(special, 
                    ' %s ' % special)

        # Reconnect borken operators
        for fix_needing_special, fixed in [
                ('<  =', '<='), 
                ('>  =', '>='), 
                ('<  >', '<>'),
            ]:
            parse_line = self.lines[self.current_line] = parse_line.replace(
                    fix_needing_special, fixed)
        
        for statement in self.statement_matches:
            if parse_line.startswith(statement[0]):
                return_val = statement[1]()
                self.current_line += 1
                return return_val
        
        # Assignment statements contain no unique words, identified as the
        # remaining option. Will need to be changed if further statements are
        # added.
        if(parse_line != ''):
            return_val = self.read_assignment()
            self.current_line += 1
            return return_val
        else: # Just whitespace
            self.current_line += 1


    def read_assignment(self):
        """ Reads in an assignment statement. """
        parse_line = self.lines[self.current_line]
        logging.debug('Reading line %s as assignment\n%s', self.current_line,
                parse_line)
        assert('=' in parse_line)
        target, remaining = self.read_element(parse_line)
        if not isinstance(target, VariableValue):
            raise InvalidStatementException('Can only assign to variables.')
        else:
            value = self.read_expression(remaining.strip(' \t='))
            return AssignmentStatement(target, value)


    def read_input(self):
        """ Reads in input statement. """
        assert('INPUT' in self.lines[self.current_line])
        parse_line = self.lines[self.current_line]
        parse_line = parse_line.replace('INPUT', '').strip()
        logging.debug('Found input statement for %s', parse_line)
        return InputStatement(parse_line)


    def read_print(self):
        """ Reads a print statement. """
        assert('PRINT' in self.lines[self.current_line])
        parse_line = self.lines[self.current_line]
        parse_line = parse_line.replace('PRINT', '').strip()
        
        elements = []
        logging.debug('Parsing for PRINT')
        while True:
            element, parse_line = self.read_element(parse_line)
            logging.debug('Adding element %s to print statement', element)
            parse_line = parse_line.strip()
            elements.append(element)
            
            if not parse_line.startswith(','):
                break
            else:
                parse_line = parse_line[1:] # Drop the comma for next pass

        return PrintStatement(elements)


    def read_let(self):
        """ Reads a let statement. """
        assert('LET' in self.lines[self.current_line])
        parts = self.lines[self.current_line].split()
        # Format is LET(0) NAME(1) =(2) VALUE(3...)
        name = parts[1]
        value = self.read_expression(' '.join(parts[3:]))
        return LetStatement(name, value)


    def read_if(self):
        """ Reads an if statement. """
        assert('IF' in self.lines[self.current_line])
        parse_line = self.lines[self.current_line]
        parse_line = parse_line.replace('IF', '')
        parse_line = parse_line.replace('THEN', '')
        cond = self.read_expression(parse_line)
        
        self.current_line += 1

        statements = []
        while 'END IF' not in self.lines[self.current_line]:
            statement = self.read_statement()
            if statement is not None:
                statements.append(statement)

        return IfStatement(cond, statements)


    def read_while(self):
        """ Reads a while statement. """
        assert('WHILE' in self.lines[self.current_line])
        cond_line = self.lines[self.current_line]
        cond_line = cond_line.replace('WHILE', '')
        cond = self.read_expression(cond_line)

        self.current_line += 1

        statements = []

        while 'WEND' not in self.lines[self.current_line]:
            statement = self.read_statement()
            if statement is not None:
                statements.append(statement)

        return WhileStatement(cond, statements)


    def read_expression(self, expr):
        """ Reads an expression. """
        logging.debug('Reading expression %s', expr)
        first_part, remaining = self.read_element(expr)
        logging.debug('Got %s, parsing %s', first_part, remaining)
        words = remaining.split()
        if words == []:
            return first_part

        op = words[0]
        logging.debug('Got op %s', op)
        
        second_part = self.read_element(' '.join(words[1:]))[0]
        if op in ['+', '-', '*', '\\', 'mod']:
            return MathExpression(first_part, op, second_part)
        elif op in ['<', '<=', '>', '>=', '=', '<>']:
            return BooleanExpression(first_part, op, second_part)
        else:
            raise InvalidExpressionException('Unsupported operator')


    def read_element(self, expr):
        """ 
        Reads a single element. Returns a tuple of the element that was
        read, and the remaining characters in the argument.
        """
        expr = expr.strip()
        words = expr.split()
        element = words[0]
        remaining = ' '.join(words[1:])

        if element.isnumeric():
            logging.debug('Parsed literal %s', words[0])
            return LiteralValue(int(words[0])), remaining

        elif element.isalpha():
            logging.debug('Found reference to variable %s', words[0])
            return VariableValue(words[0]), remaining

        elif element.startswith('"'):
            string_value, parsed_chars = self.read_string(expr)
            return string_value, expr[parsed_chars:]

        elif element.startswith('('):
            string_expr, parsed_chars = self.get_inner_expression(expr)
            return self.read_expression(string_expr), expr[parsed_chars:]

        else:
            raise InvalidExpressionException('Invalid element %s' % words[0])


    def get_inner_expression(self, expr):
        """ Gets an inner expression within a larger expression. """
        assert(expr[0] == '(')
        logging.debug('Getting inner expression in:\n %s', expr)
        chars = []
        num_exprs = 1
        parsed_chars = 0

        for char in expr[1:]:
            parsed_chars += 1
            if char == '(': # Ignore inner sub-expressions for now.
                num_exprs += 1
                chars.append(char)
            elif char == ')':
                num_exprs -= 1
                if num_exprs == 0:
                    parsed_chars += 1
                    break # And we're done
                else:
                    chars.append(char)
            else:
                chars.append(char)

        # If we have too many parens
        if num_exprs != 0:
            raise InvalidExpressionException('Unbalanced parentheses on line %s',
                    self.current_line)
        else:
            inner_expression = ''.join(chars) # Strip parens out
            return inner_expression, parsed_chars


    def read_string(self, expr):
        """ 
        Reads in a string from an expression. strings are inside quotes,
        and quotes in strings are escaped by repeating them. 
        """
        assert(expr[0] == '"')
        logging.debug('Reading %s as string', expr)
        chars = []
        num_quotes = 0
        current_char = 1
        parsed_chars = 1
        while current_char < len(expr):
            char = expr[current_char]
            parsed_chars += 1
            
            # Handle strings at the end of expressions
            try:
                next_char = expr[current_char + 1]
            except IndexError:
                next_char = ''


            if char != '"':
                chars.append(char)
            elif num_quotes == 0 and next_char != '"':
                break
            elif num_quotes < 2:
                num_quotes += 1
            elif num_quotes == 2:
                chars.append(char)
                num_quotes = 0

            current_char += 1

        return LiteralValue(''.join(chars)), parsed_chars
