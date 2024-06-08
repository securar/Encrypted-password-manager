from colorama import Fore, Style


def success(text: str) -> None:
    print(Fore.GREEN + text + Style.RESET_ALL)


def info(text: str) -> None:
    print(Fore.YELLOW + text + Style.RESET_ALL)


def caution(text: str) -> None:
    print(Fore.RED + text + Style.RESET_ALL)


def error(text: str) -> None:
    print(Fore.RED + text + Style.RESET_ALL)
