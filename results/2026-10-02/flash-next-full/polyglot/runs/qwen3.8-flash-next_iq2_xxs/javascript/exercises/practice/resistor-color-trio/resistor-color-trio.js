//
// This is only a SKELETON file for the 'Resistor Color Trio' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

const COLORS = ['black', 'brown', 'red', 'orange', 'yellow', 'green', 'blue', 'violet', 'grey', 'white'];

export class ResistorColorTrio {
  constructor(colors) {
    for (const color of colors) {
      if (!COLORS.includes(color)) {
        throw new Error('invalid color');
      }
    }
    this.colors = colors;
    this.label = this._computeLabel();
  }

  _computeLabel() {
    const values = this.colors.map(color => COLORS.indexOf(color));
    const digit1 = values[0];
    const digit2 = values[1];
    const multiplier = values[2];

    const mainValue = digit1 * 10 + digit2;
    const totalOhms = mainValue * Math.pow(10, multiplier);

    if (totalOhms >= 1e9) {
      return `Resistor value: ${totalOhms / 1e9} gigaohms`;
    } else if (totalOhms >= 1e6) {
      return `Resistor value: ${totalOhms / 1e6} megaohms`;
    } else if (totalOhms >= 1e3) {
      return `Resistor value: ${totalOhms / 1e3} kiloohms`;
    } else {
      return `Resistor value: ${totalOhms} ohms`;
    }
  }
}
