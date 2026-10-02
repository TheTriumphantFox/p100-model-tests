export class Zipper {
  /**
   * Create a new zipper with the given focus node and context stack.
   * @param {Object} focus - The current node {value, left, right}
   * @param {Array} context - Array of context objects for ancestors.
   * Each context object has:
   *   parent: the parent node
   *   left: sibling to the left of the focus (may be null)
   *   right: sibling to the right of the focus (may be null)
   */
  constructor(focus, context = []) {
    this.focus = focus;
    this.context = context;
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
    return new Zipper(tree, []);
  }

  /**
   * Convert the zipper back into a binary tree.
   * @returns {Object} The root node of the tree.
   */
  toTree() {
    let node = this.focus;
    // Walk up to the root, reconstructing the tree.
    for (let i = this.context.length - 1; i >= 0; i--) {
      const ctx = this.context[i];
      node = {
        value: ctx.parent.value,
        left: ctx.left !== null ? ctx.left : node,
        right: ctx.right !== null ? ctx.right : node,
      };
    }
    return node;
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
    return new Zipper(this.focus.left, [
      ...this.context,
      { parent: this.focus, left: null, right: this.focus.right },
    ]);
  }

  /**
   * Get the right child of the focus node.
   * @returns {Zipper|null}
   */
  right() {
    if (!this.focus.right) return null;
    return new Zipper(this.focus.right, [
      ...this.context,
      { parent: this.focus, left: this.focus.left, right: null },
    ]);
  }

  /**
   * Move the focus to the parent node.
   * @returns {Zipper|null}
   */
  up() {
    if (this.context.length === 0) return null;
    const ctx = this.context[this.context.length - 1];
    const newContext = this.context.slice(0, -1);
    return new Zipper(ctx.parent, newContext);
  }

  /**
   * Set the value of the focus node.
   * @param {*} newValue
   * @returns {Zipper}
   */
  setValue(newValue) {
    const newFocus = { ...this.focus, value: newValue };
    return new Zipper(newFocus, this.context);
  }

  /**
   * Set the left child of the focus node.
   * @param {Object|null} newLeft
   * @returns {Zipper}
   */
  setLeft(newLeft) {
    const newFocus = { ...this.focus, left: newLeft };
    return new Zipper(newFocus, this.context);
  }

  /**
   * Set the right child of the focus node.
   * @param {Object|null} newRight
   * @returns {Zipper}
   */
  setRight(newRight) {
    const newFocus = { ...this.focus, right: newRight };
    return new Zipper(newFocus, this.context);
  }
}
