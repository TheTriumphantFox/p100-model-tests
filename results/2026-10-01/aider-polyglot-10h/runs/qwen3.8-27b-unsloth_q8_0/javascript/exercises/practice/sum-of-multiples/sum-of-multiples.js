//
// This is only a SKELETON file for the 'Sum Of Multiples' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const sum = (multiples, limit) => {
  const uniqueMultiples = new Set();

  for (const multiple of multiples) {
    if (multiple === 0) continue;
    for (let i = multiple; i < limit; i += multiple) {
      uniqueMultiples.add(i);
    }
  }

  let total = 0;
  for (const value of uniqueMultiples) {
    total += value;
  }

  return total;
};
