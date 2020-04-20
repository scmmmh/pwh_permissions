import pytest

from pwh_permissions import tokenise, parse, PermissionException


def test_empty_parse():
    """Test parsing an empty expression."""
    instructions = parse(tokenise(''))
    assert len(instructions) == 0


def test_basic_parse():
    """Test parsing a basic expression."""
    instructions = parse(tokenise('obj allow user edit'))
    assert len(instructions) == 1
    assert instructions == [('obj', 'allow', 'user', 'edit')]


def test_combined_parse():
    """Test parsing an expression that contains an operator."""
    instructions = parse(tokenise('obj allow user edit or user has_role admin'))
    assert len(instructions) == 3
    assert instructions == [('obj', 'allow', 'user', 'edit'), ('user', 'has_role', 'admin'), 'or']
    instructions = parse(tokenise('obj allow user edit and user has_role admin'))
    assert len(instructions) == 3
    assert instructions == [('obj', 'allow', 'user', 'edit'), ('user', 'has_role', 'admin'), 'and']


def test_bracket_parse():
    """Test parsing an expression that contains a bracket."""
    instructions = parse(tokenise('obj allow user edit and (user has_role admin or user has_role ' +
                                  'superuser)'))
    assert len(instructions) == 5
    assert instructions == [('obj', 'allow', 'user', 'edit'), ('user', 'has_role', 'admin'),
                            ('user', 'has_role', 'superuser'), 'or', 'and']


def test_invalid_parse_missing_opening_bracket():
    """Test exception handling for missing or too few opening brackets."""
    with pytest.raises(PermissionException) as exc_info:
        parse(tokenise('obj allow user edit )'))
    assert exc_info.value.message == 'Too many closing brackets'
    with pytest.raises(PermissionException) as exc_info:
        parse(tokenise('obj allow user edit and (obj has_role admin))'))
    assert exc_info.value.message == 'Too many closing brackets'


def test_invalid_parse_missing_closing_bracket():
    """Test exception handling for missing closing brackets."""
    with pytest.raises(PermissionException) as exc_info:
        parse(tokenise('obj allow user edit and (user has_role admin'))
    assert exc_info.value.message == 'Missing closing bracket'
