from data.db_sqlite import SchoolDBSqlite
from gui.app import SchoolApp

if __name__ == "__main__":
    db = SchoolDBSqlite("school.db")  # creates file if missing
    app = SchoolApp(db)
    app.mainloop()
