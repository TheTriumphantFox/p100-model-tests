class SgfTree:
    def __init__(self, properties=None, children=None):
        self.properties = properties or {}
        self.children = children or []

    def __eq__(self, other):
        if not isinstance(other, SgfTree):
            return False
        for key, value in self.properties.items():
            if key not in other.properties:
                return False
            if other.properties[key] != value:
                return False
        for key in other.properties.keys():
            if key not in self.properties:
                return False
        if len(self.children) != len(other.children):
            return False
        for child, other_child in zip(self.children, other.children):
            if child != other_child:
                return False
        return True

    def __ne__(self, other):
        return not self == other


def parse(input_string):
    if not input_string:
        raise ValueError("tree missing")

    parser = SgfParser(input_string)
    tree = parser.parse_tree()
    
    if parser.pos < len(input_string):
        raise ValueError("tree missing")
        
    return tree


class SgfParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def parse_tree(self):
        if self.pos >= len(self.text) or self.text[self.pos] != '(':
            raise ValueError("tree missing")
        
        self.pos += 1  # consume '('
        
        if self.pos >= len(self.text) or self.text[self.pos] != ';':
            raise ValueError("tree with no nodes")
            
        root = self.parse_node()
        children = self.parse_children()
        
        if self.pos >= len(self.text) or self.text[self.pos] != ')':
            raise ValueError("tree missing")
        self.pos += 1  # consume ')'
        
        root.children = children
        return root

    def parse_children(self):
        children = []
        while self.pos < len(self.text) and self.text[self.pos] == ';':
            child = self.parse_node()
            child_children = self.parse_children()
            child.children = child_children
            children.append(child)
            
        # Check for variations (branches)
        while self.pos < len(self.text) and self.text[self.pos] == '(':
            variation = self.parse_tree()
            children.append(variation)
            
        return children

    def parse_node(self):
        # Expect ';'
        if self.pos >= len(self.text) or self.text[self.pos] != ';':
            raise ValueError("tree with no nodes")
        self.pos += 1  # consume ';'
        
        properties = self.parse_properties()
        return SgfTree(properties=properties)

    def parse_properties(self):
        properties = {}
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char == ';' or char == ')' or char == '(':
                break
                
            if not char.isalpha():
                raise ValueError("properties without delimiter")
                
            # Parse key
            key_start = self.pos
            while self.pos < len(self.text) and self.text[self.pos].isalpha():
                self.pos += 1
            key = self.text[key_start:self.pos]
            
            if not key.isupper():
                raise ValueError("property must be in uppercase")
                
            # Parse values for this key
            values = []
            while self.pos < len(self.text) and self.text[self.pos] == '[':
                values.append(self.parse_value())
                
            if not values:
                raise ValueError("properties without delimiter")
                
            properties[key] = tuple(values)
            
        return properties

    def parse_value(self):
        if self.pos >= len(self.text) or self.text[self.pos] != '[':
            raise ValueError("properties without delimiter")
        self.pos += 1  # consume '['
        
        value_chars = []
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char == ']':
                self.pos += 1  # consume ']'
                return self.process_value_string(''.join(value_chars))
            elif char == '\\':
                self.pos += 1
                if self.pos < len(self.text):
                    next_char = self.text[self.pos]
                    if next_char == '\n':
                        # Newline immediately after backslash is removed
                        self.pos += 1
                    else:
                        value_chars.append(next_char)
                        self.pos += 1
                else:
                    # Backslash at end of string (before ])
                    value_chars.append('\\')
            elif char == '\n':
                value_chars.append('\n')
                self.pos += 1
            elif char in '\t\r':
                # Other whitespace converted to space
                value_chars.append(' ')
                self.pos += 1
            else:
                value_chars.append(char)
                self.pos += 1
                
        raise ValueError("properties without delimiter")

    def process_value_string(self, s):
        # The parsing logic above handles most of the SGF text type rules:
        # - Newlines are removed if they come immediately after a \
        # - All whitespace characters other than newline are converted to spaces.
        # - \ is the escape character.
        #   Any non-whitespace character after \ is inserted as-is.
        #   Any whitespace character after \ follows the above rules.
        
        # However, the loop in parse_value handles:
        # 1. \ followed by \n -> removed (handled in loop)
        # 2. \ followed by other -> inserted as-is (handled in loop)
        # 3. \n -> kept as \n (handled in loop)
        # 4. \t, \r -> converted to space (handled in loop)
        
        # Let's double check if any post-processing is needed.
        # The instructions say:
        # "Newlines are removed if they come immediately after a \, otherwise they remain as newlines."
        # "All whitespace characters other than newline are converted to spaces."
        # "\ is the escape character. Any non-whitespace character after \ is inserted as-is."
        
        # My parse_value logic:
        # if char == '\\':
        #    self.pos += 1
        #    if self.pos < len(self.text):
        #        next_char = self.text[self.pos]
        #        if next_char == '\n':
        #            self.pos += 1 # removed
        #        else:
        #            value_chars.append(next_char) # inserted as-is
        #            self.pos += 1
        # elif char == '\n':
        #    value_chars.append('\n') # remains
        # elif char in '\t\r':
        #    value_chars.append(' ') # converted to space
            
        # This seems correct.
        return s
