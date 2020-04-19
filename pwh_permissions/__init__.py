"""A simple permission parsing library.

The main function for permission checking is :func:`pwh_permissions.permitted`.
"""
import re


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
            while stack[-1] != '(':
                result.append(stack.pop())
            stack.pop()
        else:
            buffer.append(token)
    if buffer:
        result.append(tuple(buffer))
    while stack:
        result.append(stack.pop())
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
    stack = []
    for instruction in instructions:
        if isinstance(instruction, tuple):
            obj = values[instruction[0]]
            attr = getattr(obj, instruction[1])
            params = [values[param] if param in values else param for param in instruction[2:]]
            stack.append(attr(*params) is True)
        else:
            a = stack.pop()
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
