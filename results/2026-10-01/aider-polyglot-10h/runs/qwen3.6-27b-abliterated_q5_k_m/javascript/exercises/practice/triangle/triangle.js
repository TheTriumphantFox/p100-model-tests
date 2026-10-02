//
// This is only a SKELETON file for the 'Triangle' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Triangle {
  constructor(...sides) {
    this.sides = sides;
  }

  get isEquilateral() {
    const [a, b, c] = this.sides;
    return this._isTriangle() && a === b && b === c;
  }

  get isIsosceles() {
    const [a, b, c] = this.sides;
    return this._isTriangle() && (a === b || b === c || a === c);
  }

  get isScalene() {
    const [a, b, c] = this.sides;
    return this._isTriangle() && a !== b && b !== c && a !== c;
  }

  _isTriangle() {
    const [a, b, c] = this.sides;
    if (a <= 0 || b <= 0 || c <= 0) {
      return false;
    }
    if (a + b < c || b + c < a || a + c < b) {
      return false;
    }
    return true;
  }
}
