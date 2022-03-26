from enum import Enum
from typing import Callable, Literal

from fastapi import Depends

from paperback.docs.analyzers.abc import Analyzer, AnalyzerResult
from paperback.docs.analyzers.implementation import PyExLingWrapper, TitanisWrapper
from paperback.docs.settings import DocsSettingsNotNone, get_docs_settings


class AnalyzerEnum(str, Enum):
    pyexling = "pyexling"
    titanis_open = "titanis_open"


DEFAULT_ANALYZER = AnalyzerEnum.pyexling

AnalyzerEnum2Wrapper: dict[AnalyzerEnum, type[Analyzer]] = {
    AnalyzerEnum.pyexling: PyExLingWrapper,
    AnalyzerEnum.titanis_open: TitanisWrapper,
}

# fastapi dependency
def get_analyzer(
    settings: DocsSettingsNotNone = Depends(get_docs_settings),
) -> Callable[[AnalyzerEnum], Analyzer]:
    def _get_analyzer(analyzer_id: AnalyzerEnum) -> Analyzer:
        match analyzer_id:
            case AnalyzerEnum.pyexling:
                return PyExLingWrapper(
                    settings.analyzers_pyexling_host,
                    settings.analyzers_pyexling_service,
                    settings.analyzers_titanis_host,
                )
            case AnalyzerEnum.titanis_open:
                return TitanisWrapper(
                    settings.analyzers_titanis_host,
                )

    return _get_analyzer
