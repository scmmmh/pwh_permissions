from pwh_permissions import convert_token


def test_boolean_conversion():
    assert convert_token('True')
    assert convert_token('False') is False


def test_number_conversion():
    assert convert_token('4325') == 4325


def test_mixed_conversion():
    assert convert_token('432a') == '432a'
