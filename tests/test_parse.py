from pwh_permissions import tokenise, parse

def test_basic_parse():
    instructions = parse(tokenise('$obj allow $user "edit"'))
    assert len(instructions) == 1
    assert instructions == [('$obj', 'allow', '$user', '"edit"')]


def test_combined_parse():
    instructions = parse(tokenise('$obj allow $user "edit" or $obj has_permission "admin"'))
    assert len(instructions) == 3
    assert instructions == [('$obj', 'allow', '$user', '"edit"'), ('$obj', 'has_permission', '"admin"'), 'or']


def test_bracket_parse():
    instructions = parse(tokenise('$obj allow $user "edit" and ($obj has_permission "admin" or $obj has_permission "superuser")'))
    print(instructions)
    assert len(instructions) == 5
    assert instructions == [('$obj', 'allow', '$user', '"edit"'), ('$obj', 'has_permission', '"admin"'), ('$obj', 'has_permission', '"superuser"'), 'or', 'and']
