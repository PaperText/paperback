from py2neo import Transaction, Node
from paperback.docs import schemas


def get_docs(tx: Transaction) -> list[schemas.Doc]:
    docs: list[Node] = tx.graph.nodes.match("Document")
    return [schemas.Doc(**d) for d in docs]


def create_doc(tx: Transaction, doc: schemas.DocCreate) -> schemas.Doc:
    doc_node = Node(
        "Document",
        **(doc.dict()),
    )
    tx.create(doc_node)

    if doc.parent_corp_name is not None:
        parent_corp = tx.graph.nodes.match("Corpus", name=doc.parent_corp_name).first()
        if parent_corp is None:
            raise Exception("Corpus doesn't exist")




