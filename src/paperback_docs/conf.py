from typing import Any, Dict, Optional

import sphinx_rtd_theme
from recommonmark.transform import AutoStructify

import paperback

pt_version = paperback.__version__

# project info
project = "PaperText"
copyright = "2020, Danil Kireev"
author = "Danil Kireev"
version, release = pt_version, pt_version

# configuration
master_doc = "index"
source_suffix = [".rst", ".md"]
gitlab_url: str = "https://gitlab.com/papertext/paperback/"


def linkcode_resolve(domain: str, info: Dict[str, Any]) -> Optional[str]:
    if domain == "py":
        if not info["module"]:
            return None
        # skip non-class links
        if len(info["fullname"].split(".")) > 1:
            return None
        path: str = info["module"].replace(".", "/")
        if info["fullname"] == "Base":
            filename: str = "base.py"
        else:
            filename: str = info["fullname"].replace(
                "Base", ""
            ).lower() + ".py"
        print(f"{gitlab_url}/-/tree/master/src/{path}/{filename}")
        return f"{gitlab_url}/-/tree/master/src/{path}/{filename}"
    return None


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "recommonmark",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["templates"]

# exclude_patterns = []

# HTML specific
html_theme = "sphinx_rtd_theme"
# html_static_path = ["static"]
# custom hooks


def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {
            "enable_auto_toc_tree": True,
            "auto_toc_tree_section": "Contents",
            "enable_math": False,
            "enable_inline_math": False,
            "enable_eval_rst": True,
            # 'url_resolver': lambda url: github_doc_root + url,
        },
        True,
    )
    app.add_transform(AutoStructify)
