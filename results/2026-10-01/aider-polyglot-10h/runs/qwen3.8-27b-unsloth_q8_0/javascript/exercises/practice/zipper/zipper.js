//
// This is only a SKELETON file for the 'Zipper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Zipper {
  constructor(focus, path) {
    this.focus = focus;
    this.path = path;
  }

  static fromTree(tree) {
    return new Zipper(tree, []);
  }

  toTree() {
    let current = this.focus;
    for (let i = this.path.length - 1; i >= 0; i--) {
      const step = this.path[i];
      if (step.dir === 'left') {
        current = {
          value: step.value,
          left: current,
          right: step.sibling,
        };
      } else {
        current = {
          value: step.value,
          left: step.sibling,
          right: current,
        };
      }
    }
    return current;
  }

  value() {
    return this.focus.value;
  }

  left() {
    if (!this.focus.left) {
      return null;
    }
    return new Zipper(this.focus.left, [
      ...this.path,
      { dir: 'left', value: this.focus.value, sibling: this.focus.right },
    ]);
  }

  right() {
    if (!this.focus.right) {
      return null;
    }
    return new Zipper(this.focus.right, [
      ...this.path,
      { dir: 'right', value: this.focus.value, sibling: this.focus.left },
    ]);
  }

  up() {
    if (this.path.length === 0) {
      return null;
    }
    const lastStep = this.path[this.path.length - 1];
    const newPath = this.path.slice(0, -1);
    let newFocus;
    if (lastStep.dir === 'left') {
      newFocus = {
        value: lastStep.value,
        left: this.focus,
        right: lastStep.sibling,
      };
    } else {
      newFocus = {
        value: lastStep.value,
        left: lastStep.sibling,
        right: this.focus,
      };
    }
    return new Zipper(newFocus, newPath);
  }

  setValue(value) {
    return new Zipper(
      { ...this.focus, value: value },
      this.path
    );
  }

  setLeft(left) {
    return new Zipper(
      { ...this.focus, left: left },
      this.path
    );
  }

  setRight(right) {
    return new Zipper(
      { ...this.focus, right: right },
      this.path
    );
  }
}
