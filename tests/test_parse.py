from pwh_permissions import tokenise, parse


def test_basic_parse():
    instructions = parse(tokenise('obj allow user edit'))
    assert len(instructions) == 1
    assert instructions == [('obj', 'allow', 'user', 'edit')]


def test_combined_parse():
    instructions = parse(tokenise('obj allow user edit or user has_role admin'))
    assert len(instructions) == 3
    assert instructions == [('obj', 'allow', 'user', 'edit'), ('user', 'has_role', 'admin'), 'or']


def test_bracket_parse():
    instructions = parse(tokenise('obj allow user edit and (user has_role admin or user has_role ' +
                                  'superuser)'))
    assert len(instructions) == 5
    assert instructions == [('obj', 'allow', 'user', 'edit'), ('user', 'has_role', 'admin'),
                            ('user', 'has_role', 'superuser'), 'or', 'and']
