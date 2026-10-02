export class Triangle {
  constructor(...sides) {
    const [a, b, c] = sides;
    if (a <= 0 || b <= 0 || c <= 0) {
      throw new Error('All sides must be greater than 0');
    }
    if (a + b < c || b + c < a || a + c < b) {
      throw new Error('Invalid triangle: violates triangle inequality');
    }
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
