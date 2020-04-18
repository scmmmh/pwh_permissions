def tokenise(expression):
    """Tokenise the ``expression``, splitting on spaces and brackets."""
    tokens = []
    buffer = []
    for char in expression:
        if char in [' ', '(', ')']:
            if buffer:
                tokens.append(''.join(buffer).strip())
                buffer = []
        buffer.append(char)
        if char in ['(', ')']:
            tokens.append(''.join(buffer).strip())
            buffer = []
    if buffer:
        tokens.append(''.join(buffer).strip())
    return [token for token in tokens if token.strip()]


def parse(tokens):
    """Parses the infix permission ``tokens`` into a postfix instruction list."""
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
    """Evaluate the ``instructions``, substituting values from ``values``."""
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
