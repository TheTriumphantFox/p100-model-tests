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
	// Find the target node and its parent chain up to the root.
	target, _ := findNodeAndParent(tr, from, nil)
	if target == nil {
		// Node not found; return the original tree.
		return tr
	}
	// Build a new tree rooted at target by walking up to the root.
	return buildReRooted(target)
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

// findNodeAndParent searches for a node with the given value and returns
// the node and its parent. If the node is not found, it returns (nil, nil).
func findNodeAndParent(tr *Tree, target string, parent *Tree) (*Tree, *Tree) {
	if tr == nil {
		return nil, nil
	}
	if tr.value == target {
		return tr, parent
	}
	for _, ch := range tr.children {
		if node, p := findNodeAndParent(ch, target, tr); node != nil {
			return node, p
		}
	}
	return nil, nil
}

// buildReRooted constructs a new tree rooted at `root` by walking up to the
// original root and reattaching ancestors as parents. This avoids creating
// cycles and does not modify the original tree.
func buildReRooted(root *Tree) *Tree {
	if root == nil {
		return nil
	}
	// Collect the chain from root up to the original root.
	chain := []*Tree{root}
	cur := root
	for {
		// Find parent of cur in the original tree.
		_, parent := findNodeAndParent(cur, cur.value, nil)
		if parent == nil {
			break
		}
		chain = append(chain, parent)
		cur = parent
	}
	// Now rebuild the tree from the bottom of the chain.
	var newTree *Tree
	for i := len(chain) - 1; i >= 0; i-- {
		node := chain[i]
		if newTree == nil {
			// First node becomes the new root.
			newTree = &Tree{value: node.value}
		} else {
			// Attach the previously built subtree as a child.
			newTree = &Tree{
				value:    node.value,
				children: []*Tree{newTree},
			}
		}
	}
	return newTree
}

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
