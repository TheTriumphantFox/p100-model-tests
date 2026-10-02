/// Apply a function to each element of the input vector and return a new vector
/// containing the results.
///
/// # Examples
///
/// ```
/// let input = vec![1, 2, 3, 4, 5];
/// let squares = map(input, |x| x * x);
/// assert_eq!(squares, vec![1, 4, 9, 16, 25]);
/// ```
pub fn map<T, U, F>(input: Vec<T>, function: F) -> Vec<U>
where
    F: Fn(T) -> U,
{
    // Create a new vector with the same capacity as the input to avoid reallocations.
    let mut result = Vec::with_capacity(input.len());
    for value in input {
        result.push(function(value));
    }
    result
}
