export class Palindromes {
  static generate({ minFactor, maxFactor }) {
    if (minFactor > maxFactor) {
      throw new Error('min must be <= max');
    }

    const palindromes = new Map();

    // Generate all possible products within the range
    for (let i = minFactor; i <= maxFactor; i++) {
      for (let j = i; j <= maxFactor; j++) {
        const product = i * j;
        if (this.isPalindrome(product)) {
          if (!palindromes.has(product)) {
            palindromes.set(product, []);
          }
          palindromes.get(product).push([i, j]);
        }
      }
    }

    if (palindromes.size === 0) {
      return { smallest: { value: null, factors: [] }, largest: { value: null, factors: [] } };
    }

    // Find smallest and largest palindromes
    const sortedPalindromes = Array.from(palindromes.entries()).sort((a, b) => a[0] - b[0]);
    const smallest = {
      value: sortedPalindromes[0][0],
      factors: sortedPalindromes[0][1]
    };

    const largest = {
      value: sortedPalindromes[sortedPalindromes.length - 1][0],
      factors: sortedPalindromes[sortedPalindromes.length - 1][1]
    };

    return { smallest, largest };
  }

  static isPalindrome(num) {
    const str = num.toString();
    return str === str.split('').reverse().join('');
  }
}
