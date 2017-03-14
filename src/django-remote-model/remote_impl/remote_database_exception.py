from django.db.utils import DatabaseError


class RemoteDatabaseError(DatabaseError):
    ENTITY_EXISTS = 1
    BAD_REQUEST = 2
    ENTITY_NOT_FOUND = 4
    VERSION_MISMATCH = 8
    DATABASE_ERROR = 16
    WEB_APP_ERROR = 32
    QUERY_MALFORMED = 64
    INVALID_AUTH_DATA = 128
    INVALID_URL = 256
    VALIDATION_FAIL = 512
    CONNECTION_FAIL = 1024
    ACCESS_DENIED = 2048
    INTERNAL_SERVER_ERROR = 65535

    def __init__(self, *args, **kwargs):
        self.remote_error_json = kwargs.pop("remote_error_json", None)
        super().__init__(*args, **kwargs)

    @property
    def message(self):
        if self.remote_error_json:
            return self.remote_error_json.get("message")
        else:
            return None

    @property
    def code(self):
        if self.remote_error_json:
            return self.remote_error_json.get("code")
        else:
            return None

    def __str__(self):
        return str(self.remote_error_json)
