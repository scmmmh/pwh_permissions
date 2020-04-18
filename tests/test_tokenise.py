from pwh_permissions import tokenise


def test_basic_tokenise():
    tokens = tokenise('obj allow user edit')
    assert len(tokens) == 4
    assert tokens == ['obj', 'allow', 'user', 'edit']


def test_combined_tokenise():
    tokens = tokenise('obj allow user edit or user has_role admin')
    assert len(tokens) == 8
    assert tokens == ['obj', 'allow', 'user', 'edit', 'or', 'user', 'has_role', 'admin']


def test_bracket_tokenise():
    tokens = tokenise('obj allow user edit and (user has_role admin or user has_role superuser)')
    assert len(tokens) == 14
    assert tokens == ['obj', 'allow', 'user', 'edit', 'and', '(', 'user', 'has_role', 'admin', 'or', 'user',
                      'has_role', 'superuser', ')']
