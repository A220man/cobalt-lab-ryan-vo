"""Text processing utilities for the job evaluation engine.

Provides normalization, skill extraction, experience-level detection,
and slug generation.  All functions are deterministic and require no
external services.
"""
import re
import unicodedata

__all__ = [
    "normalize_text",
    "normalize_skill",
    "normalize_location",
    "extract_skills",
    "extract_experience_level",
    "slugify",
    "KNOWN_SKILLS",
    "SKILL_ALIASES",
    "EXPERIENCE_LEVELS",
]


# ---------------------------------------------------------------------------
# Skill knowledge base
# ---------------------------------------------------------------------------

#: Canonical skill terms recognised in job descriptions.
KNOWN_SKILLS: list[str] = [
    # Programming languages
    "python", "javascript", "typescript", "java", "kotlin", "scala",
    "c++", "c#", "go", "rust", "swift", "ruby", "php", "sql",
    # ML / AI
    "tensorflow", "pytorch", "scikit-learn", "keras", "xgboost",
    "lightgbm", "hugging face", "transformers", "numpy", "pandas",
    "scipy", "opencv", "nltk", "spacy",
    # Web
    "react", "angular", "vue.js", "next.js", "svelte", "nodejs",
    "fastapi", "django", "flask", "express", "spring boot",
    # Cloud / DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
    "jenkins", "github actions", "gitlab ci",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "sqlite", "oracle", "cockroachdb", "kafka", "spark",
    # ML Ops / Data engineering
    "mlops", "airflow", "kubeflow", "mlflow", "dvc",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data engineering", "etl", "data warehousing", "snowflake", "bigquery",
    # Tools / methodologies
    "git", "linux", "bash", "graphql", "rest", "microservices",
    "agile", "scrum", "TDD", "DDD",
]

#: Aliases that are normalised to canonical skill names.
SKILL_ALIASES: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "node": "nodejs",
    "node.js": "nodejs",
    "py": "python",
    "react.js": "react",
    "vue": "vue.js",
    "google cloud": "gcp",
    "amazon web services": "aws",
    "ms sql": "sql",
    "ms sql server": "sql",
    "tf": "tensorflow",
    "huggingface": "hugging face",
    "scikit learn": "scikit-learn",
}


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Lowercase, strip BOM, unicode-normalise and strip *text*."""
    if not text:
        return ""
    # Remove a leading BOM if present (issue 594 style)
    text = text.lstrip("\ufeff")
    text = unicodedata.normalize("NFKC", text)
    return text.lower().strip()


def normalize_skill(skill: str) -> str:
    """Map a skill string to its canonical form via alias lookup."""
    return SKILL_ALIASES.get(normalize_text(skill), normalize_text(skill))


def normalize_location(loc: str) -> str:
    """Normalize a location string for matching (lowercase, single-spaced)."""
    if not loc:
        return ""
    return re.sub(r"\s+", " ", normalize_text(loc)).strip()


# ---------------------------------------------------------------------------
# Skill extraction
# ---------------------------------------------------------------------------

def _skill_matches(haystack: str, skill: str) -> bool:
    """Check if *skill* appears as a word in *haystack*.

    Uses lookbehind/lookahead so that short skills like ``r`` are
    not matched as substrings of longer words (``recognizable``).
    """
    return bool(
        re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", haystack)
    )


def extract_skills(text: str) -> list[str]:
    """Extract known skill keywords from free-form *text*.

    Scans the normalised text for every entry in :data:`KNOWN_SKILLS`
    using word-boundary matching, and returns a de-duplicated,
    normalised list.
    """
    if not text:
        return []
    haystack = normalize_text(text)
    found: set[str] = set()
    for skill in KNOWN_SKILLS:
        if _skill_matches(haystack, skill):
            found.add(normalize_skill(skill))
    return sorted(found)


# ---------------------------------------------------------------------------
# Experience-level extraction
# ---------------------------------------------------------------------------

#: Ordered experience levels used by the scoring engine and text extractor.
#: ``principal`` is checked before ``lead`` so that "Principal Architect"
#: matches ``principal`` (via the keyword) rather than ``lead`` (via
#: ``architect``).
EXPERIENCE_LEVELS: list[str] = [
    "entry", "junior", "mid", "senior", "principal", "lead",
]

#: Patterns that map to each experience level.
_LEVEL_PATTERNS: dict[str, list[str]] = {
    "entry": ["entry level", "entry-level", "0-1 year", "0-2 years"],
    "junior": ["junior", "1-2 years", "1-3 years", "early career", "new grad"],
    "mid": ["mid level", "mid-level", "intermediate", "3-5 years", "3-7 years"],
    "senior": ["senior", "5+ years", "5-7 years", "10+ years", "experienced"],
    "principal": ["principal", "head of", "director", "cto", "vp"],
    "lead": ["lead", "staff", "architect", "8+ years"],
}


def extract_experience_level(text: str) -> str:
    """Detect an experience level keyword in *text*.

    Returns ``"unspecified"`` when no level can be determined.
    """
    if not text:
        return "unspecified"
    haystack = normalize_text(text)
    for level in EXPERIENCE_LEVELS:
        for pattern in _LEVEL_PATTERNS.get(level, []):
            if pattern in haystack:
                return level
    return "unspecified"


# ---------------------------------------------------------------------------
# Slug generation (non-ASCII safe)
# ---------------------------------------------------------------------------

# Transliteration map applied *before* NFKD so that letters with no
# decomposition (ae, oslash, aring) are still handled.
_TRANSLITERATION: str = str.maketrans({
    "æ": "ae", "ø": "oe", "å": "aa",
    "Æ": "ae", "Ø": "oe", "Å": "aa",
    "ß": "ss", "ñ": "n", "ç": "c",
})

_NON_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Generate a URL-safe slug from *text*.

    Non-ASCII characters are transliterated before ASCII folding so
    that, for example, ``oersted`` stays readable rather than
    becoming ``rsted``.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text).translate(_TRANSLITERATION)
    text = unicodedata.normalize("NFKD", text)
    ascii_text = text.encode("ascii", "ignore").decode("ascii")
    return _NON_SLUG.sub("-", ascii_text.lower()).strip("-")