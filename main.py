from data.db_sqlite import SchoolDBSqlite
from gui.app import SchoolApp
import sys
print("Choose UI: 1) Tkinter  2) PyQt")
choice = input("Enter 1 or 2: ").strip()

if choice == "1":
    import tkinter  
elif choice == "2":
    import main_qt  
else:
    print("Invalid choice")
    sys.exit(1)
if __name__ == "__main__":
    db = SchoolDBSqlite("school.db")  
    app = SchoolApp(db)
    app.mainloop()
