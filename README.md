# Python Mock Firestore

An in-memory implementation of the [Python client library](https://github.com/googleapis/google-cloud-python/tree/master/firestore) for Google Cloud Firestore, intended for use in tests to replace the real thing. This project is in early stages and is only a partial implementation of the real  client library.

To install:

`pip install mock-firestore`

Python 3.5+ is required for it to work.

## Usage

```python
db = firestore.Client()
mock_db = MockFirestore()

# Can be used in the same way as a firestore.Client() object would be, e.g.:
db.collection('users').get()
mock_db.collection('users').get()
```

To reset the store to an empty state, use the `reset()` method:
```python
mock_db = MockFirestore()
mock_db.reset()
```

## Supported operations

```python
mock_db = MockFirestore()

# Collections
mock_db.collection('users')
mock_db.collection('users').get()
mock_db.collection('users').list_documents()

# Documents
mock_db.collection('users').document()
mock_db.collection('users').document('alovelace')
mock_db.collection('users').document('alovelace').id
mock_db.collection('users').document('alovelace').get()
mock_db.collection('users').document('alovelace').get().exists
mock_db.collection('users').document('alovelace').get().to_dict()
mock_db.collection('users').document('alovelace').set({
    'first': 'Ada',
    'last': 'Lovelace'
})
mock_db.collection('users').document('alovelace').set({
    'first': 'Augusta Ada'
}, merge=True)
mock_db.collection('users').document('alovelace').update({
    'born': 1815
})
mock_db.collection('users').document('alovelace').collection('friends')
mock_db.collection('users').document('alovelace').delete()

# Querying
mock_db.collection('users').document('alovelace').order_by('born').get()
mock_db.collection('users').document('alovelace').order_by('born', direction='DESCENDING').get()
mock_db.collection('users').document('alovelace').limit(5).get()
mock_db.collection('users').document('alovelace').where('born', '==', 1815).get()
mock_db.collection('users').document('alovelace').where('born', '<', 1815).get()
mock_db.collection('users').document('alovelace').where('born', '>', 1815).get()
mock_db.collection('users').document('alovelace').where('born', '<=', 1815).get()
mock_db.collection('users').document('alovelace').where('born', '>=', 1815).get()
```
