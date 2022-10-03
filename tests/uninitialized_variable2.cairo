func bar() -> (res: felt) {
    alloc_locals;
    local x;
    local xx;
    %{ ids.xx = 3 %}
    return (res=x);
}
