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

// Helper function to find a node with a given value in the tree
func findNode(root *Tree, target string) *Tree {
	if root == nil {
		return nil
	}
	if root.Value() == target {
		return root
	}
	for _, child := range root.Children() {
		found := findNode(child, target)
		if found != nil {
			return found
		}
	}
	return nil
}

// Helper function to find the parent of a node
func findParent(root *Tree, target *Tree) *Tree {
	if root == nil || target == nil {
		return nil
	}
	for _, child := range root.Children() {
		if child == target {
			return root
		}
		found := findParent(child, target)
		if found != nil {
			return found
		}
	}
	return nil
}

// FromPov returns the pov from the node specified in the argument.
func (tr *Tree) FromPov(from string) *Tree {
	// Find the node with the given value
	node := findNode(tr, from)
	if node == nil {
		return nil
	}

	// Find the parent of the node
	parent := findParent(tr, node)
	if parent == nil {
		// If no parent found, just return a copy of the tree
		return buildTree(node)
	}

	// Create new children list for the new root
	// First add all siblings of the new root
	newChildren := []*Tree{}
	for _, child := range parent.Children() {
		if child != node {
			newChildren = append(newChildren, buildTree(child))
		}
	}

	// Then add the parent (with its other children)
	newChildren = append(newChildren, buildTree(parent))

	// Create the new tree with the node as root
	return New(node.Value(), newChildren...)
}

// Helper function to build a new tree with the given root and its descendants
func buildTree(root *Tree) *Tree {
	if root == nil {
		return nil
	}
	children := []*Tree{}
	for _, child := range root.Children() {
		children = append(children, buildTree(child))
	}
	return New(root.Value(), children...)
}

// Helper function to find the path from a node to its ancestor
func findPathToAncestor(node *Tree, ancestor *Tree, path []string) []string {
	if node == nil || ancestor == nil {
		return nil
	}
	if node.Value() == ancestor.Value() {
		return path
	}
	// Search in children
	for _, child := range node.Children() {
		foundPath := findPathToAncestor(child, ancestor, append(path, child.Value()))
		if foundPath != nil {
			return foundPath
		}
	}
	return nil
}

// PathTo returns the shortest path between two nodes in the tree.
func (tr *Tree) PathTo(from, to string) []string {
	// Find both nodes
	fromNode := findNode(tr, from)
	toNode := findNode(tr, to)
	if fromNode == nil || toNode == nil {
		return nil
	}

	// If they're the same node, return empty path
	if fromNode.Value() == toNode.Value() {
		return []string{}
	}

	// Reparent the tree on the 'from' node to make path finding easier
	povTree := tr.FromPov(from)

	// Now find the path from root (which is 'from') to 'to'
	path := findPathToAncestor(povTree, toNode, []string{from})
	if path == nil {
		return nil
	}

	// The path includes the 'from' node at the beginning, which we don't need
	return path[1:]
}
