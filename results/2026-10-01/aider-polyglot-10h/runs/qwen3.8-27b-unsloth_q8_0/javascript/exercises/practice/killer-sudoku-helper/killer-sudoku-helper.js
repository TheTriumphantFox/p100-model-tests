//
// This is only a SKELETON file for the 'Killer Sudoku Helper' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const combinations = (cage) => {
  let sum;
  let excluded;
  let size;

  if (typeof cage === 'number') {
    sum = cage;
    excluded = new Set();
    size = 1;
  } else {
    sum = cage[cage.length - 1];
    excluded = new Set(cage.slice(0, -1));
    size = cage.length - 1;
  }

  const results = [];

  const generate = (start, current) => {
    if (current.length === size) {
      const currentSum = current.reduce((a, b) => a + b, 0);
      if (currentSum === sum && !current.some((digit) => excluded.has(digit))) {
        results.push([...current]);
      }
      return;
    }

    for (let i = start; i <= 9; i++) {
      if (excluded.has(i)) continue;
      current.push(i);
      generate(i + 1, current);
      current.pop();
    }
  };

  generate(1, []);
  
  // Sort the results to ensure consistent ordering
  results.sort((a, b) => {
    for (let i = 0; i < a.length; i++) {
      if (a[i] !== b[i]) {
        return a[i] - b[i];
      }
    }
    return 0;
  });

  return results;
};
