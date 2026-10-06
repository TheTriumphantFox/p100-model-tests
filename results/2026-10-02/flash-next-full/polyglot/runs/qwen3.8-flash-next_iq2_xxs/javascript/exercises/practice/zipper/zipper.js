//
// This is only a SKELETON file for the 'Zipper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

class Node {
  constructor(value, left, right) {
    this.value = value;
    this.left = left;
    this.right = right;
  }
}

export class Zipper {
  constructor(focus, breadcrumbs) {
    this.focus = focus;
    this.breadcrumbs = breadcrumbs || [];
  }

  static fromTree(tree) {
    return new Zipper(tree, []);
  }

  toTree() {
    let tree = this.focus;
    for (let i = this.breadcrumbs.length - 1; i >= 0; i--) {
      const breadcrumb = this.breadcrumbs[i];
      if (breadcrumb.side === 'left') {
        tree = new Node(breadcrumb.value, tree, breadcrumb.right);
      } else {
        tree = new Node(breadcrumb.value, breadcrumb.left, tree);
      }
    }
    return tree;
  }

  value() {
    return this.focus.value;
  }

  left() {
    if (this.focus.left === null) {
      return null;
    }
    const newFocus = this.focus.left;
    const newBreadcrumb = {
      value: this.focus.value,
      right: this.focus.right,
      side: 'left'
    };
    return new Zipper(newFocus, [...this.breadcrumbs, newBreadcrumb]);
  }

  right() {
    if (this.focus.right === null) {
      return null;
    }
    const newFocus = this.focus.right;
    const newBreadcrumb = {
      value: this.focus.value,
      left: this.focus.left,
      side: 'right'
    };
    return new Zipper(newFocus, [...this.breadcrumbs, newBreadcrumb]);
  }

  up() {
    if (this.breadcrumbs.length === 0) {
      return null;
    }
    const breadcrumb = this.breadcrumbs[this.breadcrumbs.length - 1];
    const newFocus = new Node(
      breadcrumb.value,
      breadcrumb.side === 'left' ? this.focus : breadcrumb.left,
      breadcrumb.side === 'right' ? this.focus : breadcrumb.right
    );
    const newBreadcrumbs = this.breadcrumbs.slice(0, -1);
    return new Zipper(newFocus, newBreadcrumbs);
  }

  setValue(value) {
    const newFocus = new Node(value, this.focus.left, this.focus.right);
    return new Zipper(newFocus, this.breadcrumbs);
  }

  setLeft(tree) {
    const newFocus = new Node(this.focus.value, tree, this.focus.right);
    return new Zipper(newFocus, this.breadcrumbs);
  }

  setRight(tree) {
    const newFocus = new Node(this.focus.value, this.focus.left, tree);
    return new Zipper(newFocus, this.breadcrumbs);
  }
}
