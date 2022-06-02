import aiounittest

from mockfirestore import AsyncMockFirestore


class TestAsyncMockFirestore(aiounittest.AsyncTestCase):
    async def test_query_get(self):
        fs = AsyncMockFirestore()
        doc_in_fs = {"id": 1}
        fs._data = {"foo": {"first": doc_in_fs}}
        docs = await fs.collection("foo").where("id", "==", 1).get()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].to_dict()["id"], 1)
