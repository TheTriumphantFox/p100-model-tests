//
// This is only a SKELETON file for the 'Zipper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Zipper {
  constructor(focus, path = []) {
    this._focus = focus;
    this._path = path;
  }

  static fromTree(tree) {
    return new Zipper(tree);
  }

  toTree() {
    if (this._path.length === 0) {
      return this._focus;
    }

    let current = this._focus;
    const path = [...this._path];

    while (path.length > 0) {
      const { parent, direction } = path.shift();
      const newNode = { ...parent };
      
      if (direction === 'left') {
        newNode.left = current;
      } else if (direction === 'right') {
        newNode.right = current;
      }
      
      current = newNode;
    }

    return current;
  }

  value() {
    return this._focus.value;
  }

  left() {
    if (!this._focus.left) {
      return null;
    }
    return new Zipper(this._focus.left, [{ parent: this._focus, direction: 'left' }, ...this._path]);
  }

  right() {
    if (!this._focus.right) {
      return null;
    }
    return new Zipper(this._focus.right, [{ parent: this._focus, direction: 'right' }, ...this._path]);
  }

  up() {
    if (this._path.length === 0) {
      return null;
    }
    const [{ parent }, ...restPath] = this._path;
    return new Zipper(parent, restPath);
  }

  setValue(newValue) {
    const newFocus = { ...this._focus, value: newValue };
    return new Zipper(newFocus, this._path);
  }

  setLeft(newLeft) {
    const newFocus = { ...this._focus, left: newLeft };
    return new Zipper(newFocus, this._path);
  }

  setRight(newRight) {
    const newFocus = { ...this._focus, right: newRight };
    return new Zipper(newFocus, this._path);
  }
}
