import logging
import operator


class NoSuchVariableException(Exception):
    pass


class Statement:
    pass


class LetStatement(Statement):
    """Represents a LET statement, which sets a variable. """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def run(self, scope):
        initial_value = self.value.eval(scope)
        logging.debug('Creating %s with value %s', self.name,
                initial_value)
        scope.variables[self.name] = initial_value


class PrintStatement(Statement):
    """Represents a print statement. """
    def __init__(self, values):
        """ Sets up a print statement to be run later."""
        self.values = values

    def run(self, scope):
        for value in self.values:
            print(value.eval(scope), end=' ')
        print()

    def __str__(self):
        return '<PrintStatement: %s>' % str(self.values)


class InputStatement(Statement):
    """ Represents a INPUT statement."""

    def __init__(self, target):
        """ Sets up an INPUT statement to run later. """
        self.target = target

    def run(self, scope):
        """ Runs an input statement. """
        scope.variables[self.target] = int(input())

    def __str__(self):
        return '<InputStatement: %s>' % self.name


class AssignmentStatement(Statement):
    """ Represents an assignment statement. """
    def __init__(self, target, value):
        self.target = target
        self.value = value

        logging.debug('Found assignment of %s with val %s', target, value)

    def run(self, scope):
        if self.target.name not in scope.variables:
            raise NoSuchVariableException('%s does not exist'
                    % self.target.name)
        else:
            scope.variables[self.target.name] = self.value.eval(scope)

    def __str__(self):
        return '<AssignmentStatement: %s %s>' % (self.target, self.value)


class IfStatement(Statement):
    """ Represents an if statement. """
    def __init__(self, cond, statements):
        """ Prepares an If statement to be run later. """
        self.cond = cond
        self.statements = statements

    def run(self, scope):
        """ Runs an if statement. """
        if self.cond.eval(scope):
            logging.debug('Running If Statement contents')
            for statement in self.statements:
                statement.run(scope)

    def __str__(self):
        return '<IfStatement: %s %s>' % (self.cond, self.statements)


class WhileStatement(Statement):
    """ Represents a while statement. """
    def __init__(self, cond, statements):
        """ Prepares a while statement to run later. """
        self.cond = cond
        self.statements = statements

    def run(self, scope):
        """ Runs a while statement. """
        while True:
            if self.cond.eval(scope):
                for statement in self.statements:
                    statement.run(scope)
            else:
                break

    def __str__(self):
        return '<WhileStatement: %s %s>' % (self.cond, self.statements)


class Expression:
    """ Represents any sort of expression. """

    def __init__(self, first_value, op, second_value):
        """
        Sets up the expression, where first_value and second_value are
        integers and op is a string.
        """
        self.first_value = first_value
        self.op = op
        self.second_value = second_value

    def eval(self, scope):
        """ Gets the value of a expression. """
        logging.debug('Applying %s to %s and %s', self.op,
                self.first_value.eval(scope),
                self.second_value.eval(scope))
        result = self.ops[self.op](self.first_value.eval(scope),
                self.second_value.eval(scope))
        return result

    def __str__(self):
        return '<Expression: %s %s %s>' % (self.first_value, self.op,
                self.second_value)


class MathExpression(Expression):
    """Represents a math expression."""
    ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '\\': operator.floordiv,
            'mod': operator.mod
            }


class BooleanExpression(Expression):
    """Represents a comparison expression."""
    ops = {
            '<=': operator.le,
            '<': operator.lt,
            '>': operator.gt,
            '>=': operator.ge,
            '<>': operator.ne,
            '=': operator.eq
            }


class Value:
    pass


class LiteralValue():
    """ Represents a literal. """
    def __init__(self, value):
        self.value = value

    def eval(self, scope):
        return self.value

    def __str__(self):
        return '<Literal: %s>' % self.value


class VariableValue():
    """ Represents a variable. """
    def __init__(self, name):
        self.name = name

    def assign(self, scope, value):
        scope.variables[self.name] = value.eval(scope)

    def eval(self, scope):
        return scope.variables[self.name]

    def __str__(self):
        return '<Variable: %s>' % self.name
