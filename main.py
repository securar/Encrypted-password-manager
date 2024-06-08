import os

import click
import printer

from sys import platform
from getpass import getpass
from cipher import encrypt, decrypt, generate_key, available_length
from storage import Storage, create_storage
from hashlib import md5, sha512
from datetime import datetime


@click.group()
def cli():
    pass


@click.command(name="generate-key")
@click.option("--length", default=32, help="Key length in bytes")
def handle_generate_key(length: int) -> None:
    if length not in available_length:
        printer.error("The key length can be only 16, 24 and 32 bytes")
        exit()

    filename = f"key-{md5(str(datetime.now()).encode()).hexdigest()}"
    with open(filename, "wb") as file:
        file.write(generate_key(key_length=length))

    printer.caution(
        "ATTENTION: Keep this key in a safe place.\n"
        "If you lose it, you will lose access to the storage too.\n"
    )
    printer.success(f"Key successfully saved to file {filename}")


@click.command(name="create-storage")
@click.option("--storage-path", help="Path to the storage folder")
def handle_create_storage(storage_path: str):
    if not storage_path:
        printer.error("Invalid arguments, --help for more")
        exit()

    key = getpass("Enter access key: ")
    create_storage(storage_path, key.encode())
    printer.success(f"Storage {storage_path} created successfully")


@click.command(name="add-password")
@click.option("--storage", help="Path to the storage")
def handle_add_password(storage: str):
    if not storage:
        printer.error("Invalid arguments, --help for more")
        exit()
    printer.info(f"Storage: {storage}")
    printer.info("Emergency exit: Ctrl + C\n")

    key = getpass("Enter access key: ")
    key_hash = sha512(key.encode()).digest()
    try:
        storage = Storage(storage_path=storage, key_hash=key_hash)
    except ValueError:
        del key
        printer.error("Invalid key")
        exit()
    except FileNotFoundError:
        printer.error("Storage not found\n")

    assignment = input("Enter password's assignment: ")
    password = getpass("Enter password: ")

    encrypted, nonce, tag = encrypt(key=key.encode(), data=password.encode())
    del key
    storage.add_password(assignment=assignment, encrypted=encrypted, nonce=nonce, tag=tag)
    printer.success("Password added successfully")


@click.command(name="list-passwords")
@click.option("--storage", help="Path to the storage")
def handle_list_password(storage: str):
    if not storage:
        printer.error("Invalid arguments, --help for more")
        exit()
    printer.info(f"Storage: {storage}")
    printer.info("Emergency exit: Ctrl + C\n")

    key = getpass("Enter access key: ")
    key_hash = sha512(key.encode()).digest()
    try:
        storage = Storage(storage_path=storage, key_hash=key_hash)
    except ValueError:
        del key
        printer.error("Invalid key")
        exit()
    except FileNotFoundError:
        printer.error("Storage not found\n")

    passwords = storage.list_passwords()
    decrypted_passwords: list[tuple] = []
    for id_, assignment, encrypted, nonce, tag in passwords:
        try:
            decrypted = decrypt(key=key.encode(), encrypted=encrypted, nonce=nonce, tag=tag)
            decrypted_passwords.append((id_, assignment, decrypted))
        except ValueError:
            printer.error("Invalid key or data corrupted")

    result = "\nid, assignment, password\n"
    for id_, assignment, decrypted in decrypted_passwords:
        result += f"{id_}, {assignment}, {decrypted.decode()}\n"

    printer.success(result)


@click.command(name="remove-password")
@click.option("--storage", help="Path to the storage")
@click.option("--id", type=int, help="Password's id to remove")
def handle_remove_password(id: int, storage: str):
    if not id:
        printer.error("Invalid arguments, --help for more")
        exit()
    printer.info(f"Storage: {storage}")
    printer.info("Emergency exit: Ctrl + C\n")

    key = getpass("Enter access key: ")
    key_hash = sha512(key.encode()).digest()
    try:
        storage = Storage(storage_path=storage, key_hash=key_hash)
    except ValueError:
        del key
        printer.error("Invalid key")
        exit()
    except FileNotFoundError:
        printer.error("Storage not found\n")

    del key
    storage.remove_password(id_=id)
    printer.success("Password removed successfully")


if __name__ == '__main__':
    if platform != "linux":
        printer.error("This program works only on linux systems")
        exit()
    try:
        cli.add_command(handle_generate_key)
        cli.add_command(handle_create_storage)
        cli.add_command(handle_add_password)
        cli.add_command(handle_list_password)
        cli.add_command(handle_remove_password)
        cli()
    except KeyboardInterrupt:
        os.system("clear")
        printer.error("Aborted!\n")
