//
// This is only a SKELETON file for the 'Transpose' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const transpose = (inputLines) => {
  if (inputLines.length === 0) {
    return [];
  }

  // Find the maximum length of any line to determine the number of output rows
  const maxLen = Math.max(...inputLines.map((line) => line.length));

  const result = [];

  for (let col = 0; col < maxLen; col++) {
    let transposedRow = '';
    // Find the last row that has a character at this column index
    // This determines the length of the current transposed row (no right padding)
    let lastRowIndex = -1;
    for (let row = inputLines.length - 1; row >= 0; row--) {
      if (col < inputLines[row].length) {
        lastRowIndex = row;
        break;
      }
    }

    // Build the transposed row up to the lastRowIndex
    for (let row = 0; row <= lastRowIndex; row++) {
      if (col < inputLines[row].length) {
        transposedRow += inputLines[row][col];
      } else {
        // Pad with space if the current input row is too short,
        // but only if there's a character later in this column (which is guaranteed by lastRowIndex)
        transposedRow += ' ';
      }
    }
    result.push(transposedRow);
  }

  return result;
};
