from typing import List, Optional, Tuple

from bytes.database.db import DBManager
from bytes.database.models import DocStore
from langchain_core.stores import BaseStore


class PostgresDocStore(BaseStore[str, str]):
    def __init__(self, db_manager: DBManager) -> None:
        self.db_manager = db_manager

    def mset(self, pairs: List[Tuple[str, str]]) -> None:
        """Set multiple key-values pairs in docstore

        Args:
            pairs (List[Tuple[str,str]]): _description_
        """

        with self.db_manager.session() as session:
            for doc_id, content in pairs:
                existing = session.query(DocStore).filter_by(doc_id=doc_id).first()
                if existing:
                    existing.content = content
                else:
                    docstore = DocStore(doc_id=doc_id, content=content)
                    session.add(docstore)

        print(f"✅ Set {len(pairs)} key-value pairs in docstore")

    def mget(self, keys: List[str]) -> List[Optional[str]]:
        """get multiple values by keys:"""
        with self.db_manager.session() as session:
            result = session.query(DocStore).filter(DocStore.doc_id.in_(keys)).all()
            result_dict = {doc.doc_id: doc.content for doc in result}
            return [result_dict.get(key) for key in keys]

    def mdelete(self, keys: List[str]) -> None:
        with self.db_manager.session() as session:
            session.query(DocStore).filter(DocStore.doc_id.in_(keys)).delete()
        print("✅ Deleted {} keys from docstore".format(len(keys)))

    def yield_keys(self) -> List[str]:
        """return all the document keys(IDs)

        Returns:
            List[str]: _description_
        """
        with self.db_manager.session() as session:
            result = session.query(DocStore).all()
            return [doc.doc_id for doc in result]
