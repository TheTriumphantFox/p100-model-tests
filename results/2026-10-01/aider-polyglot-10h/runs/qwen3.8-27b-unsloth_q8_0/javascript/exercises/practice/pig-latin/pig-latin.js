//
// This is only a SKELETON file for the 'Pig Latin' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const translate = (text) => {
  return text
    .split(' ')
    .map(translateWord)
    .join(' ');
};

const translateWord = (word) => {
  if (!word) return word;

  const lowerWord = word.toLowerCase();
  const vowels = 'aeiou';

  // Rule 1: Starts with a vowel, or "xr", or "yt"
  if (
    vowels.includes(lowerWord[0]) ||
    lowerWord.startsWith('xr') ||
    lowerWord.startsWith('yt')
  ) {
    return word + 'ay';
  }

  // Rule 3: Starts with zero or more consonants followed by "qu"
  const quIndex = lowerWord.indexOf('qu');
  if (quIndex !== -1) {
    // Check if everything before "qu" is consonants
    const prefix = lowerWord.substring(0, quIndex);
    if (prefix.split('').every((char) => !vowels.includes(char))) {
      const movePart = word.substring(0, quIndex + 2);
      const rest = word.substring(quIndex + 2);
      return rest + movePart + 'ay';
    }
  }

  // Rule 4: Starts with one or more consonants followed by "y"
  // Find the first 'y' that is not at the start (since start is handled by Rule 1 if it was a vowel, but 'y' is not a vowel here)
  // Actually, Rule 4 says "starts with one or more consonants followed by y".
  // So we look for 'y' at index > 0.
  const yIndex = lowerWord.indexOf('y', 1);
  if (yIndex !== -1) {
    const prefix = lowerWord.substring(0, yIndex);
    if (prefix.split('').every((char) => !vowels.includes(char))) {
      const movePart = word.substring(0, yIndex);
      const rest = word.substring(yIndex);
      return rest + movePart + 'ay';
    }
  }

  // Rule 2: Starts with one or more consonants
  // Find the index of the first vowel
  let firstVowelIndex = -1;
  for (let i = 0; i < lowerWord.length; i++) {
    if (vowels.includes(lowerWord[i])) {
      firstVowelIndex = i;
      break;
    }
  }

  if (firstVowelIndex === -1) {
    // No vowels found, move whole word? Or just handle as is?
    // Standard Pig Latin usually assumes there is a vowel.
    // If no vowel, we can just return word + 'ay' or handle edge case.
    // Given the rules, this shouldn't happen for standard English words in tests.
    return word + 'ay';
  }

  const movePart = word.substring(0, firstVowelIndex);
  const rest = word.substring(firstVowelIndex);
  return rest + movePart + 'ay';
};
