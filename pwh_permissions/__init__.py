"""A simple permission parsing library.

The main function for permission checking is :func:`pwh_permissions.permitted`.

The permission language is structured as follows:

.. sourcecode:: ebnf

  EXPRESSION := CALL | EXPRESSION , OPERATOR , EXPRESSION | "(" , EXPRESSION , ")" | "True" | "False"
  OPERATOR := "and" | "or"
  CALL := CLASS | CLASS , FUNCTION | CLASS , FUNCTION , PARAMLIST
  PARAMLIST : = PARAM | PARAM , PARAMLIST
  CLASS := VALUE
  FUNCTION := VALUE
  PARAM := VALUE
  VALUE := CHAR | CHAR , VALUE
  CHAR := "a-z" | "A-Z" | "0-9"

Examples::

  page allow user edit

  page allow user edit or user has_permission admin

  user is_logged_in and (page allow user edit or page owned_by user)
"""
import re

from inspect import signature


class PermissionException(Exception):
    """Exception indicating an error in either the definition of the permission expression or its execution."""

    def __init__(self, message):
        self.message = message


def convert_token(token):
    """Convert the token into a bool value or a numeric value, if it is one.

    If the value is ``'True'`` or ``'False'``, then the matching ``bool`` value is returned.

    If the value matches the regular expression ``'^[0-9]+$'``, then it is converted to an ``int`` value.

    All other values are returned as-is.

    :param token: The token to convert
    :type token: ``str``
    :return: The converted token
    :rtype: ``bool``, ``int``, or ``str``
    """
    if token == 'True':
        return True
    elif token == 'False':
        return False
    elif re.match('^[0-9]+$', token):
        return int(token)
    else:
        return token


def tokenise(expression):
    """Tokenise the ``expression``, splitting on spaces and brackets.

    :param expression: The permission expression to tokenise
    :type token: ``str``
    :return: The tokenised expression
    :rtype: ``list``
    """
    tokens = []
    buffer = []
    for char in expression:
        if char in [' ', '(', ')']:
            if buffer:
                tokens.append(convert_token(''.join(buffer).strip()))
                buffer = []
        buffer.append(char)
        if char in ['(', ')']:
            tokens.append(convert_token(''.join(buffer).strip()))
            buffer = []
    if buffer:
        tokens.append(convert_token(''.join(buffer).strip()))
    return [token for token in tokens if token.strip()]


def parse(tokens):
    """Parses the infix permission ``tokens`` into a postfix instruction list.

    :param tokens: The token list produced by :func:`~pwh_permissions.tokenise`
    :type tokens: ``list``
    :return: The token list in postfix notation
    :rtype: ``list``
    """
    result = []
    stack = []
    buffer = []
    for token in tokens:
        if token in ['and', 'or', '(']:
            if buffer:
                result.append(tuple(buffer))
                buffer = []
            if len(stack) > 0:
                if token != '(' and stack[-1] in ['and', 'or']:
                    result.append(stack.pop())
            stack.append(token)
        elif token == ')':
            if buffer:
                result.append(tuple(buffer))
                buffer = []
            if len(stack) == 0:
                raise PermissionException('Too many closing brackets')
            while stack[-1] != '(':
                result.append(stack.pop())
                if len(stack) == 0:
                    raise PermissionException('Too many closing brackets')
            stack.pop()
        else:
            buffer.append(token)
    if buffer:
        result.append(tuple(buffer))
    while stack:
        tmp = stack.pop()
        if tmp == '(':
            raise PermissionException('Missing closing bracket')
        result.append(tmp)
    return result


def evaluate(instructions, values):
    """Evaluate the ``instructions``, substituting values from ``values``.

    :param instructions: The postfix instruction list produced by :func:`~pwh_permissions.parse`
    :type instructions: ``list``
    :param values: The values to substitute into the ``instructions`` when evaluating
    :type values: ``dict``
    :return: The result of evaluating the ``instructions``
    :rtype: ``bool``
    """
    if not instructions:
        return False
    stack = []
    for instruction in instructions:
        if isinstance(instruction, tuple):
            if instruction[0] not in values:
                raise PermissionException('Object "{0}" not found in the values'.format(instruction[0]))
            obj = values[instruction[0]]
            if not obj:
                stack.append(False)
            else:
                if not hasattr(obj, instruction[1]):
                    raise PermissionException('Object "{0}" has no method "{1}"'.format(instruction[0], instruction[1]))
                attr = getattr(obj, instruction[1])
                params = [values[param] if param in values else param for param in instruction[2:]]
                try:
                    stack.append(attr(*params) is True)
                except TypeError:
                    sig = signature(attr)
                    min_count = len([param for param in sig.parameters.values() if param.default == param.empty])
                    max_count = len(sig.parameters)
                    if len(params) < min_count:
                        raise PermissionException('Too few parameters for method "{0}" on "{1}"'.format(
                            instruction[1],
                            instruction[0],
                        ))
                    elif len(params) > max_count:
                        raise PermissionException('Too many parameters for method "{0}" on "{1}"'.format(
                            instruction[1],
                            instruction[0],
                        ))
        else:
            if len(stack) == 0:
                raise PermissionException('Missing expression for boolean operator')
            a = stack.pop()
            if len(stack) == 0:
                raise PermissionException('Missing expression for boolean operator')
            b = stack.pop()
            if instruction == 'and':
                stack.append(a and b)
            elif instruction == 'or':
                stack.append(a or b)
    return stack.pop()


def permitted(expression, values):
    """Evaluate the ``expression``, substituting values from ``values``.

    :param expression: The expression to check
    :type instructions: ``str``
    :param values: The values to substitute into the ``instructions`` when evaluating
    :type values: ``dict``
    :return: The result of evaluating the ``expression``
    :rtype: ``bool``
    """
    return evaluate(parse(tokenise(expression)), values)
