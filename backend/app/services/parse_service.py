"""
Parse service — extracts structured data from uploaded resume files (PDF / DOCX).

Implements full parsing pipeline per TRD §4:
- DOCX: Extract typographic fingerprint + raw text
- PDF: Extract layout fingerprint + raw text  
- LLM: Extract structured data using NVIDIA NIM
- Embedding: Generate vector embedding using sentence-transformers
"""

import io
import json
import re
import statistics
from collections import defaultdict
from typing import Any

import pdfplumber
from docx import Document
from openai import OpenAI
from pydantic import ValidationError
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models.fingerprints import (
    BulletConfig,
    DocxFingerprint,
    LinguisticPattern,
    ParagraphStyle,
    PdfFingerprint,
    PdfSectionBoundary,
    PdfTextBlock,
    RunStyle,
    SectionFingerprint,
)
from app.models.resume import StructuredResume

# ── Constants ─────────────────────────────────────────────────────────────────

PAST_TENSE_VERBS = {
    "led", "managed", "built", "designed", "developed", "implemented", "created",
    "improved", "reduced", "increased", "delivered", "architected", "launched",
    "drove", "owned", "coordinated", "collaborated", "established", "achieved",
    "optimized", "automated", "migrated", "scaled", "deployed", "configured"
}

PRESENT_TENSE_VERBS = {
    "lead", "manage", "build", "design", "develop", "implement", "create",
    "improve", "reduce", "increase", "deliver", "architect", "launch",
    "drive", "own", "coordinate", "collaborate", "establish", "achieve",
    "optimize", "automate", "migrate", "scale", "deploy", "configure"
}

BULLET_CHARS = {"•", "-", "▪", "◦", "○", "–", "*"}

# ── Singleton embedding model ─────────────────────────────────────────────────

_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    """Lazy-load sentence-transformers model (loaded once per worker)."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


# ── Linguistic analysis helpers ───────────────────────────────────────────────


def _classify_tense(bullets: list[str]) -> str:
    """Classify bullets as past, present, or mixed tense."""
    if not bullets:
        return "mixed"
    
    past_count = 0
    present_count = 0
    
    for bullet in bullets:
        words = bullet.strip().split()
        if not words:
            continue
        first_word = words[0].lower().strip("•-▪◦○–*").strip()
        
        if first_word in PAST_TENSE_VERBS or first_word.endswith("ed"):
            past_count += 1
        elif first_word in PRESENT_TENSE_VERBS or first_word.endswith("ing") or first_word.endswith("s"):
            present_count += 1
    
    if past_count == present_count:
        return "mixed"
    return "past" if past_count > present_count else "present"


def _check_verb_first(bullets: list[str]) -> bool:
    """Check if >70% of bullets start with a verb."""
    if not bullets:
        return False
    
    verb_count = 0
    for bullet in bullets:
        words = bullet.strip().split()
        if not words:
            continue
        first_word = words[0].lower().strip("•-▪◦○–*").strip()
        
        if first_word in PAST_TENSE_VERBS or first_word in PRESENT_TENSE_VERBS:
            verb_count += 1
    
    return (verb_count / len(bullets)) > 0.7


def _avg_word_count(bullets: list[str]) -> float:
    """Calculate average word count of bullets."""
    if not bullets:
        return 0.0
    word_counts = [len(b.split()) for b in bullets]
    return statistics.mean(word_counts)


def _check_oxford_comma(bullets: list[str]) -> bool | None:
    """Check for Oxford comma usage. None if insufficient data."""
    if len(bullets) < 5:
        return None
    
    full_text = " ".join(bullets)
    return ", and " in full_text


def _check_first_person(bullets: list[str]) -> bool:
    """Check if first person is omitted (True = no 'I' found)."""
    for bullet in bullets:
        if bullet.strip().lower().startswith("i "):
            return False
    return True


# ── DOCX parsing ──────────────────────────────────────────────────────────────


def parse_docx(file_path: str) -> DocxFingerprint:
    """
    Parse a DOCX file and extract typographic fingerprint.
    
    TRD §4.1: Extract paragraph styles, run formatting, bullets, sections, and linguistics.
    """
    doc = Document(file_path)
    
    paragraphs: list[ParagraphStyle] = []
    section_order: list[SectionFingerprint] = []
    bullet_texts: list[str] = []
    raw_lines: list[str] = []
    bullet_count = 0
    
    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        raw_lines.append(text)
        
        style_name = para.style.name
        
        # Extract run styles
        runs: list[RunStyle] = []
        for run in para.runs:
            color_hex = None
            if run.font.color and run.font.color.rgb:
                color_hex = str(run.font.color.rgb)
            
            font_size = None
            if run.font.size:
                font_size = run.font.size.pt
            
            runs.append(RunStyle(
                font_name=run.font.name,
                font_size=font_size,
                bold=run.font.bold or False,
                italic=run.font.italic or False,
                underline=run.font.underline or False,
                color_hex=color_hex
            ))
        
        # Bullet detection
        bullet = None
        if style_name.startswith("List"):
            bullet_count += 1
            bullet_texts.append(text)
            
            bullet_char = text[0] if text else "-"
            for char in text:
                if not char.isspace():
                    bullet_char = char
                    break
            
            indent_level = None
            if para.paragraph_format.left_indent:
                indent_level = para.paragraph_format.left_indent.pt
            
            bullet = BulletConfig(bullet_char=bullet_char, indent_level=indent_level)
        
        # Section detection
        if style_name.startswith("Heading"):
            section_order.append(SectionFingerprint(
                heading_text=text,
                style_name=style_name,
                position=idx
            ))
        
        # Build paragraph style
        space_before = para.paragraph_format.space_before.pt if para.paragraph_format.space_before else None
        space_after = para.paragraph_format.space_after.pt if para.paragraph_format.space_after else None
        alignment = para.paragraph_format.alignment
        
        paragraphs.append(ParagraphStyle(
            style_name=style_name,
            space_before=space_before,
            space_after=space_after,
            alignment=alignment,
            runs=runs,
            bullet=bullet
        ))
    
    # Compute linguistic pattern
    linguistic = LinguisticPattern(
        dominant_tense=_classify_tense(bullet_texts),
        verb_first=_check_verb_first(bullet_texts),
        avg_bullet_word_count=_avg_word_count(bullet_texts),
        oxford_comma=_check_oxford_comma(bullet_texts),
        first_person_omitted=_check_first_person(bullet_texts)
    )
    
    return DocxFingerprint(
        paragraphs=paragraphs,
        section_order=section_order,
        linguistic=linguistic,
        total_paragraphs=len(paragraphs),
        bullet_count=bullet_count,
        raw_full_text="\n".join(raw_lines)
    )


# ── PDF parsing ───────────────────────────────────────────────────────────────


def parse_pdf(file_path: str) -> PdfFingerprint:
    """
    Parse a PDF file and extract layout fingerprint.
    
    TRD §4.2: Extract text blocks with positioning, detect headings/bullets, and linguistics.
    """
    text_blocks: list[PdfTextBlock] = []
    section_boundaries: list[PdfSectionBoundary] = []
    bullet_texts: list[str] = []
    raw_lines: list[str] = []
    font_sizes: list[float] = []
    
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["fontname", "size"])
            
            if not words:
                continue
            
            # Cluster words into lines (within 3pt vertical distance)
            lines: dict[float, list[dict]] = defaultdict(list)
            for word in words:
                y_key = round(word["top"] / 3) * 3
                lines[y_key].append(word)
                if word.get("size"):
                    font_sizes.append(word["size"])
            
            # Process each line
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])
            prev_y = None
            
            for y_pos, line_words in sorted_lines:
                # Sort words left to right
                line_words = sorted(line_words, key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in line_words)
                raw_lines.append(text)
                
                if not line_words:
                    continue
                
                first_word = line_words[0]
                x0 = min(w["x0"] for w in line_words)
                x1 = max(w["x1"] for w in line_words)
                y0 = min(w["top"] for w in line_words)
                y1 = max(w["bottom"] for w in line_words)
                
                size = first_word.get("size")
                fontname = first_word.get("fontname")
                
                # Detect bullets
                is_bullet = False
                first_char = text.strip()[0] if text.strip() else ""
                if first_char in BULLET_CHARS:
                    is_bullet = True
                    bullet_texts.append(text)
                
                text_blocks.append(PdfTextBlock(
                    text=text,
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    fontname=fontname,
                    size=size,
                    is_heading=False,  # Will update after median calculation
                    is_bullet=is_bullet
                ))
                
                prev_y = y_pos
    
    # Calculate median font size and mark headings
    median_size = statistics.median(font_sizes) if font_sizes else 12.0
    
    for block in text_blocks:
        if block.size and block.size > (median_size + 2):
            block.is_heading = True
            # Find corresponding section boundary
            for i, existing in enumerate(section_boundaries):
                if abs(existing.y_position - block.y0) < 5:
                    break
            else:
                section_boundaries.append(PdfSectionBoundary(
                    heading_text=block.text,
                    page_num=0,  # Would need to track page number in loop
                    y_position=block.y0
                ))
    
    # Compute linguistic pattern
    linguistic = LinguisticPattern(
        dominant_tense=_classify_tense(bullet_texts),
        verb_first=_check_verb_first(bullet_texts),
        avg_bullet_word_count=_avg_word_count(bullet_texts),
        oxford_comma=_check_oxford_comma(bullet_texts),
        first_person_omitted=_check_first_person(bullet_texts)
    )
    
    return PdfFingerprint(
        pages=len(list(pdfplumber.open(file_path).pages)),
        text_blocks=text_blocks,
        section_boundaries=section_boundaries,
        linguistic=linguistic,
        raw_full_text="\n".join(raw_lines),
        median_font_size=median_size
    )


# ── LLM extraction ────────────────────────────────────────────────────────────


def extract_structured(raw_text: str) -> StructuredResume:
    """
    Extract structured resume data using NVIDIA NIM LLM.
    
    TRD §4.3: Use Mistral-Nemotron to parse raw text into StructuredResume.
    """
    schema = StructuredResume.model_json_schema()
    
    system_prompt = f"""You are a resume parser. Extract structured data from the provided resume text.
Respond with ONLY valid JSON matching this schema exactly. No preamble, no explanation, no markdown fences. If a field is not present, use null.

Schema: {json.dumps(schema, indent=2)}"""
    
    client = OpenAI(
        base_url=settings.nvidia_nim_base_url,
        api_key=settings.nvidia_api_key_mistral
    )
    
    # First attempt
    response = client.chat.completions.create(
        model="mistralai/mistral-nemotron",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text}
        ],
        temperature=0.1,
        max_tokens=4096
    )
    
    content = response.choices[0].message.content
    
    try:
        data = json.loads(content)
        resume = StructuredResume.model_validate(data)
        resume.raw_full_text = raw_text
        return resume
    except (json.JSONDecodeError, ValidationError) as e:
        # Retry once with error feedback
        retry_prompt = f"""The previous response failed validation with this error: {str(e)}. Fix and return valid JSON only."""
        
        retry_response = client.chat.completions.create(
            model="mistralai/mistral-nemotron",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_text},
                {"role": "assistant", "content": content},
                {"role": "user", "content": retry_prompt}
            ],
            temperature=0.1,
            max_tokens=4096
        )
        
        retry_content = retry_response.choices[0].message.content
        
        try:
            data = json.loads(retry_content)
            resume = StructuredResume.model_validate(data)
            resume.raw_full_text = raw_text
            return resume
        except (json.JSONDecodeError, ValidationError) as retry_error:
            raise ValueError(f"LLM extraction failed after retry: {retry_error}")


# ── Embedding generation ──────────────────────────────────────────────────────


def generate_embedding(text: str) -> list[float]:
    """
    Generate 384-dim embedding using sentence-transformers.
    
    Uses all-MiniLM-L6-v2 model (loaded once per worker).
    """
    model = _get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()
