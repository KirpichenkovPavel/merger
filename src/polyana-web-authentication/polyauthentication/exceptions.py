class PolyAuthenticationException(Exception):
    pass


class NoUserInNSI(PolyAuthenticationException):
    pass


class NoEmployeeID(PolyAuthenticationException):
    pass


class EmployeeIDConflict(PolyAuthenticationException):
    pass