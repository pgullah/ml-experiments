
def lazy_init(scope, variable_name, init_func):
    if not hasattr(scope, variable_name):
        setattr(scope, variable_name, init_func())

    return getattr(scope, variable_name)