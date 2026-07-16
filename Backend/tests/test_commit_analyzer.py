from pathlib import Path

from git import Repo

from commit_analyzer import CommitAnalyzer


def test_commit_analyzer_skips_full_diff_collection_for_history(tmp_path):
    repo_dir = tmp_path / "repo"
    repo = Repo.init(repo_dir)
    (repo_dir / "src").mkdir()
    java_file = repo_dir / "src" / "Example.java"
    java_file.write_text("class Example {}\n", encoding="utf-8")
    repo.index.add([str(java_file.relative_to(repo_dir))])
    repo.index.commit("initial commit")

    analyzer = CommitAnalyzer(repo_dir)

    def fail_diff_collection(*args, **kwargs):
        raise AssertionError("full diff collection should not be required")

    analyzer._collect_diff = fail_diff_collection  # type: ignore[assignment]

    commits = analyzer.get_commits_for_file("src/Example.java")

    assert commits
    assert commits[0].modified_files == ["src/Example.java"]
