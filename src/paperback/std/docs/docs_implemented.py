from __future__ import annotations

import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import py2neo
from fastapi import APIRouter, Depends, HTTPException, status

from paperback.abc import BaseAuth, BaseDocs
from paperback.abc.models import CreateDoc, ReadMinimalCorp, TokenTester, UserInfo
from paperback.exceptions import PaperBackError
from paperback.exceptions.docs import CorpusDoesntExist, DocumentNameError, DictNameError
from paperback.std.docs.analyzers import PyExLingWrapper, TitanisWrapper
from paperback.std.docs.tasks import add_document


class AnalyzerEnum(str, Enum):
    pyexling = "pyexling"
    titanis_open = "titanis_open"


class DocsImplemented(BaseDocs):
    requires_dir: bool = True
    requires_auth: bool = True
    DEFAULTS: Dict[str, Any] = {
        "db": {
            "scheme": "bolt",
            "username": "neo4j",
            "password": "password",
            "host": "localhost",
            "port": "7687",
        },
        "analyzers": {
            "titanis": {
                "host": "",
            },
            "pyexling": {
                "host": "",
                "service": "",
                "titanis_host": "",
            },
        },
    }

    def __init__(self, cfg: SimpleNamespace, storage_dir: Path, auth_module: BaseAuth):
        # self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.getLogger("paperback").level)
        # self.logger.info("initializing papertext_docs module")

        # self.logger.debug("using storage dir %s", storage_dir)
        # self.logger.debug("using config %s", cfg)
        # self.storage_dir: Path = storage_dir
        # self.cfg: SimpleNamespace = cfg
        # TODO: add check for configuration,
        #  i.e. that hash.algo lib and token.curve lib are present
        self.auth_module = auth_module

        self.docs_backup_folder = self.storage_dir / "docs.bak"
        self.docs_backup_folder.mkdir(parents=True, exist_ok=True)

        # self.logger.debug("connecting to neo4j database")
        # self.graph_db = py2neo.Graph(
        #     scheme=self.cfg.db.scheme,
        #     user=self.cfg.db.username,
        #     password=self.cfg.db.password,
        #     host=self.cfg.db.host,
        #     port=self.cfg.db.port,
        # )
        # self.logger.debug("connected to neo4j database")

        self.logger.debug("creating default corpus")
        self.root_corp = self.graph_db.nodes.match("corp", corp_id="root").first()
        if self.root_corp is None:
            tx = self.graph_db.begin()
            self.root_corp = py2neo.Node("corp", corp_id="root")
            tx.create(self.root_corp)
            tx.commit()
            self.logger.debug("created default root corpus")
        else:
            self.logger.debug("using already existing root corpus")

        # self.logger.debug("syncing with auth module")
        # self.sync_modules_on_startup()
        # self.logger.debug("synced with auth module")

        # self.logger.debug("loading analyzers")
        # self.analyzers = self.get_analyzers(cfg.analyzers)
        # self.logger.debug("loaded analyzers")

    # DONE
    # def get_analyzers(self, analyzers: SimpleNamespace) -> Dict[AnalyzerEnum, Analyzer]:
    #     return {
    #         AnalyzerEnum.pyexling: PyExLingWrapper(
    #             analyzers.pyexling.host,
    #             analyzers.pyexling.service,
    #             analyzers.pyexling.titanis_host,
    #         ),
    #         AnalyzerEnum.titanis_open: TitanisWrapper(analyzers.titanis.host),
    #     }

    # async def __async__init__(self):
    #     await self.sync_modules()
    #     self.set_constraints()

    # def set_constraints(self):
    #     if len(self.graph_db.schema.get_uniqueness_constraints("org")) == 0:
    #         self.graph_db.schema.create_uniqueness_constraint("org", "org_id")
    #     if len(self.graph_db.schema.get_uniqueness_constraints("user")) == 0:
    #         self.graph_db.schema.create_uniqueness_constraint("user", "user_id")
    #     if len(self.graph_db.schema.get_uniqueness_constraints("corp")) == 0:
    #         self.graph_db.schema.create_uniqueness_constraint("corp", "corp_id")
    #     if len(self.graph_db.schema.get_uniqueness_constraints("doc")) == 0:
    #         self.graph_db.schema.create_uniqueness_constraint("doc", "doc_id")

    # def sync_modules_on_startup(self):
    #     pass

    async def sync_modules(self):
        org_nodes: Dict[str, py2neo.Node] = {}
        user_nodes: Dict[str, py2neo.Node] = {}

        tx = self.graph_db.begin()
        self.logger.debug("orgs: %s", await self.auth_module.read_orgs())
        for org in await self.auth_module.read_orgs():
            # creating organisation
            org_node = tx.graph.nodes.match(
                "org",
                org_id=org["organisation_id"],
            ).first()
            if org_node is None:
                org_node = py2neo.Node(
                    "org",
                    org_id=org["organisation_id"],
                    org_name=org["organisation_name"],
                )
                tx.create(org_node)
            org_nodes[org["organisation_id"]] = org_node

        self.logger.debug("users: %s", await self.auth_module.read_users())
        for user in await self.auth_module.read_users():
            # creating user
            user_node = tx.graph.nodes.match(
                "user",
                user_id=user["user_id"],
            ).first()
            if user_node is None:
                user_node = py2neo.Node(
                    "user",
                    user_id=user["user_id"],
                    user_name=user["user_name"],
                    email=user["email"],
                    loa=user["level_of_access"],
                )
                tx.create(user_node)
            user_nodes[user["user_id"]] = user_node

            # connect org to user
            user2org_relation = tx.graph.relationships.match(
                nodes=[
                    org_nodes[user["member_of"]],
                    user_node,
                ]
            ).first()

            if user2org_relation is None:
                user2org_relation = py2neo.Relationship(
                    org_nodes[user["member_of"]],
                    "contains",
                    user_node,
                )
                tx.create(user2org_relation)

        tx.commit()

    # DONE
    # async def create_doc(
    #     self,
    #     creator_id: str,
    #     creator_type: str,
    #     doc_id: str,
    #     text: str,
    #     analyzer_id: Optional[AnalyzerEnum] = "pyexling",
    #     private: bool = False,
    #     parent_corp_id: Optional[str] = None,
    #     name: Optional[str] = None,
    #     has_access: Optional[List[str]] = None,
    #     author: Optional[str] = None,
    #     created: Optional[datetime] = None,
    #     tags: Optional[List[str]] = None,
    # ) -> Dict[str, Any]:
    #     self.logger.debug("adding new document")

    #     tx = self.graph_db.begin()

    #     # check that Document with the same id

    #     docs_with_same_name = tx.graph.nodes.match(
    #         "Document",
    #         doc_id=doc_id,
    #     ).first()

    #     if docs_with_same_name is not None:
    #         raise DocumentNameError

    #     # create Document

    #     doc_node = py2neo.Node(
    #         "Document",
    #         doc_id=doc_id,
    #         text=text,
    #         private=private,
    #         name=name,
    #         author=author,
    #         created=created,
    #         tags=tags,
    #     )
    #     tx.create(doc_node)

    #     # connect Document with creator

    #     if creator_type == "user":
    #         author = tx.graph.nodes.match("user", user_id=creator_id).first()
    #     else:
    #         self.logger.warning("unknown user type: %s", creator_type)

    #     tx.create(py2neo.Relationship(author, "created", doc_node))

    #     # connect Document with corpus

    #     if parent_corp_id is not None:
    #         parent_corp = tx.graph.nodes.match("Corp", corp_id=parent_corp_id).first()
    #         if parent_corp is None:
    #             raise CorpusDoesntExist
    #     else:
    #         parent_corp = self.root_corp
    #     tx.create(py2neo.Relationship(parent_corp, "contains", doc_node))

    #     # add analyzer node

    #     analyzer_res_node = py2neo.Node("AnalyzerResult", analyzer_id=analyzer_id)
    #     tx.create(analyzer_res_node)
    #     tx.create(py2neo.Relationship(doc_node, "analyzed", analyzer_res_node))

    #     # add

    #     analyzer_result: AnalyzerResult = self.analyzers[analyzer_id](
    #         text, analyzer_res_node
    #     )

    #     for node in analyzer_result["nodes"]:
    #         tx.create(node)

    #     for relationship in analyzer_result["relationships"]:
    #         tx.create(relationship)

    #     for command in analyzer_result["commands_to_run"]:
    #         tx.run(command)

    #     tx.commit()

    # async def read_docs(
    #     self,
    #     requester_id: str,
    #     contains: Optional[str] = None,
    #     author: Optional[str] = None,
    #     created_before: Optional[datetime] = None,
    #     created_after: Optional[datetime] = None,
    #     tags: Optional[List[str]] = None,
    # ) -> List[Dict[str, Any]]:
    #     self.logger.debug("reading documents")

    #     if contains is not None:
    #         raise PaperBackError(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="option `contains` is currently unsupported",
    #         )
    #     elif author is not None:
    #         raise PaperBackError(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="option `author` is currently unsupported",
    #         )
    #     elif created_before is not None:
    #         raise PaperBackError(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="option `created_before` is currently unsupported",
    #         )
    #     elif created_after is not None:
    #         raise PaperBackError(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="option `created_after` is currently unsupported",
    #         )
    #     elif tags is not None:
    #         raise PaperBackError(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="option `tags` is currently unsupported",
    #         )
    #     # graph = init_graph(config)
    #     # if only_inactive:
    #     #     query = "MATCH (d:document {inactive : false}) RETURN id(d) as doc_id, d.name as name"
    #     # else:
    #     #     query = "MATCH (d:document {inactive : true}) RETURN id(d) as doc_id, d.name as name"
    #     #
    #     # result = graph.run(query).data()
    #     #
    #     # return {'documents': result}

    #     tx = self.graph_db.begin()
    #     docs: list[py2neo.Node] = tx.graph.nodes.match("document")
    #     self.logger.debug("read documents: %s", list(docs))
    #     self.logger.info("read documents")
    #     return [dict(d) for d in docs]

    async def read_doc(self, doc_id: str) -> Dict[str, Any]:
        pass

    async def update_doc(
        self,
        doc_id: str,
        owner_id: Optional[str] = None,
        owner_type: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        text: Optional[str] = None,
        private: Optional[bool] = False,
        name: Optional[str] = None,
        has_access: Optional[List[str]] = None,
        author: Optional[str] = None,
        created: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        pass

    async def delete_doc(self, doc_id: str):
        pass

    async def create_corp(
        self,
        issuer_id: str,
        issuer_type: str,
        corp_id: str,
        name: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        private: bool = False,
        has_access: Optional[List[str]] = None,
        to_include=None,
    ) -> Dict[str, Any]:
        if to_include is None:
            to_include = []

        tx = self.graph_db.begin()

        corp_with_same_id = tx.graph.nodes.match("corp", corp_id=corp_id).first()
        if corp_with_same_id is not None:
            tx.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "end": f"corpus with id {corp_id} already exists",
                    "rus": f"корпус с id {corp_id} уже существует",
                },
            )
        else:
            corpus = py2neo.Node("corp", corp_id=corp_id, name=name, private=private)
            tx.create(corpus)

        self.logger.debug("created corpus %s", corpus)
        if parent_corp_id is not None:
            parent_corpus = tx.graph.nodes.match(
                "corp",
                corp_id=parent_corp_id,
            ).first()
            if parent_corpus is None:
                tx.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "end": f"parent corpus with id {parent_corp_id} doesn't exists",
                        "rus": f"родительский корпус с id {parent_corp_id} не существует",
                    },
                )

            parent2child_relation = tx.graph.relationships.match(
                nodes=[
                    corpus,
                    parent_corpus,
                ]
            ).first()

            if parent2child_relation is not None:
                tx.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "end": f"connection between parent corpus with id {parent_corp_id} and corpus with id {corp_id} "
                        "already exists",
                        "rus": f"связь между родительским корпусов с id {parent_corp_id} и корпусов с id {corp_id} "
                        "уже существует",
                    },
                )
            else:
                self.logger.debug("parent corpus %s", parent_corpus)
                parent2child = py2neo.Relationship(
                    parent_corpus,
                    "contains",
                    corpus,
                )
                tx.create(parent2child)
                self.logger.debug(f"{parent2child=}")
        if issuer_type == "user":
            issuer_node = tx.graph.nodes.match("user", user_id=issuer_id).first()
        elif issuer_type == "org":
            issuer_node = tx.graph.nodes.match("org", org_id=issuer_id).first()
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "end": f"issuer with type {issuer_type} not recognized",
                    "rus": f"создатель с типом {issuer_type} не распознан",
                },
            )

        issuer2corpus = py2neo.Relationship(
            issuer_node,
            "created",
            corpus,
        )
        tx.create(issuer2corpus)

        if len(to_include) != 0:
            # TODO: implement
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "end": f"to_include is not supported yet",
                    "rus": f"to_include ещё не поддерживается",
                },
            )

        tx.commit()
        return corpus

    async def read_corps(
        self,
        requester_id: str,
        parent_corp_id: Optional[str] = None,
        private: bool = False,
        has_access: Optional[List[str]] = None,
    ):
        return [
            ReadMinimalCorp(corp_id="corp_1", name="Первый корпус"),
            ReadMinimalCorp(corp_id="pushkin_1", name="Корпус сочинений Пушкина"),
        ]

    async def read_corp(self, corp_id: str) -> Dict[str, Any]:
        pass

    async def update_corp(
        self,
        corp_id: str,
        name: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        private: bool = False,
        has_access: Optional[List[str]] = None,
        to_include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        pass

    async def delete_corp(self, corp_id: str):
        pass

    async def create_dict(
        self,
        user_id: str,
        dict_id: str,
        words: List[str],
        private: bool = False,
        name: Optional[str] = None,
        has_access: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        self.logger.debug("adding new document")

        tx = self.graph_db.begin()

        # check that Document with the same id

        dict_with_same_name = tx.graph.nodes.match(
            "Dictionary", dict_id=dict_id,
        ).first()

        if dict_with_same_name is not None:
            raise DictNameError

        # create Dict

        dict_node = py2neo.Node(
            "Dictionary",
            dict_id=dict_id,
            words=words,
            private=private,
            name=name,
        )
        tx.create(dict_node)

        # connect Dict with creator

        author = tx.graph.nodes.match(
            "user", user_id=user_id
        ).first()
        tx.create(py2neo.Relationship(author, "created", dict_node))

        tx.commit()

    async def read_dicts(
        self,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        tx = self.graph_db.begin()

        query_res = tx.run(
            """
            match (:user {user_id: "root"})-[created]->(d:Dictionary)
            return d
            """
        )
        self.logger.debug("read dicts: %s", query_res)


        author = tx.graph.nodes.match(
            "user", user_id=user_id
        ).first()

        dicts: list[py2neo.Node] = tx.graph.match((author, ), r_type="created").where("_ = Dictionary")
        self.logger.debug("read dicts: %s", list(dicts))
        self.logger.info("read dicts")
        return [dict(d) for d in dicts]

    async def read_dict(
        self,
        user_id: str,
        dict_id: str,
    ) -> Dict[str, Any]:
        tx = self.graph_db.begin()

        author = tx.graph.nodes.match(
            "user", user_id=user_id
        ).first()

        dict_node: py2neo.Node = tx.graph.match((author, "Dictionary"), r_type="created").where(dict_id=dict_id)
        self.logger.debug("read dict: %s", dict_node)
        self.logger.info("read dict")
        return dict(dict_node)

    async def update_dict(
        self,
        user_id: str,
        dict_id: str,
        words: List[str],
        private: bool = False,
        name: Optional[str] = None,
        has_access: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        pass

    async def delete_dict(
        self,
        user_id: str,
        corp_id: str
    ):
        pass

    def add_routes(self, router: APIRouter, token_tester: TokenTester):
        # router.routes.pop([r for r in router.routes if r.path=="/docs"][0])

        @router.post("/docs", tags=["docs_module", "docs"])
        async def create_doc(
            doc: CreateDoc[AnalyzerEnum],
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ):
            """
            creates document with given id if it's not occupied
            """
            return self.create_doc(
                creator_id=requester.user_id, creator_type="user", **doc.dict()
            )
