//
// This is only a SKELETON file for the 'Say' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

const ones = [
  'zero',
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

const scales = ['', 'thousand', 'million', 'billion'];

function convertChunk(num) {
  if (num === 0) {
    return '';
  }
  
  let result = '';
  
  if (num >= 100) {
    const hundreds = Math.floor(num / 100);
    result += ones[hundreds] + ' hundred';
    num %= 100;
    if (num > 0) {
      result += ' ';
    }
  }
  
  if (num >= 20) {
    const ten = Math.floor(num / 10);
    const one = num % 10;
    result += tens[ten];
    if (one > 0) {
      result += '-' + ones[one];
    }
  } else if (num > 0) {
    result += ones[num];
  }
  
  return result;
}

export const say = (n) => {
  if (typeof n !== 'number' || !Number.isInteger(n)) {
    throw new Error('Input must be an integer');
  }
  
  if (n < 0 || n > 999999999999) {
    throw new Error('Number must be between 0 and 999,999,999,999.');
  }
  
  if (n === 0) {
    return 'zero';
  }
  
  let result = '';
  let scaleIndex = 0;
  
  while (n > 0) {
    const chunk = n % 1000;
    if (chunk !== 0) {
      let chunkStr = convertChunk(chunk);
      if (scales[scaleIndex]) {
        chunkStr += ' ' + scales[scaleIndex];
      }
      if (result) {
        result = chunkStr + ' ' + result;
      } else {
        result = chunkStr;
      }
    }
    n = Math.floor(n / 1000);
    scaleIndex++;
  }
  
  return result;
};
