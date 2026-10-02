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

    const firstDigit = colorCodes.indexOf(this.colors[0]);
    const secondDigit = colorCodes.indexOf(this.colors[1]);
    const zeros = colorCodes.indexOf(this.colors[2]);

    if (firstDigit === -1 || secondDigit === -1 || zeros === -1) {
      throw new Error('invalid color');
    }

    let value = (firstDigit * 10 + secondDigit) * Math.pow(10, zeros);

    let unit = 'ohms';
    if (value >= 1000000000) {
      value /= 1000000000;
      unit = 'gigaohms';
    } else if (value >= 1000000) {
      value /= 1000000;
      unit = 'megaohms';
    } else if (value >= 1000) {
      value /= 1000;
      unit = 'kiloohms';
    }

    return `Resistor value: ${value} ${unit}`;
  }
}
