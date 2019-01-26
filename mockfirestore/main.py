import operator
from collections import OrderedDict
from functools import reduce
from itertools import islice
from typing import Dict, Any, List, Tuple, NamedTuple, TypeVar, Sequence, Callable

T = TypeVar('T')
KeyValuePair = Tuple[str, Dict[str, Any]]
Document = Dict[str, Any]
Collection = Dict[str, Document]
Store = Dict[str, Collection]

GeoPoint = NamedTuple('GeoPoint', (('latitude', float), ('longitude', float)))


class DocumentSnapshot:
    def __init__(self, doc: Document) -> None:
        self._doc = doc

    @property
    def exists(self) -> bool:
        return self._doc != {}

    def to_dict(self) -> Document:
        return self._doc


class DocumentReference:
    def __init__(self, data: Store, path: List[str]) -> None:
        self._data = data
        self._path = path

    def get(self) -> DocumentSnapshot:
        return DocumentSnapshot(get_by_path(self._data, self._path))

    def set(self, data: Document):
        set_by_path(self._data, self._path, data)

    def update(self, data: Dict[str, Any]):
        get_by_path(self._data, self._path).update(data)

    def collection(self, name) -> 'CollectionReference':
        document = get_by_path(self._data, self._path)
        new_path = self._path + [name]
        if name not in document:
            set_by_path(self._data, new_path, {})
        return CollectionReference(self._data, new_path)


class Query:
    def __init__(self, data: OrderedDict) -> None:
        self._data = data

    @staticmethod
    def from_dict(data: Collection) -> 'Query':
        ordered = OrderedDict(sorted(data.items(), key=lambda t: t[0]))
        return Query(ordered)

    def get(self) -> List[DocumentSnapshot]:
        return [DocumentSnapshot(doc) for doc in self._data.values()]

    def where(self, field: str, op: str, value: Any) -> 'Query':
        compare = self._compare_func(op)
        filtered = {k: v for k, v in self._data.items() if compare(v[field], value)}
        return Query.from_dict(dict(filtered))

    def order_by(self, key: str) -> 'Query':
        sorted_items = sorted(self._data.items(), key=lambda doc: doc[1][key])
        return Query(OrderedDict(sorted_items))

    def limit(self, limit_amount: int) -> 'Query':
        limited = islice(self._data.items(), limit_amount)
        return Query.from_dict(dict(limited))

    def _compare_func(self, op: str) -> Callable[[T, T], bool]:
        if op == '==':
            return lambda x, y: x == y
        elif op == '<':
            return lambda x, y: x < y
        elif op == '<=':
            return lambda x, y: x <= y
        elif op == '>':
            return lambda x, y: x > y
        elif op == '>=':
            return lambda x, y: x >= y


class CollectionReference:
    def __init__(self, data: Store, path: List[str]) -> None:
        self._data = data
        self._path = path

    def document(self, name: str) -> DocumentReference:
        collection = get_by_path(self._data, self._path)
        new_path = self._path + [name]
        if name not in collection:
            set_by_path(self._data, new_path, {})
        return DocumentReference(self._data, new_path)

    def get(self) -> List[DocumentSnapshot]:
        collection = get_by_path(self._data, self._path)
        return Query.from_dict(collection).get()

    def where(self, field: str, op: str, value: Any) -> Query:
        collection = get_by_path(self._data, self._path)
        return Query.from_dict(collection).where(field, op, value)

    def order_by(self, key: str) -> Query:
        collection = get_by_path(self._data, self._path)
        return Query.from_dict(collection).order_by(key)

    def limit(self, limit_amount: int) -> Query:
        collection = get_by_path(self._data, self._path)
        return Query.from_dict(collection).limit(limit_amount)


class MockFirestore:

    def __init__(self) -> None:
        self._data = {}

    def collection(self, name: str) -> CollectionReference:
        if name not in self._data:
            self._data[name] = {}
        return CollectionReference(self._data, [name])

    def reset(self):
        self._data = {}


def get_by_path(data: Dict[str, T], path: Sequence[str]) -> T:
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, path, data)


def set_by_path(data: Dict[str, T], path: Sequence[str], value: T):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(data, path[:-1])[path[-1]] = value
