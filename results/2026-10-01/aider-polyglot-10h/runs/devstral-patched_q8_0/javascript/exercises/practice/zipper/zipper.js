export class Zipper {
  constructor(tree, breadcrumbs) {
    this.tree = tree;
    this.breadcrumbs = breadcrumbs || [];
  }

  static fromTree(tree) {
    return new Zipper(tree, []);
  }

  toTree() {
    return this._rebuildTree(this.tree, this.breadcrumbs);
  }

  _rebuildTree(node, breadcrumbs) {
    if (breadcrumbs.length === 0) {
      return node;
    }

    const lastBreadcrumb = breadcrumbs[breadcrumbs.length - 1];
    const parent = lastBreadcrumb.parent;
    const newBreadcrumbs = breadcrumbs.slice(0, -1);

    if (lastBreadcrumb.direction === 'left') {
      return {
        ...parent,
        left: this._rebuildTree(node, newBreadcrumbs)
      };
    } else {
      return {
        ...parent,
        right: this._rebuildTree(node, newBreadcrumbs)
      };
    }
  }

  value() {
    return this.tree.value;
  }

  left() {
    if (this.tree.left) {
      return new Zipper(
        this.tree.left,
        [...this.breadcrumbs, { direction: 'left', parent: this.tree }]
      );
    }
    return null;
  }

  right() {
    if (this.tree.right) {
      return new Zipper(
        this.tree.right,
        [...this.breadcrumbs, { direction: 'right', parent: this.tree }]
      );
    }
    return null;
  }

  up() {
    if (this.breadcrumbs.length === 0) {
      return null; // Already at root
    }

    const lastBreadcrumb = this.breadcrumbs[this.breadcrumbs.length - 1];
    const parent = lastBreadcrumb.parent;
    const newBreadcrumbs = this.breadcrumbs.slice(0, -1);

    return new Zipper(parent, newBreadcrumbs);
  }

  setValue(value) {
    const newTree = { ...this.tree, value };
    return new Zipper(newTree, this.breadcrumbs);
  }

  setLeft(tree) {
    const newTree = { ...this.tree, left: tree };
    return new Zipper(newTree, this.breadcrumbs);
  }

  setRight(tree) {
    const newTree = { ...this.tree, right: tree };
    return new Zipper(newTree, this.breadcrumbs);
  }
}

// Helper Tree class (not exported, used internally)
class Tree {
  constructor(value, left = null, right = null) {
    this.value = value;
    this.left = left;
    this.right = right;
  }
}
