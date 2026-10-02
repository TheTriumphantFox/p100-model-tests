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
    if not input_string or not input_string.strip():
        raise ValueError("tree missing")

    # Remove outer parentheses if present
    stripped = input_string.strip()
    if stripped.startswith('(') and stripped.endswith(')'):
        stripped = stripped[1:-1].strip()

    if not stripped:
        raise ValueError("tree with no nodes")

    # Parse the tree
    return _parse_node(stripped)

def _parse_node(input_str):
    nodes = []
    i = 0
    n = len(input_str)

    while i < n:
        if input_str[i] == '(':
            # Start of a new node
            i += 1
            node_str = []
            balance = 1

            while i < n and balance > 0:
                if input_str[i] == '(':
                    balance += 1
                elif input_str[i] == ')':
                    balance -= 1
                if balance > 0:
                    node_str.append(input_str[i])
                i += 1

            if balance != 0:
                raise ValueError("tree missing")

            node_str = ''.join(node_str).strip()
            if node_str:
                nodes.append(_parse_properties(node_str))
        else:
            # Parse properties until next '(' or end
            prop_str = []
            while i < n and input_str[i] != '(':
                prop_str.append(input_str[i])
                i += 1

            prop_str = ''.join(prop_str).strip()
            if prop_str:
                nodes.append(_parse_properties(prop_str))

    if not nodes:
        raise ValueError("tree with no nodes")

    # The first node is the main node, others are variations
    main_node = nodes[0]
    main_node.children = nodes[1:]
    return main_node

def _parse_properties(input_str):
    properties = {}
    i = 0
    n = len(input_str)

    while i < n:
        if input_str[i] != ';':
            # Check if this is an empty node (just semicolon)
            if i == n - 1 and input_str[i] == ';':
                return SgfTree(properties)
            raise ValueError("properties without delimiter")

        i += 1
        # Parse key
        key = []
        while i < n and input_str[i] not in ['[', ';']:
            key.append(input_str[i])
            i += 1

        if not key:
            # Empty key after semicolon
            if i < n and input_str[i] == ';':
                continue
            raise ValueError("properties without delimiter")

        key = ''.join(key)
        if not key.isupper():
            raise ValueError("property must be in uppercase")

        # Parse values
        values = []
        while i < n and input_str[i] == '[':
            i += 1
            value = []
            while i < n and input_str[i] != ']':
                if input_str[i] == '\\':
                    i += 1
                    if i < n:
                        # Handle escaped characters
                        if input_str[i] == '\n':
                            # Escaped newline is removed
                            pass
                        elif input_str[i].isspace():
                            # Escaped whitespace becomes space
                            value.append(' ')
                        else:
                            value.append(input_str[i])
                        i += 1
                else:
                    if input_str[i].isspace() and input_str[i] != '\n':
                        # Convert whitespace to space
                        value.append(' ')
                    else:
                        value.append(input_str[i])
                    i += 1

            if i >= n or input_str[i] != ']':
                raise ValueError("properties without delimiter")

            i += 1
            values.append(''.join(value))

        if not values:
            raise ValueError("properties without delimiter")

        if key in properties:
            raise ValueError("duplicate property key")

        properties[key] = values

    return SgfTree(properties)
