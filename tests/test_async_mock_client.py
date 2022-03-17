import aiounittest

from mockfirestore import AsyncMockFirestore
from mockfirestore._helpers import consume_async_iterable


class TestAsyncMockFirestore(aiounittest.AsyncTestCase):
    async def test_client_get_all(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}, "second": {"id": 2}}}
        doc = fs.collection("foo").document("first")
        results = await consume_async_iterable(fs.get_all([doc]))
        returned_doc_snapshot = results[0].to_dict()
        expected_doc_snapshot = (await doc.get()).to_dict()
        self.assertEqual(returned_doc_snapshot, expected_doc_snapshot)

    async def test_client_collections(self):
        fs = AsyncMockFirestore()
        fs._data = {"foo": {"first": {"id": 1}, "second": {"id": 2}}, "bar": {}}
        collections = await consume_async_iterable(fs.collections())
        expected_collections = fs._data

        self.assertEqual(len(collections), len(expected_collections))
        for collection in collections:
            self.assertTrue(collection._path[0] in expected_collections)
