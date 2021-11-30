def dirname(path: str) -> str:
    return "/".join(path.split("/")[:-1])


def filename(path: str) -> str:
    return path.split("/")[-1]
