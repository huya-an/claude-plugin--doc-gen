"""
Encoding pipeline for draw.io XML embedding in HTML.

Two-step process per drawio-patterns.md:
1. JSON-escape the XML string (\" and \\)
2. HTML-entity-encode the result (<, >, &)

CRITICAL: Never use &quot; for " — that breaks JSON parsing in data-mxgraph attributes.
"""


def json_escape(xml: str) -> str:
    """Step 1: JSON-escape quotes and backslashes in XML string."""
    return xml.replace("\\", "\\\\").replace('"', '\\"')


def html_entity_encode(s: str) -> str:
    """Step 2: HTML-entity-encode angle brackets, ampersands, and single quotes.

    Order matters: & must be encoded first to avoid double-encoding.
    Single quotes must be encoded because data-mxgraph uses single-quoted
    HTML attribute delimiters — an unescaped ' in the content terminates
    the attribute prematurely.
    """
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
    )


def encode_for_mxgraph(xml: str) -> str:
    """Full encoding pipeline: JSON-escape then HTML-entity-encode.

    Returns a string safe for use as the "xml" value inside a
    data-mxgraph JSON attribute (single-quoted HTML attribute).
    """
    return html_entity_encode(json_escape(xml))


def wrap_in_mxgraph_div(encoded_xml: str) -> str:
    """Wrap encoded XML in a draw.io viewer div element.

    The div uses single-quoted data-mxgraph attribute containing JSON
    with navigation, resize, fit, and toolbar options.
    """
    return (
        '<div class="mxgraph" data-mxgraph=\''
        '{"nav":true,"resize":true,"fit":true,"center":true,'
        '"toolbar":"zoom layers lightbox","page":0,'
        f'"xml":"{encoded_xml}"}}'
        "'></div>"
    )


def xml_to_html(raw_xml: str) -> str:
    """Convert raw mxGraphModel XML to an embeddable HTML div."""
    return wrap_in_mxgraph_div(encode_for_mxgraph(raw_xml))
