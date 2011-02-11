from bint import tokens

class EndOfTokenisation(Exception): pass

class BintLexer:
    operator_chars = ['m', 'o', 'd', '+', '-', '*',
            '\\', '<', '>', '=', ',', '(', ')']
       
    def tokenise(self, text):
        """Tokenises the passed in string. """
        self.text = text
        self.char = 0
        try:
            self.current_char = text[0]
        except IndexError:
            return [] # Empty string
        
        try:
            self.next_char = text[1]
        except IndexError:
            self.next_char = ''

        parsed_tokens = []
        
        while True:
            if self.char >= len(self.text):
                break # All done

            try:
                if self.current_char == '"':
                    parsed_tokens.append(self.read_string())
                elif self.current_char.isdigit():
                    parsed_tokens.append(self.read_number())
                elif self.current_char.isalpha():
                    
                    if text[self.char:].startswith('mod'):
                        parsed_tokens.append(self.read_op())
                    else:
                        parsed_tokens.append(self.read_identifier())
                            
                elif self.current_char in self.operator_chars:
                    parsed_tokens.append(self.read_op())
                elif self.current_char == '\n':
                    parsed_tokens.append(tokens.EndLineToken())
                    self.get_next_char()
                elif self.current_char.isspace():
                    self.get_next_char()
            
            except EndOfTokenisation:
                break
        
        return parsed_tokens


    def read_op(self):
        """ Reads an operator from the text to tokenise. """
        op_string = ''

        while self.current_char in self.operator_chars:
            op_string += self.current_char
            try:
                self.get_next_char()
            except EndOfTokenisation:
                return tokens.OpToken(op_string)

        return tokens.OpToken(op_string)


    def read_number(self):
        """ Gets a token of a number in the text. """
        num = 0
       
        while self.current_char.isdigit():
            num *= 10
            num += int(self.current_char)


            try:
                self.get_next_char()
            except EndOfTokenisation:
                return tokens.NumberToken(num)
                
        return tokens.NumberToken(num)


    def read_string(self):
        """ Reads in a string token. """
        self.get_next_char() # Drop opening quote.
        chars = ''
        num_quotes = 0

        while True:
            if self.current_char != '"':
                chars += self.current_char
            elif num_quotes == 1:
                chars += '"'
                num_quotes = 0
            elif num_quotes == 0 and self.next_char == '"':
                num_quotes += 1
            else:
                try:
                    self.get_next_char() # Drop ending quote
                except EndOfTokenisation:
                    return tokens.StringToken(chars)
                break

            try:
                self.get_next_char()
            except EndOfTokenisation:
                return tokens.StringToken(chars)

        return tokens.StringToken(chars)


    def read_identifier(self):
        """ Reads in a identifier token. """
        chars = ''
        
        while self.is_identifier_char(self.current_char):    
            chars += self.current_char
            try:
                self.get_next_char()
            except EndOfTokenisation:
                return tokens.IdentifierToken(chars)

        return tokens.IdentifierToken(chars)


    def is_identifier_char(self, char):
        """ Checks if the current character is an identifier character.

        Valid identifier characters are [0-9A-Za-z_]
        """
        return (char.isalpha() or char.isdigit() or char == '_')


    def get_next_char(self):
        """ Updates the current character to the next character.

        Throws IndexError if no more characters are available.
        """
        self.char += 1

        print('Parsing char #{}'.format(self.char))
        
        try:
            self.current_char = self.text[self.char]
        except IndexError:
            raise EndOfTokenisation() 
        
        try:
            self.next_char = self.text[self.char + 1]
        except IndexError:
            self.next_char = ''
