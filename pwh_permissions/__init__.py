def tokenise(expression):
    """Tokenise the expression, splitting on spaces and brackets."""
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
