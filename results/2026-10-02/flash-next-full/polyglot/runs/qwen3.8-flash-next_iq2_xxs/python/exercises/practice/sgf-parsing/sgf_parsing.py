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
    
    if not input_string.startswith('(') or not input_string.endswith(')'):
        raise ValueError("tree missing")
        
    content = input_string[1:-1]
    
    if not content:
        raise ValueError("tree with no nodes")
        
    if not content.startswith(';'):
        raise ValueError("tree missing")

    def parse_node_properties(sgf_str, index):
        properties = {}
        i = index
        while i < len(sgf_str):
            char = sgf_str[i]
            if char == ';':
                break
            elif char == '(':
                break
            elif char == ')':
                break
            elif char.isalpha():
                if not char.isupper():
                    raise ValueError("property must be in uppercase")
                key = char
                i += 1
                while i < len(sgf_str) and sgf_str[i].isalpha():
                    if not sgf_str[i].isupper():
                        raise ValueError("property must be in uppercase")
                    key += sgf_str[i]
                    i += 1
                
                if i >= len(sgf_str) or sgf_str[i] != '[':
                    raise ValueError("properties without delimiter")
                
                values = []
                while i < len(sgf_str) and sgf_str[i] == '[':
                    i += 1
                    value = ""
                    while i < len(sgf_str):
                        if sgf_str[i] == ']':
                            i += 1
                            break
                        elif sgf_str[i] == '\\':
                            if i + 1 < len(sgf_str):
                                next_char = sgf_str[i+1]
                                if next_char == '\n':
                                    i += 2
                                    continue
                                elif next_char.isspace():
                                    value += ' '
                                    i += 2
                                    continue
                                else:
                                    value += next_char
                                    i += 2
                                    continue
                            else:
                                value += '\\'
                                i += 1
                        elif sgf_str[i] == '\n':
                            value += '\n'
                            i += 1
                        elif sgf_str[i].isspace():
                            value += ' '
                            i += 1
                        else:
                            value += sgf_str[i]
                            i += 1
                    values.append(value)
                
                properties[key] = values
            else:
                raise ValueError("properties without delimiter")
                
        return properties, i

    def parse_node(sgf_str, index):
        if index >= len(sgf_str) or sgf_str[index] != ';':
            raise ValueError("tree missing")
            
        properties, next_index = parse_node_properties(sgf_str, index + 1)
        
        children = []
        i = next_index
        
        while i < len(sgf_str) and sgf_str[i] == '(':
            child_tree, i = parse_tree(sgf_str, i)
            children.append(child_tree)
            
        return SgfTree(properties, children), i

    def parse_tree(sgf_str, index):
        if index >= len(sgf_str) or sgf_str[index] != '(':
            raise ValueError("tree missing")
            
        i = index + 1
        
        if i >= len(sgf_str) or sgf_str[i] != ';':
            raise ValueError("tree with no nodes")
            
        root_node, i = parse_node(sgf_str, i)
        
        if i >= len(sgf_str) or sgf_str[i] != ')':
            raise ValueError("tree missing")
            
        i += 1
        
        return root_node, i

    root_tree, _ = parse_tree(content, 0)
    return root_tree
