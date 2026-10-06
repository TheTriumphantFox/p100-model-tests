#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    IncompleteNumber,
}

/// Convert a list of numbers to a stream of bytes encoded with variable length encoding.
pub fn to_bytes(values: &[u32]) -> Vec<u8> {
    let mut result = Vec::new();
    for &value in values {
        let mut bytes = Vec::new();
        let mut val = value;
        loop {
            let mut byte = (val & 0x7F) as u8;
            val >>= 7;
            if val != 0 {
                byte |= 0x80;
            }
            bytes.push(byte);
            if val == 0 {
                break;
            }
        }
        // The bytes were collected in reverse order (LSB first), so we reverse them to get MSB first
        bytes.reverse();
        result.extend_from_slice(&bytes);
    }
    result
}

/// Given a stream of bytes, extract all numbers which are encoded in there.
pub fn from_bytes(bytes: &[u8]) -> Result<Vec<u32>, Error> {
    let mut result = Vec::new();
    let mut current: u32 = 0;
    let mut has_continuation = false;

    for &byte in bytes {
        let data = (byte & 0x7F) as u32;
        current = (current << 7) | data;
        if byte & 0x80 != 0 {
            has_continuation = true;
        } else {
            result.push(current);
            current = 0;
            has_continuation = false;
        }
    }

    if has_continuation {
        Err(Error::IncompleteNumber)
    } else {
        Ok(result)
    }
}
