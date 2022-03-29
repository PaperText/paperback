from uuid import uuid4

import py2neo
from fastapi import HTTPException, status

from paperback.docs import schemas


def create_corpus(
    tx: py2neo.Transaction,
    corp: schemas.CorpusCreate,
) -> schemas.Corpus:
    corpus_node = py2neo.Node("Corpus")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )

    return schemas.Corpus(**dict(corpus_node))


def get_corpuses(
    tx: py2neo.Transaction,
) -> list[schemas.Corpus]:
    corpuses: py2neo.Node = tx.graph.nodes.match("Corpus")
    return [schemas.Corpus(**c) for c in corpuses]


def get_corpus_by_name(
    tx: py2neo.Transaction,
    name: str,
) -> schemas.Corpus:
    corpus: py2neo.Node = tx.graph.nodes.match("Corpus", name=name)
    return schemas.Corpus(**dict(corpus))


def add_subcorpus_to_corpus_by_name(
    tx: py2neo.Transaction,
    name: str,
    sub_name: str,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def add_document_to_corpus_by_name(
    tx: py2neo.Transaction,
    name: str,
    sub_name: str,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )

def remove_subcorpus_from_corpus_by_name(
    tx: py2neo.Transaction,
    name: str,
    sub_name: str,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def remove_document_from_corpus_by_name(
    tx: py2neo.Transaction,
    name: str,
    sub_name: str,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def delete_corpus_by_name(
    tx: py2neo.Transaction,
    name: str,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )
