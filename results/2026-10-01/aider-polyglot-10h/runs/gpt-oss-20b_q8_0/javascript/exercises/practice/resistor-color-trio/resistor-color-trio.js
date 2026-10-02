export class ResistorColorTrio {
  constructor(colors) {
    if (!Array.isArray(colors) || colors.length !== 3) {
      throw new Error('Exactly three colors must be provided');
    }

    const [first, second, third] = colors;

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

    // Validate input colors
    if (
      !(first in colorMap) ||
      !(second in colorMap) ||
      !(third in colorMap)
    ) {
      throw new Error('Invalid color band');
    }

    // Build the base number from the first two digits
    const baseNumber = colorMap[first] * 10 + colorMap[second];

    // Determine the multiplier (10^third)
    const multiplier = Math.pow(10, colorMap[third]);

    // Final resistance value in ohms
    const resistance = baseNumber * multiplier;

    // Determine metric prefix
    const prefixes = [
      { value: 1e9, label: 'gigaohms' },
      { value: 1e6, label: 'megaohms' },
      { value: 1e3, label: 'kiloohms' },
      { value: 1,   label: 'ohms' }
    ];

    let chosenPrefix = prefixes[prefixes.length - 1];
    for (const prefix of prefixes) {
      if (resistance >= prefix.value) {
        chosenPrefix = prefix;
        break;
      }
    }

    const formatted = resistance / chosenPrefix.value;
    const display = Number.isInteger(formatted) ? formatted : formatted.toFixed(1);

    // Store the final label string
    this._label = `Resistor value: ${display} ${chosenPrefix.label}`;
  }

  // Expose the label as a read‑only property
  get label() {
    return this._label;
  }
}
