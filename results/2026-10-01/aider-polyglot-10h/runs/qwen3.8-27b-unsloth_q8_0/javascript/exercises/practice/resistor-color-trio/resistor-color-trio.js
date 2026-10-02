//
// This is only a SKELETON file for the 'Resistor Color Trio' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class ResistorColorTrio {
  constructor(colors) {
    this.colors = colors;
  }

  get label() {
    const colorMap = {
      black: 0,
      brown: 1,
      red: 2,
      orange: 3,
      yellow: 4,
      green: 5,
      blue: 6,
      violet: 7,
      grey: 8,
      white: 9,
    };

    const [first, second, third] = this.colors;
    
    if (!(first in colorMap) || !(second in colorMap) || !(third in colorMap)) {
      throw new Error('invalid color');
    }

    const firstValue = colorMap[first];
    const secondValue = colorMap[second];
    const multiplier = colorMap[third];

    const value = (firstValue * 10 + secondValue) * Math.pow(10, multiplier);

    let unit = 'ohms';
    let displayValue = value;

    if (value >= 1000000000) {
      displayValue = value / 1000000000;
      unit = 'gigaohms';
    } else if (value >= 1000000) {
      displayValue = value / 1000000;
      unit = 'megaohms';
    } else if (value >= 1000) {
      displayValue = value / 1000;
      unit = 'kiloohms';
    }

    return `Resistor value: ${displayValue} ${unit}`;
  }
}
