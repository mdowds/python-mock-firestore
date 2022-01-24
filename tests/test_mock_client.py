from unittest import TestCase

from mockfirestore import MockFirestore


class TestMockFirestore(TestCase):
    def test_client_get_all(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1},
            'second': {'id': 2}
        }}
        doc = fs.collection('foo').document('first')
        results = list(fs.get_all([doc]))
        returned_doc_snapshot = results[0].to_dict()
        expected_doc_snapshot = doc.get().to_dict()
        self.assertEqual(returned_doc_snapshot, expected_doc_snapshot)

    def test_client_collections(self):
        fs = MockFirestore()
        fs._data = {
            'foo': {
                'first': {'id': 1},
                'second': {'id': 2}
            },
            'bar': {}
        }
        collections = fs.collections()
        expected_collections = fs._data

        self.assertEqual(len(collections), len(expected_collections))
        for collection in collections:
            self.assertTrue(collection._path[0] in expected_collections)
