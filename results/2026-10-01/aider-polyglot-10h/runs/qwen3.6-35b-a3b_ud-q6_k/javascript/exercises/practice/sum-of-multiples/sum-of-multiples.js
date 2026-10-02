//
// This is only a SKELETON file for the 'Sum Of Multiples' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const sum = (factors, limit) => {
  const multiples = new Set();

  for (const factor of factors) {
    if (factor === 0) {
      continue;
    }
    for (let i = factor; i < limit; i += factor) {
      multiples.add(i);
    }
  }

  return Array.from(multiples).reduce((acc, curr) => acc + curr, 0);
};
