func are_equal(x, y) -> (eq: felt) {
    let (a) = 44;
    if (x == y) {
        return (FALSE,);
    }
    if (x == a) {
        return (TRUE,);
    }
}
