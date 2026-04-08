from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "contract_automation.db"
TEMPLATES_DIR = PROJECT_ROOT / "templates_storage"
CONFIG_FILE = PROJECT_ROOT / "app_config.json"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


def load_exports_dir() -> Path:
    """Load exports directory from config, fallback to default."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                exports_path = config.get("exports_dir")
                if exports_path:
                    path = Path(exports_path)
                    path.mkdir(parents=True, exist_ok=True)
                    return path
    except Exception:
        pass
    
    default_dir = PROJECT_ROOT / "exports"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir


def save_exports_dir(path: Path) -> None:
    """Save exports directory path to config file."""
    config = {}
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
    except Exception:
        pass
    
    config["exports_dir"] = str(path.resolve())
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


EXPORTS_DIR = load_exports_dir()
