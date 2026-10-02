/**
 * Transposes a matrix represented as a string.
 *
 * The input is a string containing rows separated by newlines. Each row may
 * have a different length. The function pads shorter rows on the left with
 * spaces so that all rows have the same length. It then transposes the
 * matrix: rows become columns and columns become rows. The output is a
 * string with the transposed rows separated by newlines.
 *
 * @param {string} input - The input string to transpose.
 * @returns {string} The transposed string.
 */
export const transpose = (input) => {
  // Ensure we are working with a string. If input is undefined or null,
  // treat it as an empty string.
  const str = typeof input === 'string' ? input : '';

  // Split the input into rows. Preserve empty lines if any.
  const rows = str.split('\n');

  // Determine the maximum row length.
  const maxLen = rows.reduce((max, row) => Math.max(max, row.length), 0);

  // Pad each row on the left with spaces so all rows have the same length.
  const paddedRows = rows.map(row => {
    const padSize = maxLen - row.length;
    return ' '.repeat(padSize) + row;
  });

  // Build the transposed rows.
  const transposed = [];
  for (let col = 0; col < maxLen; col++) {
    let newRow = '';
    for (let r = 0; r < paddedRows.length; r++) {
      newRow += paddedRows[r][col];
    }
    transposed.push(newRow);
  }

  // Join the transposed rows with newlines.
  return transposed.join('\n');
};
