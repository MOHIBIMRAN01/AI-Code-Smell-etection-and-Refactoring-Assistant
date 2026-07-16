from datetime import datetime, timedelta
from pathlib import Path

from config.database import Base, SessionLocal, engine
from models.db_models import Analysis
from services.cleanup_service import purge_expired_repo_clones
from utils.repo_archive import archive_repository, extract_repository


def test_archive_and_extract_repository(tmp_path):
    repo_src = tmp_path / "repo"
    repo_src.mkdir()
    (repo_src / "Main.java").write_text("public class Main {}", encoding="utf-8")

    archive_bytes = archive_repository(repo_src)
    assert archive_bytes

    restored = extract_repository(archive_bytes, tmp_path / "out")
    assert (restored / "Main.java").exists()


def test_purge_expired_repo_clones(tmp_path):
    repo_src = tmp_path / "repo"
    repo_src.mkdir()
    (repo_src / "Main.java").write_text("public class Main {}", encoding="utf-8")
    archive_bytes = archive_repository(repo_src)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        analysis = Analysis(
            id="analysis_test_purge",
            user_id="user-1",
            repository_url="https://example.com/repo.git",
            repository_name="repo",
            repository_path="db://analysis_test_purge",
            total_java_files=1,
            analyzed_classes=1,
            summary="test",
            repo_archive_blob=archive_bytes,
            repo_expires_at=datetime.utcnow() - timedelta(minutes=1),
        )
        db.add(analysis)
        db.commit()

        purged = purge_expired_repo_clones(db)
        assert purged == 1

        refreshed = db.query(Analysis).filter(Analysis.id == "analysis_test_purge").one()
        assert refreshed.repo_archive_blob is None
        assert refreshed.repo_expires_at is None
        assert refreshed.repository_path == "db://purged/analysis_test_purge"
    finally:
        db.query(Analysis).filter(Analysis.id == "analysis_test_purge").delete()
        db.commit()
        db.close()
