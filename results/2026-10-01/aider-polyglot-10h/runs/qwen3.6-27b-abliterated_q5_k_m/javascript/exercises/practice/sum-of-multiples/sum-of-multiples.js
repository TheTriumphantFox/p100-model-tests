//
// This is only a SKELETON file for the 'Sum Of Multiples' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const sum = (items, level) => {
  const multiples = new Set();

  for (const item of items) {
    if (item === 0) {
      multiples.add(0);
      continue;
    }
    for (let i = item; i < level; i += item) {
      multiples.add(i);
    }
  }

  let total = 0;
  for (const multiple of multiples) {
    total += multiple;
  }

  return total;
};
