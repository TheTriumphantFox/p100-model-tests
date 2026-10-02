//
// This is only a SKELETON file for the 'Killer Sudoku Helper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const combinations = (cage) => {
  const { target, size, exclude = [] } = cage;
  const result = [];

  const findCombinations = (currentCombination, startDigit, currentSum) => {
    if (currentCombination.length === size) {
      if (currentSum === target) {
        result.push([...currentCombination]);
      }
      return;
    }

    for (let digit = startDigit; digit <= 9; digit++) {
      if (exclude.includes(digit)) continue;
      if (currentSum + digit > target) break;

      currentCombination.push(digit);
      findCombinations(currentCombination, digit + 1, currentSum + digit);
      currentCombination.pop();
    }
  };

  findCombinations([], 1, 0);

  return result;
};
