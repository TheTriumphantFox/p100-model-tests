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
    
    if input_string[0] != '(' or input_string[-1] != ')':
        raise ValueError("tree missing")
    
    # Remove the outer parentheses
    content = input_string[1:-1]
    
    if not content:
        raise ValueError("tree missing")
        
    parser = SGFParser(content)
    tree = parser.parse_tree()
    
    if parser.pos != len(parser.input):
        raise ValueError("tree missing")
        
    return tree


class SGFParser:
    def __init__(self, input_string):
        self.input = input_string
        self.pos = 0

    def parse_tree(self):
        # A tree starts with a node sequence (;)
        # It can have multiple nodes in sequence, and each node can have children ()
        
        if not self.input or self.pos >= len(self.input):
            raise ValueError("tree missing")
            
        # Check if there's at least one node
        if self.pos >= len(self.input) or self.input[self.pos] != ';':
            raise ValueError("tree missing")
            
        nodes = []
        
        # Parse first node
        nodes.append(self.parse_node())
        
        # Parse subsequent nodes in the sequence
        while self.pos < len(self.input) and self.input[self.pos] == ';':
            nodes.append(self.parse_node())
            
        if len(nodes) == 0:
            raise ValueError("tree with no nodes")
            
        # The first node is the root of this tree part
        root_node = nodes[0]
        
        # Parse children variations
        children = []
        while self.pos < len(self.input) and self.input[self.pos] == '(':
            child_content = self.extract_parenthesized_content()
            child_parser = SGFParser(child_content)
            children.append(child_parser.parse_tree())
            
        return SgfTree(root_node['properties'], children)

    def extract_parenthesized_content(self):
        if self.input[self.pos] != '(':
            raise ValueError("tree missing")
        
        depth = 0
        start = self.pos
        while self.pos < len(self.input):
            if self.input[self.pos] == '(':
                depth += 1
            elif self.input[self.pos] == ')':
                depth -= 1
                if depth == 0:
                    return self.input[start+1:self.pos]
            self.pos += 1
        raise ValueError("tree missing")

    def parse_node(self):
        if self.pos >= len(self.input) or self.input[self.pos] != ';':
            raise ValueError("tree missing")
            
        self.pos += 1 # Skip ';'
        
        properties = {}
        
        while self.pos < len(self.input) and self.input[self.pos] != ';' and self.input[self.pos] != ')':
            key, value = self.parse_property()
            
            # Check if key is already present
            if key in properties:
                properties[key].append(value)
            else:
                properties[key] = [value]
                
        return {'properties': properties}

    def parse_property(self):
        # Parse key
        if self.pos >= len(self.input):
            raise ValueError("property must be in uppercase")
            
        key_start = self.pos
        while self.pos < len(self.input) and self.input[self.pos].isupper():
            self.pos += 1
            
        if self.pos == key_start:
            raise ValueError("property must be in uppercase")
            
        key = self.input[key_start:self.pos]
        
        # Check if key is all uppercase (already ensured by loop, but good to be explicit if mixed case was possible)
        if not key.isupper():
            raise ValueError("property must be in uppercase")
            
        # Expect '['
        if self.pos >= len(self.input) or self.input[self.pos] != '[':
            raise ValueError("properties without delimiter")
            
        values = []
        while self.pos < len(self.input) and self.input[self.pos] == '[':
            self.pos += 1 # Skip '['
            value = self.parse_value()
            values.append(value)
            
        if not values:
            raise ValueError("properties without delimiter")
            
        return key, values[0] if len(values) == 1 else values

    def parse_value(self):
        value_chars = []
        while self.pos < len(self.input) and self.input[self.pos] != ']':
            char = self.input[self.pos]
            if char == '\\':
                self.pos += 1
                if self.pos >= len(self.input):
                    raise ValueError("properties without delimiter")
                next_char = self.input[self.pos]
                if next_char == '\n':
                    # Newline after backslash is removed
                    pass
                else:
                    # Any other char after backslash is inserted as-is
                    # Note: whitespace rules apply if it was a whitespace char, 
                    # but the instruction says "Any non-whitespace character after \ is inserted as-is."
                    # And "Any whitespace character after \ follows the above rules."
                    # The "above rules" for whitespace are: converted to space.
                    # So if next_char is whitespace (but not newline), it becomes space.
                    if next_char.isspace():
                        value_chars.append(' ')
                    else:
                        value_chars.append(next_char)
            else:
                if char.isspace():
                    if char == '\n':
                        value_chars.append(char)
                    else:
                        value_chars.append(' ')
                else:
                    value_chars.append(char)
            self.pos += 1
            
        if self.pos >= len(self.input):
            raise ValueError("properties without delimiter")
            
        self.pos += 1 # Skip ']'
        
        return "".join(value_chars)
