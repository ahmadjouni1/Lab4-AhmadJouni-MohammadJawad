# 🎓 School Manager – Tkinter & PyQt Project  

## 📖 Overview  
This project is a collaborative exercise for **Software Tools Lab (Fall 2024–2025)** at the **American University of Beirut (AUB)**.  
The goal is to practice **Git/GitHub collaboration** while building a **School Management System** with two separate user interfaces:  

- **Tkinter UI** – implemented by Student 1  
- **PyQt UI** – implemented by Student 2  

Both interfaces connect to a **shared backend and database**, ensuring consistent functionality while providing flexibility in GUI frameworks.  

---

## ✨ Features  
✅ Tkinter interface for school management  
✅ PyQt interface for the same backend logic  
✅ SQLite database integration  
✅ Modular code structure with `models`, `utils`, `gui`, and `docs`  
✅ Full Sphinx documentation generated under `/docs`  

---

## 📂 Project Structure  
Lab4-AhmadJouni-MohammadJawad/
│── data/ # Database files (SQLite)
│── docs/ # Sphinx-generated documentation
│── gui/ # Tkinter interface implementation
│── gui_qt/ # PyQt interface implementation
│── models/ # Data models (Student, Instructor, Course, etc.)
│── utils/ # Helper utilities & validators
│── main.py # Entry point (Tkinter)
│── main_qt.py # Entry point (PyQt)
│── Makefile # Automation for docs/build
│── README.md # Project documentation (this file)
