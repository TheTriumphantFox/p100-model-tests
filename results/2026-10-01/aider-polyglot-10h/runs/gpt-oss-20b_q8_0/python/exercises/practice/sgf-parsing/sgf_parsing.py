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


def _consume_whitespace(s, i):
    # SGF input has no optional whitespace, but this helper is kept for clarity
    return i


def _parse_value(s, i):
    """Parse a single SGF text value starting at s[i] which should be '['."""
    if i >= len(s) or s[i] != '[':
        raise ValueError("value missing opening '['")
    i += 1
    value_chars = []
    while i < len(s):
        ch = s[i]
        if ch == ']':
            i += 1
            break
        if ch == '\\':
            i += 1
            if i >= len(s):
                raise ValueError("escape character at end of input")
            esc = s[i]
            # Escape handling:
            if esc == '\n':
                # Escaped newline is removed
                pass
            elif esc == '\t':
                value_chars.append(' ')
            else:
                value_chars.append(esc)
            i += 1
        else:
            # Convert whitespace other than newline to space
            if ch == '\t':
                value_chars.append(' ')
            else:
                value_chars.append(ch)
            i += 1
    else:
        raise ValueError("value missing closing ']'")
    return ''.join(value_chars), i


def _parse_property(s, i):
    """Parse a property key (uppercase letters) and its values."""
    start = i
    while i < len(s) and s[i].isalpha():
        i += 1
    if start == i:
        raise ValueError("property key missing")
    key = s[start:i]
    if not key.isupper():
        raise ValueError("property must be in uppercase")
    if i >= len(s) or s[i] != '[':
        raise ValueError("properties without delimiter")
    values = []
    while i < len(s) and s[i] == '[':
        val, i = _parse_value(s, i)
        values.append(val)
    if not values:
        raise ValueError("property without value")
    return key, values, i


def _parse_node(s, i):
    """Parse a node starting at ';'."""
    if i >= len(s) or s[i] != ';':
        raise ValueError("node missing opening ';'")
    i += 1
    properties = {}
    while i < len(s) and s[i] not in (';', ')'):
        key, vals, i = _parse_property(s, i)
        properties[key] = vals
    return properties, i


def _parse_tree(s, i):
    """Recursively parse a tree starting at '('."""
    if i >= len(s) or s[i] != '(':
        raise ValueError("tree missing")
    i += 1
    # Parse root node
    if i >= len(s) or s[i] != ';':
        raise ValueError("tree with no nodes")
    root_props, i = _parse_node(s, i)
    children = []
    # After root node, parse any number of sibling nodes or subtrees
    while i < len(s) and s[i] in (';', '('):
        if s[i] == ';':
            child_props, i = _parse_node(s, i)
            children.append(SgfTree(child_props))
        else:  # '('
            child_tree, i = _parse_tree(s, i)
            children.append(child_tree)
    if i >= len(s) or s[i] != ')':
        raise ValueError("tree missing closing ')'")
    i += 1
    return SgfTree(root_props, children), i


def parse(input_string):
    """Parse an SGF string and return an SgfTree."""
    if not input_string:
        raise ValueError("tree missing")
    i = 0
    tree, i = _parse_tree(input_string, i)
    i = _consume_whitespace(input_string, i)
    if i != len(input_string):
        raise ValueError("unexpected trailing characters")
    return tree
