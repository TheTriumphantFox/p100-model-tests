/// What should the type of _function be?
pub fn map<T, F>(input: Vec<T>, _function: F) -> Vec<T>
where
    F: Fn(T) -> T,
{
    let mut result = Vec::with_capacity(input.len());
    for item in input {
        result.push(_function(item));
    }
    result
}
