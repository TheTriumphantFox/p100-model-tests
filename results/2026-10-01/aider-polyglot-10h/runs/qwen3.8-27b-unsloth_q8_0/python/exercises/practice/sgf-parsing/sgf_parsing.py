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
    
    if input_string[0] != '(':
        raise ValueError("tree missing")
        
    if input_string.count('(') != input_string.count(')'):
        raise ValueError("tree missing")

    # Remove the outermost parentheses
    inner = input_string[1:-1]
    
    if not inner:
        raise ValueError("tree with no nodes")

    # We expect the first character to be ';'
    if inner[0] != ';':
        raise ValueError("tree with no nodes")

    return _parse_node(inner)


def _parse_node(s):
    # s starts with ';'
    # Parse properties until we hit '(' or end of string
    properties = {}
    i = 1 # skip ';'
    n = len(s)
    
    while i < n:
        if s[i] == '(':
            break
        if s[i] == ';':
            # This shouldn't happen in valid SGF inside a node without a new node start
            # But if it does, it's likely malformed or we are at a sibling which is handled by caller
            # Actually, siblings are handled by the caller loop. Inside a node, we stop at '(' or end.
            # If we see ';' here, it's an error or unexpected structure.
            # However, the structure is (;props (;props) (;props))
            # So inside the first node, we stop at the first '('.
            # If we see ';' before '(', it's invalid.
            raise ValueError("properties without delimiter")
            
        # Parse key
        key_start = i
        while i < n and s[i] != '[':
            i += 1
        if i >= n:
            raise ValueError("properties without delimiter")
        
        key = s[key_start:i]
        if not key:
            raise ValueError("properties without delimiter")
            
        # Check if key is uppercase
        if not key.isupper():
            raise ValueError("property must be in uppercase")
            
        i += 1 # skip '['
        
        # Parse value
        value, i = _parse_value(s, i)
        
        # Store property. If key exists, append to list, else create list.
        if key in properties:
            properties[key].append(value)
        else:
            properties[key] = [value]
            
    # After parsing properties, check for children
    children = []
    if i < n and s[i] == '(':
        # Parse children
        while i < n and s[i] == '(':
            # Find matching closing parenthesis
            depth = 0
            start = i
            i += 1
            while i < n:
                if s[i] == '(':
                    depth += 1
                elif s[i] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            
            if i >= n:
                raise ValueError("tree missing")
                
            # s[start:i+1] is the child node string including parens
            child_str = s[start:i+1]
            # The child string starts with '(' and ends with ')'
            # We need to parse the content inside
            # The content should start with ';'
            if len(child_str) < 3 or child_str[1] != ';':
                 # It might be an empty node? SGF nodes usually have at least one property or are empty?
                 # "tree with no nodes" is for the root.
                 # A child node like () is invalid?
                 # Let's assume valid input has (;...)
                 pass
            
            children.append(_parse_node(child_str[1:-1]))
            i += 1 # skip ')'
            
    return SgfTree(properties, children)


def _parse_value(s, i):
    # s[i] should be the start of the value, after '['
    # We need to find the matching ']'
    # Handle escapes
    value_chars = []
    n = len(s)
    
    while i < n:
        char = s[i]
        if char == '\\':
            i += 1
            if i >= n:
                # Unterminated escape
                break
            next_char = s[i]
            if next_char == '\n':
                # Newline after backslash is removed
                pass
            elif next_char in ' \t\r':
                # Other whitespace after backslash becomes space
                value_chars.append(' ')
            else:
                # Non-whitespace after backslash is inserted as-is
                value_chars.append(next_char)
            i += 1
        elif char == ']':
            # End of value
            i += 1
            break
        else:
            if char in ' \t\r':
                value_chars.append(' ')
            else:
                value_chars.append(char)
            i += 1
            
    if i >= n:
        raise ValueError("properties without delimiter")
        
    return ''.join(value_chars), i
