from functools import wraps


def check_forbidden_records(method):
    @wraps(method)
    def inner(*args, **kwargs):
        if 'another_record' not in kwargs:
            raise AttributeError('method must contain "another_record" attribute')
        grouprecord_object = args[0]
        if kwargs['another_record'] in grouprecord_object.forbidden_group_records.all():
            print('rejected by decorator')
            return False
        else:
            return method(*args, **kwargs)
    return inner


def predicate(method):
    @wraps(method)
    def inner(*args, **kwargs):
        return method(*args, **kwargs)
    inner._is_a_predicate_method = True
    return inner
