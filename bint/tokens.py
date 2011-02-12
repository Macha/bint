class Token:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '<{}: {}>'.format(self.__module__, self.__class__.__name__, repr(self.value))

    def __repr__(self):
        return '{}.{}({})'.format(
                self.__module__,
                self.__class__.__name__,
                repr(self.value)
            )

class IdentifierToken(Token):
    pass


class StringToken(Token):
    pass


class NumberToken(Token):
    pass


class OpToken(Token):
    pass


class EndLineToken(Token):
    def __init__(self):
        self.value = '\n'
