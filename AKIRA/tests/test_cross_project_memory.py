import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    from core.memory import EnhancedMemoryStore
    from core.memory.cross_project import CrossProjectIndex
    from core.memory.pattern_extractor import PatternExtractor

    td = tempfile.mkdtemp(prefix="akira_cross_")
    root = os.path.join(td, "root")
    os.makedirs(root, exist_ok=True)

    proj1 = os.path.join(root, "proj1")
    proj2 = os.path.join(root, "proj2")
    os.makedirs(proj1, exist_ok=True)
    os.makedirs(proj2, exist_ok=True)

    _write(os.path.join(proj1, "requirements.txt"), "requests==2.31.0\n")
    _write(os.path.join(proj1, "main.py"), "print('ok')\n")
    _write(
        os.path.join(proj2, "package.json"),
        json.dumps({"dependencies": {"express": "^4.0.0"}}, ensure_ascii=True),
    )
    _write(os.path.join(proj2, "index.js"), "console.log('ok');\n")

    store = EnhancedMemoryStore(td, "http://localhost:1234/v1", "testkey", "gpt-4o")
    cross = CrossProjectIndex(store, data_dir=td, max_depth=2, max_projects=10)

    res1 = cross.index_roots([root, os.path.join(td, "missing")], user_id="u1")
    assert proj1 in res1.indexed
    assert proj2 in res1.indexed
    assert any("Missing root" in w for w in res1.warnings)

    res2 = cross.index_roots([root], user_id="u1")
    assert proj1 in res2.skipped and proj2 in res2.skipped

    # Symlink escape should be skipped
    outside = os.path.join(td, "outside")
    os.makedirs(outside, exist_ok=True)
    _write(os.path.join(outside, "main.py"), "print('outside')\n")
    link_path = os.path.join(root, "link_outside")
    created = False
    try:
        os.symlink(outside, link_path, target_is_directory=True)
        created = True
    except Exception:
        created = False
    if created and os.path.exists(link_path):
        res3 = cross.index_roots([root], user_id="u1")
        assert link_path not in res3.indexed
        assert link_path not in res3.skipped

    hits = cross.search("proj1")
    assert any("proj1" in h.get("path", "") for h in hits)

    extractor = PatternExtractor(td)
    summary = extractor.extract(limit=5)
    langs = [i["name"] for i in summary.get("top_languages", [])]
    techs = [i["name"] for i in summary.get("top_tech_stack", [])]
    deps = [i["name"] for i in summary.get("top_dependencies", [])]
    assert "python" in langs and "javascript" in langs
    assert "python" in techs and "nodejs" in techs
    assert "requests" in deps and "express" in deps


if __name__ == "__main__":
    main()
