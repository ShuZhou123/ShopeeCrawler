import sys

from PyQt5.QtWidgets import QApplication

from backend import Main


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = Main()
    main_win.show()
    sys.exit(app.exec_())