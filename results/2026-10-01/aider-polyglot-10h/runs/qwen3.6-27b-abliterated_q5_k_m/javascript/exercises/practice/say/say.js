//
// This is only a SKELETON file for the 'Say' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

const ones = [
  '',
  'one',
  'two',
  'three',
  'four',
  'five',
  'six',
  'seven',
  'eight',
  'nine',
  'ten',
  'eleven',
  'twelve',
  'thirteen',
  'fourteen',
  'fifteen',
  'sixteen',
  'seventeen',
  'eighteen',
  'nineteen',
];

const tens = [
  '',
  '',
  'twenty',
  'thirty',
  'forty',
  'fifty',
  'sixty',
  'seventy',
  'eighty',
  'ninety',
];

const scales = ['', ' thousand', ' million', ' billion'];

const sayChunk = (n) => {
  let result = '';
  if (n >= 100) {
    result += ones[Math.floor(n / 100)] + ' hundred';
    n %= 100;
    if (n > 0) {
      result += ' ';
    }
  }

  if (n > 0) {
    if (n < 20) {
      result += ones[n];
    } else {
      const ten = Math.floor(n / 10);
      const one = n % 10;
      result += tens[ten];
      if (one > 0) {
        result += '-' + ones[one];
      }
    }
  }

  return result;
};

export const say = (n) => {
  if (n < 0 || n > 999999999999) {
    throw new Error('Number must be between 0 and 999,999,999,999.');
  }

  if (n === 0) {
    return 'zero';
  }

  let chunkIndex = 0;
  let result = '';

  while (n > 0) {
    const chunk = n % 1000;
    if (chunk !== 0) {
      const chunkStr = sayChunk(chunk) + scales[chunkIndex];
      if (result) {
        result = chunkStr + ' ' + result;
      } else {
        result = chunkStr;
      }
    }
    n = Math.floor(n / 1000);
    chunkIndex++;
  }

  return result;
};
