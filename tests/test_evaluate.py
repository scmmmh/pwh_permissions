from pwh_permissions import tokenise, parse, evaluate


class ExampleObject(object):

    def allow(self, user, action):
        """Checks whether the given user is allowed the action. The "view" action is always allowed, the "edit" action
        only if the is_allowed flag is set on the user."""
        if action == 'view':
            return True
        elif action == 'edit':
            if user.is_allowed:
                return True
            else:
                return False


class ExampleUser(object):
    """A configurable example user that has an is_allowed marker and a role."""

    def __init__(self, is_allowed, role):
        self.is_allowed = is_allowed
        self.role = role

    def has_role(self, role):
        """Test whether the initialised role is the same as the role parameter."""
        if role == self.role:
            return True
        else:
            return False


def test_basic_evaluate():
    """Test evaluating a basic single expression."""
    instructions = parse(tokenise('obj allow user edit'))
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'admin')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'admin')})
    assert result is False


def test_or_evalute():
    """Test evaluating two expressions joined by or."""
    instructions = parse(tokenise('obj allow user edit or user has_role admin'))
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'admin')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'admin')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'superuser')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'superuser')})
    assert result is False


def test_and_evalute():
    """Test evaluating two expressions joined by and."""
    instructions = parse(tokenise('obj allow user edit and user has_role admin'))
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'admin')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'admin')})
    assert result is False
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'superuser')})
    assert result is False
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'superuser')})
    assert result is False


def test_and_or_evaluate():
    """Test evaluating three expressions joined by and and or."""
    instructions = parse(tokenise('obj allow user edit and user has_role admin or user has_role superuser'))
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'admin')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'admin')})
    assert result is False
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'superuser')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'superuser')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'nobody')})
    assert result is False


def test_bracket_evaluate():
    """Test evaluating three expressions in a complex structure using a bracket."""
    instructions = parse(tokenise('obj allow user edit and (user has_role admin or user has_role superuser)'))
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'admin')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(True, 'superuser')})
    assert result
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'admin')})
    assert result is False
    result = evaluate(instructions, {'obj': ExampleObject(),
                                     'user': ExampleUser(False, 'superuser')})
    assert result is False
