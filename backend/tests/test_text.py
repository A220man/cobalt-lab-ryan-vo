"""Unit tests for text processing utilities (no database needed)."""
from app.core.text import (
    extract_experience_level,
    extract_skills,
    normalize_location,
    normalize_skill,
    normalize_text,
    slugify,
)


# ---------------------------------------------------------------------------
# normalize_text
# ---------------------------------------------------------------------------

class TestNormalizeText:
    def test_basic(self):
        assert normalize_text("Hello World") == "hello world"

    def test_unicode_normalization(self):
        assert normalize_text("Café") == "café"

    def test_strips_whitespace(self):
        assert normalize_text("  hello  ") == "hello"

    def test_empty_and_none(self):
        assert normalize_text("") == ""
        assert normalize_text(None) == ""

    def test_bom_removal(self):
        """BOM-prefixed text is handled (issue 594 style)."""
        assert normalize_text("\ufeffhello") == "hello"


# ---------------------------------------------------------------------------
# normalize_skill
# ---------------------------------------------------------------------------

class TestNormalizeSkill:
    def test_alias_js(self):
        assert normalize_skill("JS") == "javascript"

    def test_alias_py(self):
        assert normalize_skill("Py") == "python"

    def test_alias_node(self):
        assert normalize_skill("node.js") == "nodejs"

    def test_no_alias(self):
        assert normalize_skill("tensorflow") == "tensorflow"


# ---------------------------------------------------------------------------
# normalize_location
# ---------------------------------------------------------------------------

class TestNormalizeLocation:
    def test_basic(self):
        assert normalize_location("New York, NY") == "new york, ny"

    def test_multiple_spaces(self):
        assert normalize_location("San  Francisco") == "san francisco"


# ---------------------------------------------------------------------------
# extract_skills
# ---------------------------------------------------------------------------

class TestExtractSkills:
    def test_finds_known_skills(self):
        text = "Experience with Python, Docker, AWS, and machine learning."
        skills = extract_skills(text)
        assert "python" in skills
        assert "docker" in skills
        assert "aws" in skills
        assert "machine learning" in skills

    def test_deduplicates(self):
        text = "Python and python are the same"
        skills = extract_skills(text)
        assert skills.count("python") == 1

    def test_empty_text(self):
        assert extract_skills("") == []
        assert extract_skills(None) == []

    def test_no_matches(self):
        text = "A role with no recognizable skills mentioned."
        assert extract_skills(text) == []


# ---------------------------------------------------------------------------
# extract_experience_level
# ---------------------------------------------------------------------------

class TestExtractExperienceLevel:
    def test_senior(self):
        assert extract_experience_level("Senior Software Engineer") == "senior"

    def test_junior(self):
        assert extract_experience_level("Junior Developer") == "junior"

    def test_mid(self):
        assert extract_experience_level("Mid-level Engineer") == "mid"

    def test_principal(self):
        assert extract_experience_level("Principal Architect") == "principal"

    def test_unspecified(self):
        assert extract_experience_level("Software Engineer") == "unspecified"

    def test_empty(self):
        assert extract_experience_level("") == "unspecified"
        assert extract_experience_level(None) == "unspecified"


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_removes_extra_punctuation(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_strips_leading_trailing_hyphens(self):
        assert slugify("!!!Hello!!!") == "hello"

    def test_empty(self):
        assert slugify("") == ""

    def test_danish_characters(self):
        """Danish letters are transliterated before ASCII folding (issue 537)."""
        assert slugify("Ørsted") == "oersted"
        assert slugify("Åben Æble") == "aaben-aeble"
        assert slugify("Mærsk") == "maersk"
    def test_unicode_preserves_readable_form(self):
        assert slugify("Café") == "cafe"
        assert slugify("naïve") == "naive"  # ï → i in NFKD