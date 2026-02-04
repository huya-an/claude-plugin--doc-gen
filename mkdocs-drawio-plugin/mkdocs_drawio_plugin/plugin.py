"""
MkDocs plugin that converts Mermaid code blocks to draw.io embeds.

Integration points:
1. SuperFences custom formatter: intercepts ```mermaid blocks during
   markdown processing and converts them to draw.io HTML in-place.
2. on_post_build hook: copies viewer-static.min.js to the output directory.
3. on_page_markdown hook: fallback to catch any unprocessed Mermaid blocks.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from .converter import mermaid_to_figure, mermaid_to_xml
from .encoding import encode_for_mxgraph, wrap_in_mxgraph_div

log = logging.getLogger("mkdocs.plugins.drawio")

# Regex to find ```mermaid blocks in markdown (fallback for on_page_markdown)
_MERMAID_FENCE_RE = re.compile(
    r"```mermaid\s*\n(.*?)```",
    re.DOTALL,
)


class DrawioConfig(Config):
    """Plugin configuration options."""

    viewer_js = config_options.Type(str, default="js/viewer-static.min.js")
    save_drawio_files = config_options.Type(bool, default=True)
    drawio_output_dir = config_options.Type(str, default="drawio")


class DrawioPlugin(BasePlugin[DrawioConfig]):
    """MkDocs plugin: Mermaid → draw.io conversion."""

    def __init__(self):
        super().__init__()
        self._drawio_files: list[tuple[str, str]] = []  # (filename, xml)

    def on_page_markdown(
        self, markdown: str, page: Page, config: MkDocsConfig, files: Files
    ) -> str:
        """Fallback: replace any remaining ```mermaid blocks in markdown.

        This catches blocks that weren't handled by SuperFences (e.g., if
        SuperFences isn't configured, or for blocks in non-standard locations).
        """

        def _replace_mermaid(match: re.Match) -> str:
            mermaid_src = match.group(1).strip()
            try:
                html = mermaid_to_figure(mermaid_src)
                if self.config.save_drawio_files:
                    self._save_drawio(page, mermaid_src)
                return html
            except Exception:
                log.exception("Failed to convert Mermaid block on %s", page.file.src_path)
                return match.group(0)  # Leave original on error

        return _MERMAID_FENCE_RE.sub(_replace_mermaid, markdown)

    def on_post_build(self, config: MkDocsConfig) -> None:
        """Copy viewer JS and .drawio files to the output directory."""
        site_dir = Path(config["site_dir"])

        # Copy viewer JS if it exists
        viewer_src = self._find_viewer_js(config)
        if viewer_src:
            viewer_dest = site_dir / self.config.viewer_js
            viewer_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(viewer_src, viewer_dest)
            log.info("Copied viewer JS to %s", viewer_dest)

        # Write saved .drawio files
        if self.config.save_drawio_files and self._drawio_files:
            drawio_dir = site_dir / self.config.drawio_output_dir
            drawio_dir.mkdir(parents=True, exist_ok=True)
            for filename, xml in self._drawio_files:
                dest = drawio_dir / filename
                dest.write_text(xml, encoding="utf-8")
                log.info("Saved %s", dest)

    def _find_viewer_js(self, config: MkDocsConfig) -> Path | None:
        """Locate viewer-static.min.js in custom_dir or docs_dir."""
        # Check custom_dir (overrides/) first
        custom_dir = config.get("theme", {}).get("custom_dir")
        if custom_dir:
            candidate = Path(custom_dir).parent / "assets" / "js" / "viewer-static.min.js"
            if candidate.exists():
                return candidate

        # Check project root assets/
        project_root = Path(config["config_file_path"]).parent
        candidate = project_root / "assets" / "js" / "viewer-static.min.js"
        if candidate.exists():
            return candidate

        return None

    def _save_drawio(self, page: Page, mermaid_src: str) -> None:
        """Save a .drawio file for download."""
        try:
            xml = mermaid_to_xml(mermaid_src)
            base = page.file.src_path.replace("/", "_").replace(".md", "")
            idx = len(self._drawio_files) + 1
            filename = f"{base}_{idx}.drawio"
            self._drawio_files.append((filename, xml))
        except Exception:
            log.exception("Failed to save .drawio file")


def mermaid_fence_format(
    source: str,
    language: str,
    css_class: str,
    options: dict,
    md,
    **kwargs,
) -> str:
    """SuperFences custom formatter for ```mermaid code blocks.

    This function is registered in mkdocs.yml as the custom_fences handler.
    SuperFences calls it instead of the default Mermaid.js renderer.

    Returns raw HTML that replaces the code block.
    """
    try:
        return mermaid_to_figure(source)
    except Exception:
        log.exception("Failed to convert Mermaid block via SuperFences")
        # Fall through to render as a code block
        return f'<pre class="{css_class}"><code>{source}</code></pre>'
