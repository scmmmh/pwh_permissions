from pwh_permissions import tokenise

def test_basic_tokenise():
    tokens = tokenise('$obj allow $user "edit"')
    assert len(tokens) == 4
    assert tokens == ['$obj', 'allow', '$user', '"edit"']


def test_combined_tokenise():
    tokens = tokenise('$obj allow $user "edit" or $obj has_permission "admin"')
    assert len(tokens) == 8
    assert tokens == ['$obj', 'allow', '$user', '"edit"', 'or', '$obj', 'has_permission', '"admin"']


def test_bracket_tokenise():
    tokens = tokenise('$obj allow $user "edit" and ($obj has_permission "admin" or $obj has_permission "superuser")')
    assert len(tokens) == 14
    assert tokens == ['$obj', 'allow', '$user', '"edit"', 'and', '(', '$obj', 'has_permission', '"admin"', 'or', '$obj', 'has_permission', '"superuser"', ')']
