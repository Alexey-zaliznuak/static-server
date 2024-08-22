import re


UUID_REGEX = re.compile(
    r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$"
)


def is_uuid(slug: str) -> bool:
    return bool(UUID_REGEX.match(slug))
