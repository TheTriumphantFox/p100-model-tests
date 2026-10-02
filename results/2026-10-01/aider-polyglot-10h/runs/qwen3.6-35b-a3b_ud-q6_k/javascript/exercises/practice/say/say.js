//
// This is only a SKELETON file for the 'Say' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

const SMALL_NUMBERS = [
  'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
  'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'
];

const TENS = [
  '', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'
];

const SCALES = [
  '', ' thousand', ' million', ' billion'
];

const saySmall = (n) => {
  if (n < 20) {
    return SMALL_NUMBERS[n];
  } else {
    const ten = Math.floor(n / 10);
    const unit = n % 10;
    if (unit === 0) {
      return TENS[ten];
    } else {
      return `${TENS[ten]}-${SMALL_NUMBERS[unit]}`;
    }
  }
};

const sayHundreds = (n) => {
  if (n === 0) {
    return '';
  } else if (n < 100) {
    return saySmall(n);
  } else {
    const hundred = Math.floor(n / 100);
    const remainder = n % 100;
    if (remainder === 0) {
      return `${SMALL_NUMBERS[hundred]} hundred`;
    } else {
      return `${SMALL_NUMBERS[hundred]} hundred ${saySmall(remainder)}`;
    }
  }
};

export const say = (n) => {
  if (n < 0 || n > 999999999999) {
    throw new Error('Number must be between 0 and 999,999,999,999.');
  }

  if (n === 0) {
    return 'zero';
  }

  let chunks = [];
  let scaleIndex = 0;

  let num = n;
  while (num > 0) {
    const chunk = num % 1000;
    if (chunk > 0) {
      chunks.unshift({
        value: sayHundreds(chunk),
        scale: SCALES[scaleIndex]
      });
    }
    num = Math.floor(num / 1000);
    scaleIndex++;
  }

  return chunks.map(chunk => chunk.value + chunk.scale).join(' ').trim();
};
