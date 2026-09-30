from typing import Protocol, Any


class Memoizer(Protocol):
    """
    A protocol for a memoization mechanism.
    This library uses a recursive algorithm while converting specifications into schemas.
    There are specifications that contain a lot of the same structures,
    not exactly recursively but very deeply nested.
    Conversion for such specifications can take a LOT of time, because the same structures
    are being converted over and over again. Memoization is there to mitigate that.
    A memoizer must implement some kind of a key-value storage mechanism under the hood.
    """

    def add(self, key: str, obj: dict[str, Any]) -> None:
        """Store an object under the given key"""
        ...

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve an object under the given key or return None"""
        ...


class NoopMemoizer(Memoizer):
    """Memoizer that does nothing, effectively turning memoization off"""

    def add(self, key: str, obj: dict[str, Any]) -> None:
        pass

    def get(self, key: str) -> dict[str, Any] | None:
        return None
