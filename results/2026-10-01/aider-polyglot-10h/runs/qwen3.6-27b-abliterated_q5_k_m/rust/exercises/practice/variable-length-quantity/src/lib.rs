#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    IncompleteNumber,
}

/// Convert a list of numbers to a stream of bytes encoded with variable length encoding.
pub fn to_bytes(values: &[u32]) -> Vec<u8> {
    let mut result = Vec::new();
    for &value in values {
        if value == 0 {
            result.push(0);
            continue;
        }

        let mut buffer = Vec::new();
        let mut v = value;
        while v > 0 {
            buffer.push((v & 0x7F) as u8);
            v >>= 7;
        }

        // The buffer has the chunks in reverse order (LSB first)
        // We need to output them MSB first, with continuation bits set appropriately.
        for (i, byte) in buffer.iter().rev().enumerate() {
            if i < buffer.len() - 1 {
                result.push(byte | 0x80);
            } else {
                result.push(*byte);
            }
        }
    }
    result
}

/// Given a stream of bytes, extract all numbers which are encoded in there.
pub fn from_bytes(bytes: &[u8]) -> Result<Vec<u32>, Error> {
    let mut result = Vec::new();
    let mut current_value: u32 = 0;
    let mut in_sequence = false;

    for &byte in bytes {
        in_sequence = true;
        current_value = (current_value << 7) | (byte & 0x7F) as u32;

        if byte & 0x80 == 0 {
            // End of a number
            result.push(current_value);
            current_value = 0;
            in_sequence = false;
        }
    }

    if in_sequence {
        return Err(Error::IncompleteNumber);
    }

    Ok(result)
}
