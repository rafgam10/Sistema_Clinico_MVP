import firebird.driver as fdb
from dotenv import load_dotenv
import os

load_dotenv()

class ConnectionDBFireBird:
    
    def __init__(self):
        self.host = os.getenv("FIREBIRD_HOST")
        self.port = int(os.getenv("FIREBIRD_PORT", 3050))
        self.database = os.getenv("FIREBIRD_DATABASE")
        self.user = os.getenv("FIREBIRD_USER")
        self.password = os.getenv("FIREBIRD_PASSWORD")
        self.charset = os.getenv("FIREBIRD_CHARSET", "WIN1252")
        self._connection = None
        self._connect()

    def _connect(self):
        database_url = f"{self.host}/{self.port}:{self.database}"

        # print("Conectando no Firebird:", database_url)
        # print("Charset:", self.charset)

        self._connection = fdb.connect(
            database_url,
            user=self.user,
            password=self.password,
            charset=self.charset
        )

    def cursor(self):
        return self._connection.cursor()

    def close(self):
        if self._connection:
            self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        

