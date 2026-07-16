"""
Bulletproof template loader — loads ALL templates from embedded Python strings.

Vercel's Python runtime only bundles .py files by default, NOT .html files.
This loader imports templates from a .py module where all template HTML is
stored as Python string constants. The module-level import ensures Vercel's
static dependency analyzer includes the file in the serverless function bundle.
"""
import logging
from typing import Iterator

from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader

# Module-level import — guarantees Vercel bundles templates_embedded.py
from apps.esppa import templates_embedded as _inline

logger = logging.getLogger(__name__)


class InlineTemplateLoader(Loader):
    """Loads ALL templates from the embedded Python strings module.

    This is configured as the FIRST loader in TEMPLATES, so it takes
    priority over filesystem loaders. This eliminates any dependency
    on .html files being bundled by Vercel.
    """

    def get_template_sources(self, template_name: str) -> Iterator[str]:
        if template_name in _inline.INLINE_TEMPLATES:
            yield f"inline:{template_name}"

    def get_contents(self, template_name: str) -> str:
        if template_name in _inline.INLINE_TEMPLATES:
            logger.debug("Loaded inline template: %s", template_name)
            return _inline.INLINE_TEMPLATES[template_name]
        raise TemplateDoesNotExist(template_name)
