//
// This is only a SKELETON file for the 'Transpose' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const transpose = (input) => {
  if (input.length === 0) {
    return '';
  }

  const maxRowLength = Math.max(...input.map((row) => row.length));
  const transposed = [];

  for (let colIndex = 0; colIndex < maxRowLength; colIndex++) {
    let transposedRow = '';
    for (let rowIndex = 0; rowIndex < input.length; rowIndex++) {
      const row = input[rowIndex];
      if (colIndex < row.length) {
        transposedRow += row[colIndex];
      } else {
        transposedRow += ' ';
      }
    }
    transposed.push(transposedRow.trimEnd());
  }

  return transposed.join('\n');
};
