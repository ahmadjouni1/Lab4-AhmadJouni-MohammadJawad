from PyQt5 import QtWidgets
from data.db_sqlite import SchoolDBSqlite
from gui_qt.app_qt import SchoolWindow

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    db = SchoolDBSqlite("school.db")  # creates file if missing
    win = SchoolWindow(db)
    win.show()
    sys.exit(app.exec_())
