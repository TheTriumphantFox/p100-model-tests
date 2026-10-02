//
// This is only a SKELETON file for the 'Killer Sudoku Helper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const combinations = (cage) => {
  const { sum, size, exclude = [] } = cage;
  const results = [];

  const backtrack = (start, currentSum, currentCombo) => {
    if (currentCombo.length === size) {
      if (currentSum === sum) {
        results.push([...currentCombo]);
      }
      return;
    }

    for (let i = start; i <= 9; i++) {
      if (exclude.includes(i)) {
        continue;
      }
      if (currentSum + i > sum) {
        break;
      }
      currentCombo.push(i);
      backtrack(i + 1, currentSum + i, currentCombo);
      currentCombo.pop();
    }
  };

  backtrack(1, 0, []);
  return results;
};
