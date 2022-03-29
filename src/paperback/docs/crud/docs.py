from uuid import uuid4

import py2neo
from fastapi import HTTPException, status

from paperback.docs import schemas
from paperback.docs.analyzers import Analyzer, AnalyzerResult


def create_doc(
    tx: py2neo.Transaction,
    doc: schemas.DocCreate,
    analyzer_id: str,
    analyzer: Analyzer,
) -> schemas.Doc:
    doc_node = py2neo.Node(
        "Document",
        name=doc.name,
        text=doc.text,
        tags=doc.tags,
        doc_uuid=str(uuid4()),
    )
    tx.create(doc_node)

    # add node with analyzer results
    analyzer_res_node = py2neo.Node("AnalyzerResult", analyzer_id=analyzer_id.value)
    tx.create(analyzer_res_node)
    tx.create(py2neo.Relationship(doc_node, "analyzed", analyzer_res_node))

    analyzer_result: AnalyzerResult = analyzer(doc.text, analyzer_res_node)

    for node in analyzer_result["nodes"]:
        tx.create(node)

    for relationship in analyzer_result["relationships"]:
        tx.create(relationship)

    for command in analyzer_result["commands_to_run"]:
        tx.run(command)

    tx.commit()

    return schemas.Doc(**dict(doc_node))


def get_docs(
    tx: py2neo.Transaction,
    tags: list[str] | None = None,
) -> list[schemas.Doc]:
    if tags is None:
        docs: list[py2neo.Node] = tx.graph.nodes.match("Document")
    else:
        # TODO: implement tags
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Not implemented: tags are not supported",
        )
    return [schemas.Doc(**d) for d in docs]


def get_doc_by_name(
    tx: py2neo.Transaction,
    name: str,
) -> schemas.DocOut:
    doc: py2neo.Node = tx.graph.nodes.match("Document", name=name)
    return schemas.Doc(**dict(doc))


def add_tag_to_doc_by_name(
    tx: py2neo.Transaction,
    name: str,
    tag: str,
) -> schemas.Doc:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def delete_tag_from_doc_by_name(
    tx: py2neo.Transaction,
    name: str,
    tag: str,
) -> schemas.Doc:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )


def delete_doc_by_name(
    tx: py2neo.Transaction,
    name: str,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented"
    )
