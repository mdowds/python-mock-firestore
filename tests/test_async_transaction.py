import aiounittest

from mockfirestore import AsyncMockFirestore, AsyncTransaction
from mockfirestore._helpers import consume_async_iterable


class TestAsyncTransaction(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        self.fs = AsyncMockFirestore()
        self.fs._data = {"foo": {"first": {"id": 1}, "second": {"id": 2}}}

    async def test_transaction_getAll(self):
        async with AsyncTransaction(self.fs) as transaction:
            await transaction._begin()
            docs = [
                self.fs.collection("foo").document(doc_name)
                for doc_name in self.fs._data["foo"]
            ]
            results = await consume_async_iterable(transaction.get_all(docs))
            returned_docs_snapshots = [result.to_dict() for result in results]
            expected_doc_snapshots = [(await doc.get()).to_dict() for doc in docs]
            for expected_snapshot in expected_doc_snapshots:
                self.assertIn(expected_snapshot, returned_docs_snapshots)

    async def test_transaction_getDocument(self):
        async with AsyncTransaction(self.fs) as transaction:
            await transaction._begin()
            doc = self.fs.collection("foo").document("first")
            returned_doc = [doc async for doc in transaction.get(doc)][0]
            self.assertEqual((await doc.get()).to_dict(), returned_doc.to_dict())

    async def test_transaction_getQuery(self):
        async with AsyncTransaction(self.fs) as transaction:
            await transaction._begin()
            query = self.fs.collection("foo").order_by("id")
            returned_docs = [doc.to_dict() async for doc in transaction.get(query)]
            query = self.fs.collection("foo").order_by("id")
            expected_docs = [doc.to_dict() async for doc in query.stream()]
            self.assertEqual(returned_docs, expected_docs)

    async def test_transaction_set_setsContentOfDocument(self):
        doc_content = {"id": "3"}
        doc_ref = self.fs.collection("foo").document("third")
        async with AsyncTransaction(self.fs) as transaction:
            await transaction._begin()
            transaction.set(doc_ref, doc_content)
        self.assertEqual((await doc_ref.get()).to_dict(), doc_content)

    async def test_transaction_set_mergeNewValue(self):
        doc = self.fs.collection("foo").document("first")
        async with AsyncTransaction(self.fs) as transaction:
            await transaction._begin()
            transaction.set(doc, {"updated": True}, merge=True)
        updated_doc = {"id": 1, "updated": True}
        self.assertEqual((await doc.get()).to_dict(), updated_doc)

    async def test_transaction_update_changeExistingValue(self):
        doc = self.fs.collection("foo").document("first")
        async with AsyncTransaction(self.fs) as transaction:
            await transaction._begin()
            transaction.update(doc, {"updated": False})
        updated_doc = {"id": 1, "updated": False}
        self.assertEqual((await doc.get()).to_dict(), updated_doc)

    async def test_transaction_delete_documentDoesNotExistAfterDelete(self):
        doc = self.fs.collection("foo").document("first")
        async with AsyncTransaction(self.fs) as transaction:
            await transaction._begin()
            transaction.delete(doc)
        doc = await self.fs.collection("foo").document("first").get()
        self.assertEqual(False, doc.exists)
