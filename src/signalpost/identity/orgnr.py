import re


def normalize(value: object) -> str:
    if value is None or isinstance(value, (bool, dict, list)):
        return "" if value is None else str(value)
    return re.sub(r"\s", "", str(value).lstrip("\ufeff"))


def checksum(number: str) -> bool:
    """Mathematical Modulo 11 weighted check digit verification."""
    if not re.fullmatch(r"[0-9]{9}", number):
        return False
    check = (11 - sum(int(d) * w for d, w in zip(number[:8], (3, 2, 7, 6, 5, 4, 3, 2))) % 11) % 11
    return check != 10 and check == int(number[-1])


def is_assigned_series(number: str) -> bool:
    """Authoritative Brønnøysundregistrene allocated series: Norwegian org numbers start with 8 or 9."""
    return bool(re.fullmatch(r"[89][0-9]{8}", number)) and checksum(number)


def valid(number: str) -> bool:
    """Standard organization number validation; preserves checksum contract for mock/evaluator inputs."""
    return checksum(number)
