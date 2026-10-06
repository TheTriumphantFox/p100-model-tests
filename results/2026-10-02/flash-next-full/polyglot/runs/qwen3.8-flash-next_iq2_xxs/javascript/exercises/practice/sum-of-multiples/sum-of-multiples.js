//
// This is only a SKELETON file for the 'Sum Of Multiples' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const sum = (factors, limit) => {
  const uniqueMultiples = new Set();

  for (const factor of factors) {
    if (factor === 0) {
      continue;
    }
    for (let multiple = factor; multiple < limit; multiple += factor) {
      uniqueMultiples.add(multiple);
    }
  }

  let sum = 0;
  for (const multiple of uniqueMultiples) {
    sum += multiple;
  }

  return sum;
};
