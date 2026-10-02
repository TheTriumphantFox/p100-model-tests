//
// This is only a SKELETON file for the 'Pig Latin' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const translate = (text) => {
  return text.split(' ').map(translateWord).join(' ');
};

const translateWord = (word) => {
  // Rule 1: Starts with vowel sound (vowel, xr, yt)
  if (/^([aeiou]|xr|yt)/.test(word)) {
    return word + 'ay';
  }

  // Rule 4: Starts with consonant(s) followed by y
  // 'y' acts as a vowel if it's not the first letter.
  // We look for consonants followed by y.
  const matchY = word.match(/^([^aeiou]+)y(.*)/);
  if (matchY) {
    const prefix = matchY[1];
    const rest = matchY[2];
    return 'y' + rest + prefix + 'ay';
  }

  // Rule 3: Starts with consonant(s) + qu
  // We check for consonants followed by qu. The split point is after 'qu'.
  const matchQu = word.match(/^([^aeiou]*qu)(.*)/);
  if (matchQu) {
    const prefix = matchQu[1];
    const rest = matchQu[2];
    return rest + prefix + 'ay';
  }

  // Rule 2: Starts with consonant cluster
  // Matches one or more consonants at the start.
  const matchConsonants = word.match(/^([^aeiou]+)(.*)/);
  if (matchConsonants) {
    const prefix = matchConsonants[1];
    const rest = matchConsonants[2];
    return rest + prefix + 'ay';
  }

  return word;
};
