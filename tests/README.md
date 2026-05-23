# Tests

Small pytest suite guarding the framework's named failure modes.

```
pip install -r ../requirements.txt pytest
python -m pytest tests/ -v
```

- `test_autoescape.py` — an `&` in the content map must survive the render
  (the 2026-04-28 ampersand-strip failure mode).
- `test_bold_runs.py` — `**bold**` markers in experience bullets must become
  real `<w:b/>` runs, and must never leak literal `**` (the 2026-05-11
  empty-bold regression).

CI runs these on every push — see `.github/workflows/ci.yml`.
