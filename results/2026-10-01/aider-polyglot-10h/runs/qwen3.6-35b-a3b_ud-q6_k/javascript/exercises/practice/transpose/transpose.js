//
// This is only a SKELETON file for the 'Transpose' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const transpose = (input) => {
  if (!input || input.length === 0) {
    return [];
  }

  const maxLen = Math.max(...input.map((line) => line.length), 0);
  const result = [];

  for (let i = 0; i < maxLen; i++) {
    let row = '';
    for (let j = 0; j < input.length; j++) {
      const char = input[j][i];
      if (char !== undefined) {
        row += char;
      } else {
        // Check if there are any more characters in subsequent lines for this column
        let hasMore = false;
        for (let k = j + 1; k < input.length; k++) {
          if (input[k][i] !== undefined) {
            hasMore = true;
            break;
          }
        }
        if (hasMore) {
          row += ' ';
        } else {
          break;
        }
      }
    }
    result.push(row);
  }

  return result;
};
