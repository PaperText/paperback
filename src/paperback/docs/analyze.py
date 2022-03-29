from paperback.docs import schemas

from fastapi import HTTPException, status
import py2neo


def analyze_lexics(
    tx: py2neo.Transaction,
    docs_and_corpuses: list[schemas.DocsAndCorpuses],
    dicts: list[str],
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def analyze_predicates(
    tx: py2neo.Transaction,
    docs_and_corpuses: list[schemas.DocsAndCorpuses],
    argument: str,
    predicate: str,
    role: str,
    return_context: bool,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def available_statistics():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def analyze_stats(
    tx: py2neo.Transaction,
    docs_and_corpuses: list[schemas.DocsAndCorpuses],
    statistics: list[str],
    analyze_sub_entities: bool,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def analyze_compare(
    tx: py2neo.Transaction,
    first_docs_and_corpuses: list[schemas.DocsAndCorpuses],
    second_docs_and_corpuses: list[schemas.DocsAndCorpuses],
    statistics: list[str],
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )
