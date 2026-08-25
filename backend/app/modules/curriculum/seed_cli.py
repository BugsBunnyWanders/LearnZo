"""CLI tool to seed or re-seed curriculum and skill graph."""

import sys

import app.modules.curriculum.models  # noqa: F401
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.modules.curriculum.service import CurriculumService


def run_seed(force: bool = False) -> None:
    """Execute database seeding for curriculum."""
    setup_logging()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        service = CurriculumService(db)
        res = service.seed_curriculum(force=force)
        print(f"✅ {res.message}")
        print(f"   Skills: {res.skills_seeded}")
        print(f"   Topics: {res.topics_seeded}")
        print(f"   Prerequisites: {res.prerequisites_seeded}")
        print(f"   Resources: {res.resources_seeded}")
    finally:
        db.close()


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    run_seed(force=force_flag)
