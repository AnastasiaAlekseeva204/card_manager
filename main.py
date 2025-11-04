import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui'))

from ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()