#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    IncompleteNumber,
}

/// Convert a list of numbers to a stream of bytes encoded with variable length encoding.
pub fn to_bytes(values: &[u32]) -> Vec<u8> {
    let mut bytes = Vec::new();
    for &value in values {
        let mut groups = Vec::new();
        let mut v = value;
        loop {
            groups.push((v & 0x7f) as u8);
            v >>= 7;
            if v == 0 {
                break;
            }
        }
        // groups is LSB first. We need MSB first.
        groups.reverse();
        
        for (i, g) in groups.iter().enumerate() {
            let mut byte = *g;
            if i != groups.len() - 1 {
                byte |= 0x80;
            }
            bytes.push(byte);
        }
    }
    bytes
}

/// Given a stream of bytes, extract all numbers which are encoded in there.
pub fn from_bytes(bytes: &[u8]) -> Result<Vec<u32>, Error> {
    let mut numbers = Vec::new();
    let mut current = 0u32;
    
    for &byte in bytes {
        current = (current << 7) | (byte & 0x7f) as u32;
        if byte & 0x80 == 0 {
            numbers.push(current);
            current = 0;
        }
    }
    
    // If the last byte had the continuation bit set, the number is incomplete.
    if !bytes.is_empty() && bytes[bytes.len() - 1] & 0x80 != 0 {
        return Err(Error::IncompleteNumber);
    }
    
    Ok(numbers)
}
