import sqlite3
import os

from hashlib import sha512


def create_storage(storage_path: str, key: bytes):
    if not os.path.exists(storage_path):
        os.mkdir(storage_path)

    with open(file=os.path.join(storage_path, "key"), mode="wb") as file:
        file.write(sha512(key).digest())

    storage = sqlite3.connect(database=os.path.join(storage_path, "storage"))
    cursor = storage.cursor()
    cursor.execute(
        """
        CREATE TABLE passwords (
            id INTEGER PRIMARY KEY,
            assignment TEXT,
            encrypted BLOB,
            nonce BLOB,
            tag BLOB
        );
        """
    )


class Storage:
    def __init__(self, storage_path: str, key_hash: bytes):
        with open(os.path.join(storage_path, "key"), "rb") as file:
            first_key_hash = file.read()

        if key_hash != first_key_hash:
            raise ValueError("Invalid key")

        self.storage = sqlite3.connect(database=os.path.join(storage_path, "storage"))
        self.cursor = self.storage.cursor()

    def add_password(self, assignment: str, encrypted: bytes, nonce: bytes, tag: bytes):
        self.cursor.execute(
            """
            INSERT INTO passwords (assignment, encrypted, nonce, tag) VALUES (?, ?, ?, ?);
            """,
            (assignment, encrypted, nonce, tag)
        )
        self.storage.commit()

    def remove_password(self, id_: int):
        self.cursor.execute(
            """
            DELETE FROM passwords WHERE id = ?;
            """,
            (id_,)
        )
        self.storage.commit()

    def list_passwords(self) -> list[bytes]:
        self.cursor.execute(
            """
            SELECT * FROM passwords;
            """
        )
        self.storage.commit()
        return self.cursor.fetchall()
