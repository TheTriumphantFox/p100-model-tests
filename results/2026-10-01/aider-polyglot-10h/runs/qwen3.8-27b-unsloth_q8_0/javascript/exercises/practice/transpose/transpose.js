//
// This is only a SKELETON file for the 'Transpose' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const transpose = (input) => {
  if (input.length === 0) return [];

  const maxLength = Math.max(...input.map((row) => row.length));
  const result = [];

  for (let col = 0; col < maxLength; col++) {
    let newRow = '';
    for (let row = 0; row < input.length; row++) {
      if (col < input[row].length) {
        newRow += input[row][col];
      } else {
        newRow += ' ';
      }
    }
    result.push(newRow);
  }

  return result;
};
