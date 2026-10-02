//
// This is only a SKELETON file for the 'Palindrome Products' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Palindromes {
  /**
   * Generate the largest and smallest palindromic products for a given inclusive range.
   *
   * @param {{ minFactor: number, maxFactor: number }} options
   * @returns {{
   *   largest: { value: number, factors: Array<[number, number]> },
   *   smallest: { value: number, factors: Array<[number, number]> }
   * }}
   */
  static generate({ minFactor, maxFactor }) {
    if (minFactor > maxFactor) {
      throw new Error('min must be <= max');
    }

    const palindromes = new Map(); // value -> Set of factor pairs

    // Helper to check if a number is a palindrome
    const isPalindrome = (num) => {
      const str = String(num);
      return str === str.split('').reverse().join('');
    };

    // Generate all products and collect palindromic ones
    for (let a = minFactor; a <= maxFactor; a++) {
      for (let b = a; b <= maxFactor; b++) {
        const product = a * b;
        if (isPalindrome(product)) {
          if (!palindromes.has(product)) {
            palindromes.set(product, new Set());
          }
          // Store factor pairs in sorted order to avoid duplicates like (2,3) and (3,2)
          palindromes.get(product).add(JSON.stringify([a, b]));
        }
      }
    }

    if (palindromes.size === 0) {
      return {
        largest: { value: null, factors: [] },
        smallest: { value: null, factors: [] },
      };
    }

    const sortedValues = Array.from(palindromes.keys()).sort((a, b) => a - b);
    const smallestValue = sortedValues[0];
    const largestValue = sortedValues[sortedValues.length - 1];

    const formatFactors = (value) => {
      const set = palindromes.get(value);
      const pairs = Array.from(set).map((str) => JSON.parse(str));
      return pairs;
    };

    return {
      smallest: {
        value: smallestValue,
        factors: formatFactors(smallestValue),
      },
      largest: {
        value: largestValue,
        factors: formatFactors(largestValue),
      },
    };
  }
}
