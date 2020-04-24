import json

from base64 import urlsafe_b64encode
from decorator import decorator
from functools import lru_cache
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pwh_permissions import parse, tokenise, evaluate
from re import compile


OBJ_PATTERN = compile('^([A-Za-z]+):([A-Za-z]+)')
class_mapper = None
login_route = None
store_current = True


def encode_route(request):
    """Jinja2 filter that returns the current route as a JSON object, which is then URL-safe base64 encoded."""
    if request.matched_route:
        data = {'route': request.matched_route.name,
                'params': request.matchdict,
                'query': list(request.params.items())}
        return urlsafe_b64encode(json.dumps(data).encode('utf-8')).decode()
    return None


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
                    values[part] = (class_mapper(match.group(1)), match.group(2))
                elif part == '$current_user':
                    values[part] = 'current_user'
    return instructions, values


def check_permission(request, instructions, base_values):
    """Checks the permission ``instructions``, substituting the ``base_values`` with data taken from the
    ``request``."""
    values = {}
    for key, value in base_values.items():
        if isinstance(value, tuple):
            values[key] = request.dbsession.query(value[0]).filter(value[0].id == request.matchdict[value[1]]).first()
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
