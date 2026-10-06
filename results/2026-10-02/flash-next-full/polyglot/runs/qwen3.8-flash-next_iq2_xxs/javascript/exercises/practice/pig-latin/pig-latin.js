//
// This is only a SKELETON file for the 'Pig Latin' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

const VOWELS = ['a', 'e', 'i', 'o', 'u'];

const translateWord = (word) => {
  // Rule 1: If a word begins with a vowel, or starts with "xr" or "yt", add an "ay" sound to the end of the word.
  if (VOWELS.includes(word[0]) || word.startsWith('xr') || word.startsWith('yt')) {
    return word + 'ay';
  }

  // Rule 3: If a word starts with zero or more consonants followed by "qu", first move those consonants (if any) and the "qu" part to the end of the word, and then add an "ay" sound to the end of the word.
  const quIndex = word.indexOf('qu');
  if (quIndex !== -1 && VOWELS.includes(word[quIndex + 1])) {
    // Check if everything before 'qu' is consonants (which is implied by finding the first 'qu' in a consonant-starting word)
    // Actually, simpler check: if it starts with consonants and has 'qu' before any vowel
    let prefixEnd = quIndex + 2;
    // Ensure all chars before 'qu' are consonants (they are, since we found the first 'qu' and word starts with consonant)
    // But we must ensure there are no vowels before 'qu'
    let hasVowelBefore = false;
    for (let i = 0; i < quIndex; i++) {
      if (VOWELS.includes(word[i])) {
        hasVowelBefore = true;
        break;
      }
    }
    if (!hasVowelBefore) {
      return word.slice(prefixEnd) + word.slice(0, prefixEnd) + 'ay';
    }
  }

  // Rule 4: If a word starts with one or more consonants followed by "y", first move the consonants preceding the "y" to the end of the word, and then add an "ay" sound to the end of the word.
  const yIndex = word.indexOf('y');
  if (yIndex > 0) {
    // Check if all chars before 'y' are consonants
    let allConsonantsBefore = true;
    for (let i = 0; i < yIndex; i++) {
      if (VOWELS.includes(word[i])) {
        allConsonantsBefore = false;
        break;
      }
    }
    if (allConsonantsBefore) {
      return word.slice(yIndex) + word.slice(0, yIndex) + 'ay';
    }
  }

  // Rule 2: If a word begins with one or more consonants, first move those consonants to the end of the word and then add an "ay" sound to the end of the word.
  // Find the first vowel
  let firstVowelIndex = -1;
  for (let i = 0; i < word.length; i++) {
    if (VOWELS.includes(word[i])) {
      firstVowelIndex = i;
      break;
    }
  }

  if (firstVowelIndex > 0) {
    return word.slice(firstVowelIndex) + word.slice(0, firstVowelIndex) + 'ay';
  }

  // Fallback (should not happen if rules are exhaustive for valid inputs)
  return word + 'ay';
};

export const translate = (text) => {
  return text
    .split(' ')
    .map(translateWord)
    .join(' ');
};
