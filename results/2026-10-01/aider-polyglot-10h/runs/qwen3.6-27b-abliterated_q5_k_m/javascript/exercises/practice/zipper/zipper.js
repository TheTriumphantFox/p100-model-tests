//
// This is only a SKELETON file for the 'Zipper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Zipper {
  constructor(focus, path = []) {
    this.focus = focus;
    this.path = path;
  }

  static fromTree(tree) {
    return new Zipper(tree, []);
  }

  toTree() {
    let z = this;
    while (z.path.length > 0) {
      z = z.up();
    }
    return z.focus;
  }

  value() {
    return this.focus.value;
  }

  left() {
    if (!this.focus || !this.focus.left) {
      return null;
    }
    return new Zipper(this.focus.left, [{ direction: 'left', parent: this.focus }, ...this.path]);
  }

  right() {
    if (!this.focus || !this.focus.right) {
      return null;
    }
    return new Zipper(this.focus.right, [{ direction: 'right', parent: this.focus }, ...this.path]);
  }

  up() {
    if (this.path.length === 0) {
      return null;
    }
    
    const [breadcrumb, ...restPath] = this.path;
    const { direction, parent } = breadcrumb;
    
    // Create a new parent node with the updated child
    const newParent = {
      ...parent,
      [direction]: this.focus
    };
    
    return new Zipper(newParent, restPath);
  }

  setValue(value) {
    const newFocus = {
      ...this.focus,
      value
    };
    return new Zipper(newFocus, this.path);
  }

  setLeft(tree) {
    const newFocus = {
      ...this.focus,
      left: tree
    };
    return new Zipper(newFocus, this.path);
  }

  setRight(tree) {
    const newFocus = {
      ...this.focus,
      right: tree
    };
    return new Zipper(newFocus, this.path);
  }
}
