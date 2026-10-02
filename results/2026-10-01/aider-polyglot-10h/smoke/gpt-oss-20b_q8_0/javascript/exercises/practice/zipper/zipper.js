/**
 * A purely functional zipper for a binary tree.
 *
 * The tree nodes are expected to be plain objects of the form:
 *   { value: any, left: Tree | null, right: Tree | null }
 *
 * The zipper keeps a focus node and a stack of contexts that describe
 * the path from the root to the focus.  Each context contains the
 * sibling subtrees and the value of the parent node.
 */
export class Zipper {
  /**
   * Create a new zipper with the given focus node and trail.
   *
   * @param {Object} focus - The current node in focus.
   * @param {Array} trail - An array of context objects.
   */
  constructor(focus, trail = []) {
    this.focus = focus;
    this.trail = trail;
  }

  /**
   * Create a zipper from a tree.  The focus starts at the root.
   *
   * @param {Object} tree - The root of the binary tree.
   * @returns {Zipper}
   */
  static fromTree(tree) {
    return new Zipper(tree, []);
  }

  /**
   * Convert the zipper back into a tree.
   *
   * @returns {Object} The root of the tree.
   */
  toTree() {
    // Walk back up to the root, reconstructing the tree.
    let node = this.focus;
    let trail = this.trail.slice(); // copy
    while (trail.length > 0) {
      const ctx = trail.pop();
      node = {
        value: ctx.value,
        left: ctx.left === ctx.focus ? node : ctx.left,
        right: ctx.right === ctx.focus ? node : ctx.right,
      };
    }
    return node;
  }

  /**
   * Get the value of the focus node.
   *
   * @returns {any}
   */
  value() {
    return this.focus.value;
  }

  /**
   * Get the left child of the focus node.
   *
   * @returns {Zipper}
   */
  left() {
    if (!this.focus.left) return null;
    const newTrail = this.trail.concat({
      value: this.focus.value,
      left: this.focus.left,
      right: this.focus.right,
      focus: this.focus.left,
    });
    return new Zipper(this.focus.left, newTrail);
  }

  /**
   * Get the right child of the focus node.
   *
   * @returns {Zipper}
   */
  right() {
    if (!this.focus.right) return null;
    const newTrail = this.trail.concat({
      value: this.focus.value,
      left: this.focus.left,
      right: this.focus.right,
      focus: this.focus.right,
    });
    return new Zipper(this.focus.right, newTrail);
  }

  /**
   * Move the focus to the parent node.
   *
   * @returns {Zipper}
   */
  up() {
    if (this.trail.length === 0) return null;
    const ctx = this.trail[this.trail.length - 1];
    const newFocus = {
      value: ctx.value,
      left: ctx.left,
      right: ctx.right,
    };
    const newTrail = this.trail.slice(0, -1);
    return new Zipper(newFocus, newTrail);
  }

  /**
   * Set the value of the focus node.
   *
   * @param {any} val
   * @returns {Zipper}
   */
  setValue(val) {
    const newFocus = { ...this.focus, value: val };
    return new Zipper(newFocus, this.trail);
  }

  /**
   * Set the left subtree of the focus node.
   *
   * @param {Object|null} subtree
   * @returns {Zipper}
   */
  setLeft(subtree) {
    const newFocus = { ...this.focus, left: subtree };
    return new Zipper(newFocus, this.trail);
  }

  /**
   * Set the right subtree of the focus node.
   *
   * @param {Object|null} subtree
   * @returns {Zipper}
   */
  setRight(subtree) {
    const newFocus = { ...this.focus, right: subtree };
    return new Zipper(newFocus, this.trail);
  }
}
