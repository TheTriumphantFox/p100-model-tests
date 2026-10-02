//
// This is only a SKELETON file for the 'Resistor Color Trio' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class ResistorColorTrio {
  constructor(colors) {
    this.colors = colors;
  }

  get label() {
    const colorCodes = [
      'black',
      'brown',
      'red',
      'orange',
      'yellow',
      'green',
      'blue',
      'violet',
      'grey',
      'white',
    ];

    const value1 = colorCodes.indexOf(this.colors[0]);
    const value2 = colorCodes.indexOf(this.colors[1]);
    const exponent = colorCodes.indexOf(this.colors[2]);

    if (value1 === -1 || value2 === -1 || exponent === -1) {
      throw new Error('invalid color');
    }

    let resistance = (value1 * 10 + value2) * (10 ** exponent);

    let unit = 'ohms';
    let value = resistance;

    if (resistance >= 1_000_000_000 && resistance % 1_000_000_000 === 0) {
      unit = 'gigaohms';
      value = resistance / 1_000_000_000;
    } else if (resistance >= 1_000_000 && resistance % 1_000_000 === 0) {
      unit = 'megaohms';
      value = resistance / 1_000_000;
    } else if (resistance >= 1_000 && resistance % 1_000 === 0) {
      unit = 'kiloohms';
      value = resistance / 1_000;
    }

    return `Resistor value: ${value} ${unit}`;
  }
}
