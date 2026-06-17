"""
Document fingerprint models — TRD §4.1 and §4.2.

These models capture the typographic and structural identity of a resume
file (DOCX or PDF) independently of its content. They are stored as JSONB
in the resumes.fingerprint column and used by the rewrite service to
reproduce the original document's appearance.
"""

from typing import Literal

from pydantic import BaseModel, Field


# ── Shared ────────────────────────────────────────────────────────────────────


class RunStyle(BaseModel):
    """Formatting attributes of a single text run inside a DOCX paragraph."""

    font_name: str | None = None
    font_size: float | None = None          # points
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color_hex: str | None = None            # e.g. "FF0000"; None = automatic/theme


class BulletConfig(BaseModel):
    """Bullet character and indentation for a list paragraph."""

    bullet_char: str                        # first visible glyph, e.g. "•", "-"
    indent_level: float | None = None       # left indent in points; None = default


class ParagraphStyle(BaseModel):
    """All style attributes recorded for one DOCX paragraph."""

    style_name: str                         # Word style name, e.g. "Heading 1", "Normal"
    space_before: float | None = None       # points
    space_after: float | None = None        # points
    alignment: int | None = None            # WD_ALIGN_PARAGRAPH int or None
    runs: list[RunStyle] = Field(default_factory=list)
    bullet: BulletConfig | None = None      # set only when style_name starts with "List"


class SectionFingerprint(BaseModel):
    """A heading-level section boundary detected in the document."""

    heading_text: str
    style_name: str                         # e.g. "Heading 1"
    position: int                           # paragraph index (0-based)


class LinguisticPattern(BaseModel):
    """Linguistic style patterns extracted from bullet paragraphs."""

    dominant_tense: Literal["past", "present", "mixed"]
    verb_first: bool                        # True if >70 % of bullets start with a verb
    avg_bullet_word_count: float
    oxford_comma: bool | None = None        # None if fewer than 5 bullets observed
    first_person_omitted: bool              # True if no bullet starts with "I "


# ── DOCX ──────────────────────────────────────────────────────────────────────


class DocxFingerprint(BaseModel):
    """
    Complete style fingerprint for a .docx resume.

    Captured by ParseService.parse_docx(); stored as JSONB in resumes.fingerprint.
    """

    paragraphs: list[ParagraphStyle] = Field(default_factory=list)
    section_order: list[SectionFingerprint] = Field(default_factory=list)
    linguistic: LinguisticPattern
    total_paragraphs: int
    bullet_count: int
    raw_full_text: str                      # newline-joined plain text of all paragraphs


# ── PDF ───────────────────────────────────────────────────────────────────────


class PdfTextBlock(BaseModel):
    """A single line-level text block extracted from a PDF page."""

    text: str
    x0: float                               # left edge (pts from left margin)
    y0: float                               # top edge (pts from top of page)
    x1: float                               # right edge
    y1: float                               # bottom edge
    fontname: str | None = None
    size: float | None = None               # font size in points
    is_heading: bool = False                # True when size > median_font_size + 2
    is_bullet: bool = False                 # True when first visible char is a bullet glyph


class PdfSectionBoundary(BaseModel):
    """A heading-level section boundary detected in a PDF."""

    heading_text: str
    page_num: int                           # 0-based page index
    y_position: float                       # y0 of the heading block


class PdfFingerprint(BaseModel):
    """
    Complete style fingerprint for a .pdf resume.

    Captured by ParseService.parse_pdf(); stored as JSONB in resumes.fingerprint.
    """

    pages: int
    text_blocks: list[PdfTextBlock] = Field(default_factory=list)
    section_boundaries: list[PdfSectionBoundary] = Field(default_factory=list)
    linguistic: LinguisticPattern
    raw_full_text: str                      # newline-joined text of all blocks
    median_font_size: float | None = None
