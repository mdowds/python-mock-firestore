from unittest import TestCase

from mockfirestore import MockFirestore


class TestDocumentSnapshot(TestCase):
    def test_documentSnapshot_toDict(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        doc = fs.collection('foo').document('first').get()
        self.assertEqual({'id': 1}, doc.to_dict())

    def test_documentSnapshot_exists(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        doc = fs.collection('foo').document('first').get()
        self.assertTrue(doc.exists)

    def test_documentSnapshot_exists_documentDoesNotExist(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        doc = fs.collection('foo').document('second').get()
        self.assertFalse(doc.exists)
