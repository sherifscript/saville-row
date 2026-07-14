"""Shared pytest fixtures and path setup for the saville-row test suite."""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "skills", "cv-tailor", "scripts")
SHARED_SCRIPTS = os.path.join(REPO_ROOT, "shared", "scripts")
TEMPLATE = os.path.join(REPO_ROOT, "templates", "OPUS", "full_template.docx")

# Make the cv-tailor and shared scripts importable as plain modules.
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, SHARED_SCRIPTS)


def minimal_content_map(**overrides):
    """A valid content_map with one experience role. Tests override fields."""
    cm = {
        "candidate_name": "Test Candidate",
        "tagline": "Senior Analyst  |  Research",
        "contact_line_1": "City, Country | +1 000 | test@example.com",
        "personal_site": "example.com",
        "linkedin_url": "linkedin.com/in/test",
        "contact_line_2_suffix": "Available immediately",
        "summary": "A three sentence summary. It has scope. It has a signal.",
        "core_skills": [{"label": "Skill", "description": "a description"}],
        "experiences": [{
            "title": "Senior Analyst", "dates": "2023-Present",
            "company": "Acme", "location": "City",
            "bullets": ["Did a plain thing."],
        }],
        "degrees": [
            {"name": "MSc", "date": "2018",
             "institution": "A University", "location": "City",
             "bullets": ["A degree bullet."]},
            {"name": "BA", "date": "2016",
             "institution": "B College", "location": "City",
             "bullets": ["Another degree bullet."]},
        ],
        "additional": [{"label": "Languages", "description": "English"}],
    }
    cm.update(overrides)
    return cm
