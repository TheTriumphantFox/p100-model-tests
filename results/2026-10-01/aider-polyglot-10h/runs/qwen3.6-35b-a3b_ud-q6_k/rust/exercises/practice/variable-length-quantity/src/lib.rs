#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    IncompleteNumber,
}

/// Convert a list of numbers to a stream of bytes encoded with variable length encoding.
pub fn to_bytes(values: &[u32]) -> Vec<u8> {
    let mut bytes = Vec::new();
    for &value in values {
        if value == 0 {
            bytes.push(0);
            continue;
        }

        let mut chunks = Vec::new();
        let mut v = value;
        while v > 0 {
            chunks.push((v & 0x7F) as u8);
            v >>= 7;
        }

        while let Some(chunk) = chunks.pop() {
            if !chunks.is_empty() {
                bytes.push(chunk | 0x80);
            } else {
                bytes.push(chunk);
            }
        }
    }
    bytes
}

/// Given a stream of bytes, extract all numbers which are encoded in there.
pub fn from_bytes(bytes: &[u8]) -> Result<Vec<u32>, Error> {
    let mut numbers = Vec::new();
    let mut accumulator: u32 = 0;
    let mut incomplete = false;

    for &byte in bytes {
        incomplete = true;
        accumulator = (accumulator << 7) | (byte as u32 & 0x7F);

        if byte & 0x80 == 0 {
            numbers.push(accumulator);
            accumulator = 0;
            incomplete = false;
        }
    }

    if incomplete {
        return Err(Error::IncompleteNumber);
    }

    Ok(numbers)
}
