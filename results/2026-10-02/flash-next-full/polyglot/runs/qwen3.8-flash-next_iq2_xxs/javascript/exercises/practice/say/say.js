//
// This is only a SKELETON file for the 'Say' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

const ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'];
const tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'];
const scales = ['', 'thousand', 'million', 'billion', 'trillion'];

const belowTen = (n) => {
  return ones[n];
};

const belowTwenty = (n) => {
  if (n < 10) return belowTen(n);
  if (n < 20) return ones[n];
  return `${tens[Math.floor(n / 10)]}${n % 10 ? '-' + ones[n % 10] : ''}`;
};

const belowHundred = (n) => {
  if (n < 20) return belowTwenty(n);
  const ten = Math.floor(n / 10);
  const rem = n % 10;
  if (rem === 0) return tens[ten];
  return `${tens[ten]}-${ones[rem]}`;
};

const belowThousand = (n) => {
  if (n < 100) return belowHundred(n);
  const hundred = Math.floor(n / 100);
  const rem = n % 100;
  if (rem === 0) return `${ones[hundred]} hundred`;
  return `${ones[hundred]} hundred ${belowHundred(rem)}`;
};

export const say = (n) => {
  if (n < 0 || n > 999999999999) {
    throw new Error('Number must be between 0 and 999,999,999,999.');
  }

  if (n === 0) return 'zero';

  let result = '';
  let scaleIndex = 0;
  let remaining = n;

  while (remaining > 0) {
    const chunk = remaining % 1000;
    remaining = Math.floor(remaining / 1000);

    if (chunk !== 0) {
      let chunkWords = belowThousand(chunk);
      if (scaleIndex > 0) {
        chunkWords += ` ${scales[scaleIndex]}`;
      }
      result = `${chunkWords} ${result}`.trim();
    }
    scaleIndex++;
  }

  return result;
};
