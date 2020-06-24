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
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "recommonmark",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["templates"]

# exclude_patterns = []

# HTML specific
html_theme = "sphinx_typlog_theme"
html_theme_options = {
    "logo_name": "PaperBack",
    "description": "🗄API of 📎PaperText app",
    "github_user": "PaperText",
    "github_repo": "paperback",
}
html_sidebars = {
    "**": [
        "logo.html",
        "github.html",
        "searchbox.html",
        "globaltoc.html",
        "relations.html",
    ]
}
# html_static_path = ["static"]

# custom hooks
source_link = "https://github.com/PaperText/paperback/blob/master/src"


def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    module = info["module"].replace(".", "/")
    filename = info["fullname"].replace(".", "/")
    return "%s/%s/%s.py" % (source_link, module, filename)


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
