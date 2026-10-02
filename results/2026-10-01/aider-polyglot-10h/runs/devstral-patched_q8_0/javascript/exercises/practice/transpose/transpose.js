export const transpose = (lines) => {
  if (!lines || lines.length === 0) return [];

  // Find the maximum line length
  const maxLength = Math.max(...lines.map(line => line.length));

  // Pad each line to the max length with spaces on the left
  const paddedLines = lines.map(line => line.padStart(maxLength));

  // Transpose the matrix
  const transposed = [];
  for (let col = 0; col < maxLength; col++) {
    let transposedLine = '';
    for (let row = 0; row < lines.length; row++) {
      transposedLine += paddedLines[row][col];
    }
    transposed.push(transposedLine);
  }

  return transposed;
};
