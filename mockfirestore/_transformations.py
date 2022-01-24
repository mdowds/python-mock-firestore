from typing import Dict, Any, List

from mockfirestore._helpers import get_document_iterator, get_by_path, set_by_path, delete_by_path


def apply_transformations(document: Dict[str, Any], data: Dict[str, Any]):
    """Handles special fields like INCREMENT."""
    increments = {}
    arr_unions = {}
    arr_deletes = {}
    deletes = []

    for key, value in list(get_document_iterator(data)):
        if not value.__class__.__module__.startswith('google.cloud.firestore'):
            # Unfortunately, we can't use `isinstance` here because that would require
            # us to declare google-cloud-firestore as a dependency for this library.
            # However, it's somewhat strange that the mocked version of the library
            # requires the library itself, so we'll just leverage this heuristic as a
            # means of identifying it.
            #
            # Furthermore, we don't hardcode the full module name, since the original
            # library seems to use a thin shim to perform versioning. e.g. at the time
            # of writing, the full module name is `google.cloud.firestore_v1.transforms`,
            # and it can evolve to `firestore_v2` in the future.
            continue

        transformer = value.__class__.__name__
        if transformer == 'Increment':
            increments[key] = value.value
        elif transformer == 'ArrayUnion':
            arr_unions[key] = value.values
        elif transformer == 'ArrayRemove':
            arr_deletes[key] = value.values
            del data[key]
        elif transformer == 'Sentinel':
            if value.description == "Value used to delete a field in a document.":
                deletes.append(key)
                del data[key]

        # All other transformations can be applied as needed.
        # See #29 for tracking.

    def _update_data(new_values: dict, default: Any):
        for key, value in new_values.items():
            path = key.split('.')

            try:
                item = get_by_path(document, path)
            except (TypeError, KeyError):
                item = default

            set_by_path(data, path, item + value, create_nested=True)

    _update_data(increments, 0)
    _update_data(arr_unions, [])

    _apply_updates(document, data)
    _apply_deletes(document, deletes)
    _apply_arr_deletes(document, arr_deletes)


def _apply_updates(document: Dict[str, Any], data: Dict[str, Any]):
    for key, value in data.items():
        path = key.split(".")
        set_by_path(document, path, value, create_nested=True)


def _apply_deletes(document: Dict[str, Any], data: List[str]):
    for key in data:
        path = key.split(".")
        delete_by_path(document, path)


def _apply_arr_deletes(document: Dict[str, Any], data: Dict[str, Any]):
    for key, values_to_delete in data.items():
        path = key.split(".")
        try:
            value = get_by_path(document, path)
        except KeyError:
            continue
        for value_to_delete in values_to_delete:
            try:
                value.remove(value_to_delete)
            except ValueError:
                pass
        set_by_path(document, path, value)