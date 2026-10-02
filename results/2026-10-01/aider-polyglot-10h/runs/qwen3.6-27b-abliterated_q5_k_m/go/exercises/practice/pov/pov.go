package pov

// Tree represents a node in the tree.
type Tree struct {
	value    string
	children []*Tree
	parent   *Tree
}

// New creates and returns a new Tree with the given root value and children.
func New(value string, children ...*Tree) *Tree {
	tr := &Tree{
		value:    value,
		children: children,
	}
	for _, ch := range children {
		ch.parent = tr
	}
	return tr
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
	// Find the target node
	target := findNode(tr, from)
	if target == nil {
		return nil
	}

	// Reorient the tree
	return reorient(target)
}

// PathTo returns the shortest path between two nodes in the tree.
func (tr *Tree) PathTo(from, to string) []string {
	// Get the tree from the perspective of 'from'
	povTree := tr.FromPov(from)
	if povTree == nil {
		return nil
	}

	// Find the path from 'from' to 'to' in the reoriented tree
	path := findPath(povTree, to)
	return path
}

// findNode searches for a node with the given value in the tree.
func findNode(tr *Tree, value string) *Tree {
	if tr == nil {
		return nil
	}
	if tr.value == value {
		return tr
	}
	for _, ch := range tr.children {
		if found := findNode(ch, value); found != nil {
			return found
		}
	}
	return nil
}

// reorient reorients the tree so that the given node becomes the root.
func reorient(node *Tree) *Tree {
	current := node

	// Walk up to the original root, reorienting as we go
	for current.parent != nil {
		parent := current.parent
		// Remove current from parent's children
		parent.children = removeChild(parent.children, current)
		// Add parent as a child of current
		current.children = append(current.children, parent)
		parent.parent = current
		// Move up
		current = parent
	}

	// The new root is the original node
	// Clear the parent of the new root
	node.parent = nil

	return node
}

// removeChild removes a child from the slice of children.
func removeChild(children []*Tree, child *Tree) []*Tree {
	for i, c := range children {
		if c == child {
			return append(children[:i], children[i+1:]...)
		}
	}
	return children
}

// findPath finds the path from the root of the tree to the node with the given value.
func findPath(tr *Tree, value string) []string {
	if tr == nil {
		return nil
	}
	if tr.value == value {
		return []string{tr.value}
	}
	for _, ch := range tr.children {
		if path := findPath(ch, value); path != nil {
			return append([]string{tr.value}, path...)
		}
	}
	return nil
}
