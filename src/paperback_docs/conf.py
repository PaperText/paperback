from typing import Any, Dict, List

from recommonmark.transform import AutoStructify

import paperback


# project info
project: str = "PaperText"
copyright: str = "2020, Danil Kireev"
author: str = "Danil Kireev"
version: str = paperback.__version__,
release: str = paperback.__version__

# configuration
master_doc: str = "index"
source_suffix: List[str] = [".rst", ".md"]
extensions: List[str] = [
    "sphinx.ext.autodoc",
    # "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "recommonmark",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
# templates_path: List[str] = ["templates"]

# exclude_patterns: List[str] = []

# HTML specific
html_theme: str = "sphinx_typlog_theme"
html_theme_options: Dict[str, str] = {
    "logo_name": "PaperBack",
    "description": "🗄API of 📎PaperText app",
    "github_user": "PaperText",
    "github_repo": "paperback",
}
html_sidebars: Dict[str, List[str]] = {
    "**": [
        "logo.html",
        "github.html",
        "searchbox.html",
        "globaltoc.html",
        "relations.html",
    ]
}
# html_static_path: List[str] = ["static"]

# custom hooks
source_link: str = "https://github.com/PaperText/paperback/tree/master/src/paperback_docs"


def setup(app: Any) -> Any:
    app.add_config_value(
        "recommonmark_config",
        {
            "enable_auto_toc_tree": True,
            "auto_toc_tree_section": "Contents",
            "enable_math": False,
            "enable_inline_math": False,
            "enable_eval_rst": True,
            "url_resolver": lambda url: source_link + url,
        },
        True,
    )
    app.add_transform(AutoStructify)
