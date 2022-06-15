# Python Mock Firestore

An in-memory implementation of the [Python client library](https://github.com/googleapis/python-firestore) for Google Cloud Firestore, intended for use in tests to replace the real thing. This project is only a partial implementation of the real client library.

To install:

`pip install mock-firestore`

Python 3.6+ is required for it to work.

## Usage

### Sync

```python
db = firestore.Client()
mock_db = MockFirestore()

# Can be used in the same way as a firestore.Client() object would be, e.g.:
db.collection('users').get()
mock_db.collection('users').get()
```

### Async

```python
db = firestore.AsyncClient()
mock_db = AsyncMockFirestore()

await db.collection('users').get()
await mock_db.collection('users').get()
```

To reset the store to an empty state, use the `reset()` method:
```python
mock_db = MockFirestore()
mock_db.reset()
```

or the equivalent method of `AsyncMockFirestore`

## Supported operations

### Sync

```python
mock_db = MockFirestore()

# Collections
mock_db.collections()
mock_db.collection('users')
mock_db.collection('users').get()
mock_db.collection('users').list_documents()
mock_db.collection('users').stream()

# Documents
mock_db.collection('users').document()
mock_db.collection('users').document('alovelace')
mock_db.collection('users').document('alovelace').id
mock_db.collection('users').document('alovelace').parent
mock_db.collection('users').document('alovelace').update_time
mock_db.collection('users').document('alovelace').read_time
mock_db.collection('users').document('alovelace').get()
mock_db.collection('users').document('alovelace').get().exists
mock_db.collection('users').document('alovelace').get().to_dict()
mock_db.collection('users').document('alovelace').set({
    'first': 'Ada',
    'last': 'Lovelace'
})
mock_db.collection('users').document('alovelace').set({'first': 'Augusta Ada'}, merge=True)
mock_db.collection('users').document('alovelace').update({'born': 1815})
mock_db.collection('users').document('alovelace').update({'favourite.color': 'red'})
mock_db.collection('users').document('alovelace').update({'associates': ['Charles Babbage', 'Michael Faraday']})
mock_db.collection('users').document('alovelace').collection('friends')
mock_db.collection('users').document('alovelace').delete()
mock_db.collection('users').document('alovelace').delete()
mock_db.collection('users').add({'first': 'Ada', 'last': 'Lovelace'}, 'alovelace')
mock_db.get_all([mock_db.collection('users').document('alovelace')])
mock_db.document('users/alovelace')
mock_db.document('users/alovelace').update({'born': 1815})
mock_db.collection('users/alovelace/friends')

# Querying
mock_db.collection('users').order_by('born').get()
mock_db.collection('users').order_by('born', direction='DESCENDING').get()
mock_db.collection('users').limit(5).get()
mock_db.collection('users').where('born', '==', 1815).get()
mock_db.collection('users').where('born', '!=', 1815).get()
mock_db.collection('users').where('born', '<', 1815).get()
mock_db.collection('users').where('born', '>', 1815).get()
mock_db.collection('users').where('born', '<=', 1815).get()
mock_db.collection('users').where('born', '>=', 1815).get()
mock_db.collection('users').where('born', 'in', [1815, 1900]).stream()
mock_db.collection('users').where('born', 'in', [1815, 1900]).stream()
mock_db.collection('users').where('associates', 'array_contains', 'Charles Babbage').stream()
mock_db.collection('users').where('associates', 'array_contains_any', ['Charles Babbage', 'Michael Faraday']).stream()

# Transforms
mock_db.collection('users').document('alovelace').update({'likes': firestore.Increment(1)})
mock_db.collection('users').document('alovelace').update({'associates': firestore.ArrayUnion(['Andrew Cross', 'Charles Wheatstone'])})
mock_db.collection('users').document('alovelace').update({firestore.DELETE_FIELD: "born"})
mock_db.collection('users').document('alovelace').update({'associates': firestore.ArrayRemove(['Andrew Cross'])})

# Cursors
mock_db.collection('users').start_after({'id': 'alovelace'}).stream()
mock_db.collection('users').end_before({'id': 'alovelace'}).stream()
mock_db.collection('users').end_at({'id': 'alovelace'}).stream()
mock_db.collection('users').start_after(mock_db.collection('users').document('alovelace')).stream()

# Transactions
transaction = mock_db.transaction()
transaction.id
transaction.in_progress
transaction.get(mock_db.collection('users').where('born', '==', 1815))
transaction.get(mock_db.collection('users').document('alovelace'))
transaction.get_all([mock_db.collection('users').document('alovelace')])
transaction.set(mock_db.collection('users').document('alovelace'), {'born': 1815})
transaction.update(mock_db.collection('users').document('alovelace'), {'born': 1815})
transaction.delete(mock_db.collection('users').document('alovelace'))
transaction.commit()
```

### Async
*(Where usage of those differs from the above)*

*Note: all iterator methods like `stream` or `list_documents` in AsyncMockFirestore and its associated async classes 
return asynchronous iterators, so when iterating over them,
`async for` syntax must be used.*

```python
mock_db = AsyncMockFirestore()

# Collections
await mock_db.collection('users').get()

# async iterators
[doc_ref async for doc_ref in mock_db.collection('users').list_documents()]
[doc_snapshot async for doc_snapshot in mock_db.collection('users').stream()]

# Documents
await mock_db.collection('users').document('alovelace').get()
doc_snapshot = await mock_db.collection('users').document('alovelace').get()
doc_snapshot.exists
doc_snapshot.to_dict()
await mock_db.collection('users').document('alovelace').set({
    'first': 'Ada',
    'last': 'Lovelace'
})
await mock_db.collection('users').document('alovelace').set({'first': 'Augusta Ada'}, merge=True)
await mock_db.collection('users').document('alovelace').update({'born': 1815})
await mock_db.collection('users').document('alovelace').update({'favourite.color': 'red'})
await mock_db.collection('users').document('alovelace').update({'associates': ['Charles Babbage', 'Michael Faraday']})
await mock_db.collection('users').document('alovelace').delete()
await mock_db.collection('users').document('alovelace').delete()
await mock_db.collection('users').add({'first': 'Ada', 'last': 'Lovelace'}, 'alovelace')
await mock_db.get_all([mock_db.collection('users').document('alovelace')])
await mock_db.document('users/alovelace').update({'born': 1815})

# Querying
await mock_db.collection('users').order_by('born').get()
await mock_db.collection('users').order_by('born', direction='DESCENDING').get()
await mock_db.collection('users').limit(5).get()
await mock_db.collection('users').where('born', '==', 1815).get()
await mock_db.collection('users').where('born', '!=', 1815).get()
await mock_db.collection('users').where('born', '<', 1815).get()
await mock_db.collection('users').where('born', '>', 1815).get()
await mock_db.collection('users').where('born', '<=', 1815).get()
await mock_db.collection('users').where('born', '>=', 1815).get()

# async iterators
mock_db.collection('users').where('born', 'in', [1815, 1900]).stream()
mock_db.collection('users').where('born', 'in', [1815, 1900]).stream()
mock_db.collection('users').where('associates', 'array_contains', 'Charles Babbage').stream()
mock_db.collection('users').where('associates', 'array_contains_any', ['Charles Babbage', 'Michael Faraday']).stream()

# Transforms
await mock_db.collection('users').document('alovelace').update({'likes': firestore.Increment(1)})
await mock_db.collection('users').document('alovelace').update({'associates': firestore.ArrayUnion(['Andrew Cross', 'Charles Wheatstone'])})
await mock_db.collection('users').document('alovelace').update({firestore.DELETE_FIELD: "born"})
await mock_db.collection('users').document('alovelace').update({'associates': firestore.ArrayRemove(['Andrew Cross'])})


# Transactions
transaction = mock_db.transaction()
transaction.id
transaction.in_progress
await transaction.get(mock_db.collection('users').where('born', '==', 1815))
await transaction.get(mock_db.collection('users').document('alovelace'))
await transaction.get_all([mock_db.collection('users').document('alovelace')])

transaction.set(mock_db.collection('users').document('alovelace'), {'born': 1815})
transaction.update(mock_db.collection('users').document('alovelace'), {'born': 1815})
transaction.delete(mock_db.collection('users').document('alovelace'))
await transaction.commit()
```


## Running the tests
* Create and activate a virtualenv with a Python version of at least 3.6
* Install dependencies with `pip install -r requirements-dev-minimal.txt`
* Run tests with `python -m unittest discover tests -t /`

## Contributors

* [Matt Dowds](https://github.com/mdowds)
* [Chris Tippett](https://github.com/christippett)
* [Anna Melnikov](https://github.com/anna-hope)
* [Ben Riggleman](https://github.com/briggleman)
* [Steve Atwell](https://github.com/satwell)
* [ahti123](https://github.com/ahti123)
* [Billcountry Mwaniki](https://github.com/Billcountry)
* [Lucas Moura](https://github.com/lsantosdemoura)
* [Kamil Romaszko](https://github.com/kromash)
* [Anna Melnikov](https://github.com/notnami)
* [Carl Chipperfield](https://github.com/carl-chipperfield)
* [Aaron Loo](https://github.com/domanchi)
* [Kristof Krenn](https://github.com/KrennKristof)
* [Ben Phillips](https://github.com/tavva)
* [Rene Delgado](https://github.com/RDelg)
* [klanderson](https://github.com/klanderson)
* [William Li](https://github.com/wli)
* [Ugo Marchand](https://github.com/UgoM)
* [Bryce Thornton](https://github.com/brycethornton)
