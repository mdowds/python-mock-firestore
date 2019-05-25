from unittest import TestCase

from mockfirestore import MockFirestore


class TestCollectionReference(TestCase):
    def test_collection_get_returnsDocuments(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1},
            'second': {'id': 2}
        }}
        docs = list(fs.collection('foo').get())

        self.assertEqual({'id': 1}, docs[0].to_dict())
        self.assertEqual({'id': 2}, docs[1].to_dict())

    def test_collection_get_collectionDoesNotExist(self):
        fs = MockFirestore()
        docs = fs.collection('foo').get()
        self.assertEqual([], list(docs))

    def test_collection_get_nestedCollection(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {
                'id': 1,
                'bar': {
                    'first_nested': {'id': 1.1}
                }
            }
        }}
        docs = list(fs.collection('foo').document('first').collection('bar').get())
        self.assertEqual({'id': 1.1}, docs[0].to_dict())

    def test_collection_get_nestedCollection_collectionDoesNotExist(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        docs = list(fs.collection('foo').document('first').collection('bar').get())
        self.assertEqual([], docs)

    def test_collection_get_ordersByAscendingDocumentId_byDefault(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'beta': {'id': 1},
            'alpha': {'id': 2}
        }}
        docs = list(fs.collection('foo').get())
        self.assertEqual({'id': 2}, docs[0].to_dict())

    def test_collection_whereEquals(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'valid': True},
            'second': {'valid': False}
        }}

        docs = list(fs.collection('foo').where('valid', '==', True).get())
        self.assertEqual({'valid': True}, docs[0].to_dict())

    def test_collection_whereLessThan(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'count': 1},
            'second': {'count': 5}
        }}

        docs = list(fs.collection('foo').where('count', '<', 5).get())
        self.assertEqual({'count': 1}, docs[0].to_dict())

    def test_collection_whereLessThanOrEqual(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'count': 1},
            'second': {'count': 5}
        }}

        docs = list(fs.collection('foo').where('count', '<=', 5).get())
        self.assertEqual({'count': 1}, docs[0].to_dict())
        self.assertEqual({'count': 5}, docs[1].to_dict())

    def test_collection_whereGreaterThan(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'count': 1},
            'second': {'count': 5}
        }}

        docs = list(fs.collection('foo').where('count', '>', 1).get())
        self.assertEqual({'count': 5}, docs[0].to_dict())

    def test_collection_whereGreaterThanOrEqual(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'count': 1},
            'second': {'count': 5}
        }}

        docs = list(fs.collection('foo').where('count', '>=', 1).get())
        self.assertEqual({'count': 1}, docs[0].to_dict())
        self.assertEqual({'count': 5}, docs[1].to_dict())

    def test_collection_orderBy(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'order': 2},
            'second': {'order': 1}
        }}

        docs = list(fs.collection('foo').order_by('order').get())
        self.assertEqual({'order': 1}, docs[0].to_dict())
        self.assertEqual({'order': 2}, docs[1].to_dict())

    def test_collection_orderBy_descending(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'order': 2},
            'second': {'order': 3},
            'third': {'order': 1}
        }}

        docs = list(fs.collection('foo').order_by('order', direction="DESCENDING").get())
        self.assertEqual({'order': 3}, docs[0].to_dict())
        self.assertEqual({'order': 2}, docs[1].to_dict())
        self.assertEqual({'order': 1}, docs[2].to_dict())

    def test_collection_limit(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1},
            'second': {'id': 2}
        }}
        docs = list(fs.collection('foo').limit(1).get())
        self.assertEqual({'id': 1}, docs[0].to_dict())
        self.assertEqual(1, len(docs))

    def test_collection_limitAndOrderBy(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'order': 2},
            'second': {'order': 1},
            'third': {'order': 3}
        }}
        docs = list(fs.collection('foo').order_by('order').limit(2).get())
        self.assertEqual({'order': 1}, docs[0].to_dict())
        self.assertEqual({'order': 2}, docs[1].to_dict())
