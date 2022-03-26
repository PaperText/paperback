from typing import Iterator

from py2neo import Graph, Transaction
from py2neo.ogm import Repository

from paperback.docs.settings import get_docs_settings

settings = get_docs_settings()


repo = Repository(
    f"{settings.db_scheme}://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}"
)


# dependency
def get_transaction() -> Iterator[Transaction]:
    graph: Graph = repo.graph
    transaction = graph.begin()
    try:
        yield transaction
    finally:
        graph.rollback(transaction)
