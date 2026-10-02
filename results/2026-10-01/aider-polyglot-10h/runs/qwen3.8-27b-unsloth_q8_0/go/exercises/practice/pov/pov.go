package pov

type Tree struct {
	value    string
	children []*Tree
}

// New creates and returns a new Tree with the given root value and children.
func New(value string, children ...*Tree) *Tree {
	return &Tree{
		value:    value,
		children: children,
	}
}

// Value returns the value at the root of a tree.
func (tr *Tree) Value() string {
	return tr.value
}

// Children returns a slice containing the children of a tree.
// There is no need to sort the elements in the result slice,
// they can be in any order.
func (tr *Tree) Children() []*Tree {
	return tr.children
}

// String describes a tree in a compact S-expression format.
// This helps to make test outputs more readable.
// Feel free to adapt this method as you see fit.
func (tr *Tree) String() string {
	if tr == nil {
		return "nil"
	}
	result := tr.Value()
	if len(tr.Children()) == 0 {
		return result
	}
	for _, ch := range tr.Children() {
		result += " " + ch.String()
	}
	return "(" + result + ")"
}

// POV problem-specific functions

// FromPov returns the pov from the node specified in the argument.
func (tr *Tree) FromPov(from string) *Tree {
	if tr == nil {
		return nil
	}

	// Find the path from the current root to the node 'from'
	var path []*Tree
	var findPath func(node *Tree, target string) bool
	findPath = func(node *Tree, target string) bool {
		if node == nil {
			return false
		}
		path = append(path, node)
		if node.value == target {
			return true
		}
		for _, child := range node.children {
			if findPath(child, target) {
				return true
			}
		}
		path = path[:len(path)-1]
		return false
	}

	if !findPath(tr, from) {
		return nil
	}

	// Reconstruct the tree with 'from' as the root
	// The path is [root, ..., parent, from]
	// We build the new tree from the target node upwards.
	
	var build func(i int) *Tree
	build = func(i int) *Tree {
		node := path[i]
		newNode := &Tree{value: node.value}
		
		// Add all original children except the one that is the parent in the path
		for _, child := range node.children {
			if i > 0 && child == path[i-1] {
				continue
			}
			newNode.children = append(newNode.children, child)
		}
		
		// Add the parent in the path as a child, but re-rooted
		if i > 0 {
			newNode.children = append(newNode.children, build(i-1))
		}
		
		return newNode
	}
	
	return build(len(path) - 1)
}

// PathTo returns the shortest path between two nodes in the tree.
func (tr *Tree) PathTo(from, to string) []string {
	if tr == nil {
		return nil
	}
	
	// Re-root the tree at 'from'
	povTree := tr.FromPov(from)
	if povTree == nil {
		return nil
	}
	
	// Now find the path from 'from' (which is the root of povTree) to 'to'
	var path []string
	var findPath func(node *Tree, target string) bool
	findPath = func(node *Tree, target string) bool {
		if node == nil {
			return false
		}
		path = append(path, node.value)
		if node.value == target {
			return true
		}
		for _, child := range node.children {
			if findPath(child, target) {
				return true
			}
		}
		path = path[:len(path)-1]
		return false
	}
	
	if !findPath(povTree, to) {
		return nil
	}
	
	return path
}
