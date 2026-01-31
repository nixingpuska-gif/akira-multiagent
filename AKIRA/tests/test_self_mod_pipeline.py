import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    from core.self_mod.analyzer import SelfModAnalyzer
    from core.self_mod.patcher import SelfModPatcher
    from core.self_mod.sandbox import SelfModSandbox

    td = tempfile.mkdtemp(prefix="akira_selfmod_")
    target_dir = os.path.join(td, "proj")
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "file.txt")
    with open(target_file, "w", encoding="utf-8") as f:
        f.write("line1\n")

    analyzer = SelfModAnalyzer(max_files=10, max_depth=2)
    analysis = analyzer.analyze(target_dir, "Fix typo in file.")
    data = analysis.to_dict()
    assert data.get("risk_level") in ("low", "medium", "high")
    assert target_file in data.get("files", [])

    diff_text = (
        f"--- a/{target_file}\n"
        f"+++ b/{target_file}\n"
        "@@ -1,1 +1,1 @@\n"
        "-line1\n"
        "+line1_fixed\n"
    )
    patcher = SelfModPatcher(td)
    patch_result = patcher.create_patch(target_file, "Fix typo", diff_text)
    assert os.path.exists(patch_result.patch_path)

    sandbox = SelfModSandbox(allowed_roots=[td])
    ok = sandbox.validate_diff_file(patch_result.patch_path)
    assert ok.ok is True

    bad_diff = (
        "--- a/C:\\Windows\\system32\\drivers\\etc\\hosts\n"
        "+++ b/C:\\Windows\\system32\\drivers\\etc\\hosts\n"
        "@@ -1,1 +1,1 @@\n"
        "-x\n"
        "+y\n"
    )
    bad = sandbox.validate_diff(bad_diff)
    assert bad.ok is False

    non_ascii = bad_diff + "\u2603\n"
    bad2 = sandbox.validate_diff(non_ascii)
    assert bad2.ok is False

    secret_path = os.path.join(td, ".env")
    secret_diff = (
        f"--- a/{secret_path}\n"
        f"+++ b/{secret_path}\n"
        "@@ -1,1 +1,1 @@\n"
        "-X=1\n"
        "+X=2\n"
    )
    secret = sandbox.validate_diff(secret_diff)
    assert secret.ok is False


if __name__ == "__main__":
    main()
