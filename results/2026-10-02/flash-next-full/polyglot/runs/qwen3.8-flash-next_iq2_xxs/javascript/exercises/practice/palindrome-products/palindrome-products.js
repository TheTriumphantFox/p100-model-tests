//
// This is only a SKELETON file for the 'Palindrome Products' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Palindromes {
  static generate({ minFactor, maxFactor }) {
    if (minFactor > maxFactor) {
      throw new Error('min must be <= max');
    }

    let smallest = null;
    let largest = null;
    const smallestFactors = [];
    const largestFactors = [];

    for (let i = minFactor; i <= maxFactor; i++) {
      for (let j = i; j <= maxFactor; j++) {
        const product = i * j;
        if (Palindromes.isPalindrome(product)) {
          if (smallest === null || product < smallest) {
            smallest = product;
            smallestFactors.length = 0;
            smallestFactors.push([i, j]);
          } else if (product === smallest) {
            smallestFactors.push([i, j]);
          }

          if (largest === null || product > largest) {
            largest = product;
            largestFactors.length = 0;
            largestFactors.push([i, j]);
          } else if (product === largest) {
            largestFactors.push([i, j]);
          }
        }
      }
    }

    return {
      smallest: { value: smallest, factors: smallestFactors },
      largest: { value: largest, factors: largestFactors },
    };
  }

  static isPalindrome(num) {
    const str = num.toString();
    const len = str.length;
    for (let i = 0; i < Math.floor(len / 2); i++) {
      if (str[i] !== str[len - 1 - i]) {
        return false;
      }
    }
    return true;
  }
}
