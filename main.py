import sys

def main():
    try:
        import tkinter
    except ImportError:
        sys.exit('Install tkinter first')
    from calc.ui import CalcApp
    app = CalcApp()
    app.mainloop()

if __name__ == '__main__':
    main()
