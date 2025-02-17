from ._config import Config


def output_warning(message: str) -> None:
    if Config.OUTPUT_FUNCTION is None:
        print(f"Schemax ⚠️:  {message}")
    else:
        Config.OUTPUT_FUNCTION(message)
