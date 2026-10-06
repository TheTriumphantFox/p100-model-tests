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
	if tr.value == from {
		return tr
	}
	for _, child := range tr.children {
		if res := child.FromPov(from); res != nil {
			// Create a new node for the current root, with the found subtree as its child
			newChildren := make([]*Tree, 0, len(tr.children))
			for _, c := range tr.children {
				if c == child {
					continue
				}
				newChildren = append(newChildren, c)
			}
			newChildren = append(newChildren, &Tree{value: tr.value, children: []*Tree{res}})
			return &Tree{value: from, children: []*Tree{&Tree{value: tr.value, children: newChildren}}}
		}
	}
	return nil
}

// PathTo returns the shortest path between two nodes in the tree.
func (tr *Tree) PathTo(from, to string) []string {
	if tr == nil {
		return nil
	}
	pathFrom := tr.pathTo(from)
	pathTo := tr.pathTo(to)
	if pathFrom == nil || pathTo == nil {
		return nil
	}
	// Find common ancestor
	i := 0
	for i < len(pathFrom) && i < len(pathTo) && pathFrom[i] == pathTo[i] {
		i++
	}
	// pathFrom[i:] contains the path from common ancestor to from (excluding ancestor)
	// pathTo[i:] contains the path from common ancestor to to (excluding ancestor)
	// We want path from -> ... -> common ancestor -> ... -> to
	// Reverse pathFrom[i:] to get path from common ancestor to from
	var result []string
	for j := len(pathFrom) - 1; j >= i; j-- {
		result = append(result, pathFrom[j])
	}
	for j := i; j < len(pathTo); j++ {
		result = append(result, pathTo[j])
	}
	return result
}

// pathTo returns the path from the root to the node with the given value.
func (tr *Tree) pathTo(value string) []string {
	if tr == nil {
		return nil
	}
	if tr.value == value {
		return []string{tr.value}
	}
	for _, child := range tr.children {
		if res := child.pathTo(value); res != nil {
			return append([]string{tr.value}, res...)
		}
	}
	return nil
}
