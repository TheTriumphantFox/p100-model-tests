package pov

import (
	"errors"
)

type Tree struct {
	value  string
	children []*Tree
}

// New creates and returns a new Tree with the given root value and children.
func New(value string, children ...*Tree) *Tree {
	return &Tree{
		value:  value,
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
	// Find the path from the root to the target node 'from'
	path := tr.findPath(tr, from)
	if path == nil {
		return nil
	}

	// The path includes the root and the target node.
	// We need to reverse the edges along this path.
	// path[0] is root, path[len-1] is 'from'
	
	// Create a copy of the tree structure to avoid modifying the original
	// We will rebuild the tree based on the new parent-child relationships.
	
	// Helper to deep copy a subtree
	var deepCopy func(t *Tree) *Tree
	deepCopy = func(t *Tree) *Tree {
		if t == nil {
			return nil
		}
		var newChildren []*Tree
		for _, c := range t.children {
			newChildren = append(newChildren, deepCopy(c))
		}
		return &Tree{
			value:  t.value,
			children: newChildren,
		}
	}
	
	// First, deep copy the entire tree
	rootCopy := deepCopy(tr)
	
	// Now we need to re-parent nodes along the path.
	// The path is from Root -> ... -> Parent -> FromNode
	// We want FromNode to become Root.
	// Parent of FromNode becomes child of FromNode.
	// Parent of Parent becomes child of Parent (but not FromNode side).
	
	// Let's work with the copied tree.
	// We identify nodes along the path in the copied tree.
	// Since values are unique, we can find them by value.
	
	pathNodes := make([]*Tree, len(path))
	for i, val := range path {
		node := findNode(rootCopy, val)
		if node == nil {
			return nil // Should not happen if path was found
		}
		pathNodes[i] = node
	}
	
	// pathNodes[0] is the original root
	// pathNodes[len-1] is the new root
	
	// For each node in the path except the last one (new root),
	// its parent in the original tree becomes its child in the new tree.
	// The node itself becomes the parent of its original parent.
	
	// Iterate from the new root upwards to the original root
	// pathNodes[i] is child of pathNodes[i-1] in original tree
	// In new tree, pathNodes[i] is parent of pathNodes[i-1]
	
	for i := len(pathNodes) - 1; i > 0; i-- {
		child := pathNodes[i]
		parent := pathNodes[i-1]
		
		// Remove parent from child's children
		var newChildren []*Tree
		for _, c := range child.children {
			if c != parent {
				newChildren = append(newChildren, c)
			}
		}
		child.children = newChildren
		
		// Add child to parent's children
		parent.children = append(parent.children, child)
	}
	
	return rootCopy
}

// findNode finds a node with the given value in the tree.
func findNode(root *Tree, value string) *Tree {
	if root == nil {
		return nil
	}
	if root.value == value {
		return root
	}
	for _, c := range root.children {
		node := findNode(c, value)
		if node != nil {
			return node
		}
	}
	return nil
}

// findPath finds the path from root to the target value.
// Returns nil if not found.
func (tr *Tree) findPath(root *Tree, target string) []string {
	if root == nil {
		return nil
	}
	if root.value == target {
		return []string{root.value}
	}
	
	for _, c := range root.children {
		path := c.findPath(c, target)
		if path != nil {
			return append([]string{root.value}, path...)
		}
	}
	return nil
}

// PathTo returns the shortest path between two nodes in the tree.
func (tr *Tree) PathTo(from, to string) []string {
	// Find path from root to 'from'
	pathFromRootToFrom := tr.findPath(tr, from)
	if pathFromRootToFrom == nil {
		return nil
	}
	
	// Find path from root to 'to'
	pathFromRootToTo := tr.findPath(tr, to)
	if pathFromRootToTo == nil {
		return nil
	}
	
	// Find the lowest common ancestor (LCA)
	// The paths are from root to node.
	// We compare them from the start until they diverge.
	lcaIndex := 0
	for i := 0; i < len(pathFromRootToFrom) && i < len(pathFromRootToTo); i++ {
		if pathFromRootToFrom[i] == pathFromRootToTo[i] {
			lcaIndex = i
		} else {
			break
		}
	}
	
	// Path from 'from' to LCA is reverse of pathFromRootToFrom[0...lcaIndex]
	// Path from LCA to 'to' is pathFromRootToTo[lcaIndex...end]
	
	path := make([]string, 0)
	
	// Add path from 'from' up to LCA (exclusive of LCA)
	for i := len(pathFromRootToFrom) - 1; i > lcaIndex; i-- {
		path = append(path, pathFromRootToFrom[i])
	}
	
	// Add LCA
	path = append(path, pathFromRootToFrom[lcaIndex])
	
	// Add path from LCA to 'to' (exclusive of LCA)
	for i := lcaIndex + 1; i < len(pathFromRootToTo); i++ {
		path = append(path, pathFromRootToTo[i])
	}
	
	return path
}
