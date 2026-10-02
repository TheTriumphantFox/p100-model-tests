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
  white: 9
};

export class ResistorColorTrio {
  constructor(colors) {
    this.colors = colors;
    this.validateColors();
  }

  validateColors() {
    for (const color of this.colors) {
      if (!(color in colorMap)) {
        throw new Error('invalid color');
      }
    }
  }

  label() {
    const [firstColor, secondColor, thirdColor] = this.colors;
    const firstValue = colorMap[firstColor];
    const secondValue = colorMap[secondColor];
    const thirdValue = colorMap[thirdColor];

    const mainValue = firstValue * 10 + secondValue;
    const ohmsValue = mainValue * Math.pow(10, thirdValue);

    if (ohmsValue >= 1000) {
      return `Resistor value: ${Math.round(ohmsValue / 1000)} kiloohms`;
    } else {
      return `Resistor value: ${ohmsValue} ohms`;
    }
  }
}
