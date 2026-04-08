from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from contract_automation.config import DB_PATH
from contract_automation.data.database import Database
from contract_automation.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    db = Database(DB_PATH)

    window = MainWindow(db)
    window.show()

    exit_code = app.exec()
    db.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
