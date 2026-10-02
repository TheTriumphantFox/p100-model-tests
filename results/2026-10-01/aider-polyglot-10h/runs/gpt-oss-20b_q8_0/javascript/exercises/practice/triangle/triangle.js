//
// This is only a SKELETON file for the 'Triangle' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Triangle {
  constructor(...sides) {
    if (sides.length !== 3) {
      throw new Error('Triangle requires exactly three side lengths');
    }
    const [a, b, c] = sides;
    // Store the sides without performing validation.  The tests expect the
    // constructor to accept any numeric values (including zero or negative
    // numbers) and to let the property getters determine the triangle type.
    this.sides = [a, b, c];
  }

  get isEquilateral() {
    const [a, b, c] = this.sides;
    return a === b && b === c;
  }

  get isIsosceles() {
    const [a, b, c] = this.sides;
    return a === b || b === c || a === c;
  }

  get isScalene() {
    const [a, b, c] = this.sides;
    return a !== b && b !== c && a !== c;
  }
}
