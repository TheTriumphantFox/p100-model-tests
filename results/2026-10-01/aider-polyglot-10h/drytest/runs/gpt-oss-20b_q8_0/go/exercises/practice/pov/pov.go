package pov

// Tree represents a node in a tree. Each node has a value and a slice of
// child nodes. The tree is rooted; the root node has no parent.
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
	if tr == nil {
		return ""
	}
	return tr.value
}

// Children returns a slice containing the children of a tree.
// There is no need to sort the elements in the result slice,
// they can be in any order.
func (tr *Tree) Children() []*Tree {
	if tr == nil {
		return nil
	}
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
	// Find the path from the original root to the target node.
	path := findPath(tr, from)
	if path == nil {
		// Node not found; return the original tree.
		return tr
	}
	// Build a new tree rooted at the target node.
	// The path slice contains nodes from root to target inclusive.
	// We rebuild by iterating from target up to root, attaching
	// the previously built subtree as a child of the current node.
	var newRoot *Tree
	// Start with the target node as the current subtree.
	newRoot = &Tree{
		value:    path[len(path)-1].value,
		children: []*Tree{},
	}
	// Iterate backwards through the path (excluding the target itself).
	for i := len(path) - 2; i >= 0; i-- {
		parent := path[i]
		// Clone the parent node.
		newParent := &Tree{
			value:    parent.value,
			children: []*Tree{},
		}
		// Attach the current subtree as a child of the new parent.
		newParent.children = append(newParent.children, newRoot)
		// The other children of the original parent (excluding the child
		// that leads to the current subtree) are appended as is.
		for _, ch := range parent.children {
			if ch == path[i+1] {
				continue
			}
			newParent.children = append(newParent.children, ch)
		}
		newRoot = newParent
	}
	return newRoot
}

// PathTo returns the shortest path between two nodes in the tree.
func (tr *Tree) PathTo(from, to string) []string {
	if tr == nil {
		return nil
	}
	// Find paths from the root to each target node.
	pathFrom := findPath(tr, from)
	pathTo := findPath(tr, to)
	if pathFrom == nil || pathTo == nil {
		return nil
	}
	// Find the lowest common ancestor (LCA) index.
	lcaIndex := 0
	for i := 0; i < len(pathFrom) && i < len(pathTo); i++ {
		if pathFrom[i] != pathTo[i] {
			break
		}
		lcaIndex = i
	}
	// Build the path from `from` to `to`.
	var result []string
	// From `from` up to LCA (inclusive).
	for i := len(pathFrom) - 1; i >= lcaIndex; i-- {
		result = append(result, pathFrom[i].Value())
	}
	// From LCA down to `to` (excluding LCA to avoid duplicate).
	for i := lcaIndex + 1; i < len(pathTo); i++ {
		result = append(result, pathTo[i].Value())
	}
	return result
}

// ---------- Helper functions ----------

// findPath returns a slice of *Tree nodes from the root to the node with
// the specified value. If the node is not found, it returns nil.
func findPath(tr *Tree, target string) []*Tree {
	if tr == nil {
		return nil
	}
	if tr.value == target {
		return []*Tree{tr}
	}
	for _, ch := range tr.children {
		if sub := findPath(ch, target); sub != nil {
			return append([]*Tree{tr}, sub...)
		}
	}
	return nil
}
