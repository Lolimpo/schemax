from typing import List

BoolProps: List[str] = ["value"]
IntProps: List[str] = ["value", "min", "max"]
FloatProps: List[str] = ["value", "min", "max"]
StrProps: List[str] = ["value", "pattern", "len", "min_len", "max_len", "alphabet", "substr"]
ListProps: List[str] = ["len", "min_len", "max_len", "type", "elements"]
DictProps: List[str] = ["keys"]
AnyProps: List[str] = ["types"]
ConstProps: List[str] = ["value"]
