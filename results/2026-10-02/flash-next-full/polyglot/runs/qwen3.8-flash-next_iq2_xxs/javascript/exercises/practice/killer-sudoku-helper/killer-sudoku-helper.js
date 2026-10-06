//
// This is only a SKELETON file for the 'Killer Sudoku Helper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const combinations = (cage) => {
  const { size, sum, exclude } = cage;
  const validCombinations = [];

  const isValidCombination = (combination) => {
    // Check if sum matches
    const currentSum = combination.reduce((acc, val) => acc + val, 0);
    if (currentSum !== sum) {
      return false;
    }

    // Check if any digit in the combination is in the exclude list
    if (exclude && exclude.length > 0) {
      for (const digit of combination) {
        if (exclude.includes(digit)) {
          return false;
        }
      }
    }

    return true;
  };

  const generateCombinations = (start, currentCombination) => {
    if (currentCombination.length === size) {
      if (isValidCombination(currentCombination)) {
        validCombinations.push([...currentCombination]);
      }
      return;
    }

    // Prune: if current sum already exceeds target, no need to continue
    const currentSum = currentCombination.reduce((acc, val) => acc + val, 0);
    if (currentSum > sum) {
      return;
    }

    // Prune: if remaining cells cannot reach the sum even with max digits, no need to continue
    const remainingCells = size - currentCombination.length;
    const maxPossibleSum = currentSum + Array.from({ length: remainingCells }, (_, i) => 9 - i).reduce((acc, val) => acc + val, 0);
    if (maxPossibleSum < sum) {
      return;
    }

    for (let digit = start; digit <= 9; digit++) {
      // Optimization: if adding this digit makes the sum too large for the remaining cells, break
      // The smallest sum we can get with remaining cells is 1+2+...+remainingCells
      const minRemainingSum = Array.from({ length: remainingCells - 1 }, (_, i) => 1 + i).reduce((acc, val) => acc + val, 0);
      if (currentSum + digit + minRemainingSum > sum) {
        break;
      }

      generateCombinations(digit + 1, [...currentCombination, digit]);
    }
  };

  generateCombinations(1, []);

  // Sort the combinations lexicographically
  validCombinations.sort((a, b) => {
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      if (a[i] !== b[i]) {
        return a[i] - b[i];
      }
    }
    return a.length - b.length;
  });

  return validCombinations;
};
