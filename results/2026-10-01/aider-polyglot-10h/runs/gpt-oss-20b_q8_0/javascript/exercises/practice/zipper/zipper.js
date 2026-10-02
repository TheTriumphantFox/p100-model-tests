export class Zipper {
  /**
   * Create a new zipper with the given root and focus path.
   * @param {Object} root - The root node of the tree.
   * @param {Array} path - Array of nodes from the root to the focus node.
   */
  constructor(root, path = []) {
    this.root = root;
    this.path = path;
  }

  /**
   * Create a zipper from a binary tree.
   * @param {Object} tree - The root node {value, left, right}
   * @returns {Zipper}
   */
  static fromTree(tree) {
    if (!tree) {
      throw new Error('Cannot create a zipper from an empty tree');
    }
    return new Zipper(tree, [tree]);
  }

  /**
   * Convert the zipper back into a binary tree.
   * @returns {Object} The root node of the tree.
   */
  toTree() {
    return this.root;
  }

  /**
   * Get the value of the focus node.
   * @returns {*}
   */
  value() {
    return this.focus.value;
  }

  /**
   * Get the left child of the focus node.
   * @returns {Zipper|null}
   */
  left() {
    if (!this.focus.left) return null;
    return new Zipper(this.root, [...this.path, this.focus.left]);
  }

  /**
   * Get the right child of the focus node.
   * @returns {Zipper|null}
   */
  right() {
    if (!this.focus.right) return null;
    return new Zipper(this.root, [...this.path, this.focus.right]);
  }

  /**
   * Move the focus to the parent node.
   * @returns {Zipper|null}
   */
  up() {
    if (this.path.length <= 1) return null;
    return new Zipper(this.root, this.path.slice(0, -1));
  }

  /**
   * Set the value of the focus node.
   * @param {*} newValue
   * @returns {Zipper}
   */
  setValue(newValue) {
    const newRoot = this._cloneTree();
    const node = this._getNode(newRoot, this.path);
    node.value = newValue;
    return new Zipper(newRoot, this.path);
  }

  /**
   * Set the left child of the focus node.
   * @param {Object|null} newLeft
   * @returns {Zipper}
   */
  setLeft(newLeft) {
    const newRoot = this._cloneTree();
    const node = this._getNode(newRoot, this.path);
    node.left = newLeft;
    return new Zipper(newRoot, this.path);
  }

  /**
   * Set the right child of the focus node.
   * @param {Object|null} newRight
   * @returns {Zipper}
   */
  setRight(newRight) {
    const newRoot = this._cloneTree();
    const node = this._getNode(newRoot, this.path);
    node.right = newRight;
    return new Zipper(newRoot, this.path);
  }

  /* ---------- Internal helpers ---------- */

  get focus() {
    return this.path[this.path.length - 1];
  }

  /**
   * Deep clone the tree rooted at this.root.
   * @returns {Object}
   */
  _cloneTree() {
    const clone = (node) => {
      if (!node) return null;
      return {
        value: node.value,
        left: clone(node.left),
        right: clone(node.right),
      };
    };
    return clone(this.root);
  }

  /**
   * Retrieve the node at the given path from the provided root.
   * @param {Object} root
   * @param {Array} path
   * @returns {Object}
   */
  _getNode(root, path) {
    let node = root;
    for (let i = 1; i < path.length; i++) {
      if (!node) throw new Error('Invalid path');
      node = node === path[i - 1] ? path[i] : node.left === path[i] ? node.left : node.right;
    }
    return node;
  }
}
