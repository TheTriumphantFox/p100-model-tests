//
// This is only a SKELETON file for the 'Palindrome Products' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export class Palindromes {
  static generate({ min, max }) {
    if (min > max) {
      throw new Error('min must be <= max');
    }

    const smallest = this._findSmallest(min, max);
    const largest = this._findLargest(min, max);

    return {
      smallest,
      largest,
    };
  }

  static _isPalindrome(n) {
    const s = n.toString();
    return s === s.split('').reverse().join('');
  }

  static _findSmallest(min, max) {
    let smallestPalindrome = null;
    let factors = [];

    for (let i = min; i <= max; i++) {
      for (let j = i; j <= max; j++) {
        const product = i * j;

        if (smallestPalindrome !== null && product > smallestPalindrome) {
          break;
        }

        if (this._isPalindrome(product)) {
          if (smallestPalindrome === null || product < smallestPalindrome) {
            smallestPalindrome = product;
            factors = [[i, j]];
          } else if (product === smallestPalindrome) {
            factors.push([i, j]);
          }
        }
      }
      
      if (smallestPalindrome !== null && i * i > smallestPalindrome) {
        break;
      }
    }

    if (smallestPalindrome === null) {
      return { value: null, factors: [] };
    }

    return { value: smallestPalindrome, factors };
  }

  static _findLargest(min, max) {
    let largestPalindrome = null;
    let factors = [];

    for (let i = max; i >= min; i--) {
      for (let j = i; j >= min; j--) {
        const product = i * j;

        if (largestPalindrome !== null && product < largestPalindrome) {
          break;
        }

        if (this._isPalindrome(product)) {
          if (largestPalindrome === null || product > largestPalindrome) {
            largestPalindrome = product;
            factors = [[j, i]];
          } else if (product === largestPalindrome) {
            factors.push([j, i]);
          }
        }
      }
      
      if (largestPalindrome !== null && i * max < largestPalindrome) {
        break;
      }
    }

    if (largestPalindrome === null) {
      return { value: null, factors: [] };
    }

    return { value: largestPalindrome, factors };
  }
}
