import platform


def available_systems(systems):
    def decorator(test_function):
        def wrapper(*args, **kwargs):
            if platform.system() == "Linux" and "linux" not in systems:
                print(  # noqa: T201
                    "warning: "
                    "skipping the test because it is not supported on Linux."
                )
                return
            test_function(*args, **kwargs)
            return

        return wrapper

    return decorator
