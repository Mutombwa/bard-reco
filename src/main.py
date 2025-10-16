import pandas as pd
from tkinter import Tk, filedialog, messagebox
from gui import MainApp
from reconciliation import reconcile_transactions

def main():
    # Initialize the main application
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()