from sqlite3 import Connection, OperationalError
import time

class DB(Connection):
    def __init__(self, *args, retries=5, delay=0.1, **kwargs):
        super().__init__(*args, **kwargs)

        # _var for private thingy variable
        self._retries = retries
        self._delay = delay

    def execute(self, sql, parameters=()):
        return self._retry(super().execute, sql, parameters)

    def commit(self):
        return self._retry(super().commit)

    def _retry(self, func, *args, **kwargs):
        # _ for unused variable
        for _ in range(self._retries):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if 'database is locked' in str(e):
                    time.sleep(self._delay)
                else:
                    raise

        raise OperationalError(f'Max retries reached ({self._retries} time(s)): database is locked')
