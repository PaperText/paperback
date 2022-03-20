from fastapi import HTTPException, status
from py2neo import Transaction, Node

from paperback.docs import schemas


def get_docs(tx: Transaction) -> list[schemas.Doc]:
    docs: list[Node] = tx.graph.nodes.match("Document")
    return [schemas.Doc(**d) for d in docs]


def create_doc(tx: Transaction, doc: schemas.DocCreate) -> schemas.Doc:
    doc_node = Node(
        "Document",
        name=doc.name,
        text=doc.text,
        parent_corp_name= doc.parent_corp_name,
        corp_name=doc.corp_name,
        tags=doc.tags,
        # **(doc.dict()),
    )
    tx.create(doc_node)

    if doc.parent_corp_name is not None:
        parent_corp = tx.graph.nodes.match("Corpus", name=doc.parent_corp_name).first()
        if parent_corp is None:
            raise HTTPException(
                status=status.HTTP_404_NOT_FOUND,
                detail="Corpus doesn't exist",
            )

    raise HTTPException(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Not implemented",
            )

