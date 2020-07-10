from decorator import decorator
from functools import lru_cache
from pwh_pyramid_routes import encode_route
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pwh_permissions import parse, tokenise, evaluate
from re import compile


OBJ_PATTERN = compile('^([A-Za-z]+):([A-Za-z_0-9]+)(?::([A-Za-z]+))?')
class_mapper = None
login_route = None
store_current = True


@lru_cache()
def process_permission(permission):
    """Process the ``permission``, return the instructions and substitution values."""
    instructions = parse(tokenise(permission))
    values = {}
    for instruction in instructions:
        if isinstance(instruction, tuple):
            for part in instruction:
                match = OBJ_PATTERN.match(part)
                if match:
                    if match.group(3) is None:
                        values[part] = (class_mapper(match.group(1)), 'id', match.group(2))
                    else:
                        values[part] = (class_mapper(match.group(1)), match.group(2), match.group(3))
                elif part == '$current_user':
                    values[part] = 'current_user'
    return instructions, values


def check_permission(request, instructions, base_values):
    """Checks the permission ``instructions``, substituting the ``base_values`` with data taken from the
    ``request``."""
    values = {}
    for key, value in base_values.items():
        if isinstance(value, tuple):
            values[key] = request.dbsession.query(value[0]).filter(getattr(value[0], value[1]) == request.matchdict[value[2]]).first()
        elif value == 'current_user':
            values[key] = request.current_user
    return evaluate(instructions, values)


def permitted(request, permission):
    """Jinja2 filter that checks if the current user has a specific permission."""
    return check_permission(request, *process_permission(permission))


def require_permission(permission):
    """Pyramid decorator to check permissions for a request."""
    instructions, values = process_permission(permission)

    def handler(f, *args, **kwargs):
        request = args[0]
        if check_permission(request, instructions, values):
            return f(*args, **kwargs)
        elif request.current_user:
            raise HTTPForbidden()
        elif login_route:
            if store_current:
                raise HTTPFound(request.route_url(login_route, _query={'redirect': encode_route(request)}))
            else:
                raise HTTPFound(request.route_url(login_route))
        else:
            raise HTTPForbidden()
    return decorator(handler)


def includeme(config):
    """Inject the filters into the configuration."""
    global login_route, store_current, class_mapper
    settings = config.get_settings()
    login_route = settings['pwh.permissions.login_route']
    class_mapper = settings['pwh.permissions.class_mapper']
    if 'pwh.permissions.store_current' in settings and \
            settings['pwh.permissions.store_current'].lower() == 'false':
        store_current = False

    config.get_jinja2_environment().filters['permitted'] = permitted
