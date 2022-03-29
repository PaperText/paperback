from uuid import uuid4

import py2neo
from fastapi import HTTPException, status

from paperback.docs import schemas


def create_dict(
    tx: py2neo.Transaction,
    dictionary: schemas.DictionaryCreate,
) -> schemas.Dictionary:
    dict_node = py2neo.Node("Dictionary")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )

    return schemas.Dictionary(**dict(dict_node))


def get_dicts(
    tx: py2neo.Transaction,
) -> list[schemas.Dictionary]:
    dicts: list[py2neo.Node] = tx.graph.nodes.match("Dictionary")
    return [schemas.Dictionary(**d) for d in dicts]


def get_dict_by_name(
    tx: py2neo.Transaction,
    name: str,
) -> schemas.DocOut:
    dictionary: py2neo.Node = tx.graph.nodes.match("Dictionary", name=name)
    return schemas.Dictionary(**dict(dictionary))


def add_word_to_dict_by_name(
    tx: py2neo.Transaction,
    name: str,
    word: str,
) -> schemas.Dictionary:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def delete_word_from_dict_by_name(
    tx: py2neo.Transaction,
    name: str,
    word: str,
) -> schemas.Dictionary:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def delete_dict_by_name(
    tx: py2neo.Transaction,
    name: str,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )
