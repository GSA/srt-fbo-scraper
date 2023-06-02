from pathlib import Path

base_dir = Path(__file__).parent.parent.parent
log_path = Path(base_dir, "logs")
alembic_path = Path(base_dir, "alembic")
bin_path = Path(base_dir, "bin")
sql_path = Path(base_dir, "sql")
