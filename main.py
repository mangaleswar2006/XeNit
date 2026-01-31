import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
# Fix for "ImportError: QtWebEngineWidgets must be imported before a QCoreApplication instance is created"
try:
    from PyQt6 import QtWebEngineWidgets
except ImportError:
    pass # Handle gracefully or improved error

from browser.styles import GLOBAL_STYLES
# We will import BrowserWindow later once created, to avoid immediate error during batch creation
# from browser.window import BrowserWindow 

def main():
    # Enable High DPI display
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # PERFORMANCE OPTIMIZATIONS
    # Use Desktop OpenGL (smoother than ANGLE on some systems)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
    # Share contexts for faster WebGL
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

    app = QApplication(sys.argv)
    app.setApplicationName("XeNit Browser")
    app.setOrganizationName("GoogleDeepmind_Agent")
    
    app.setStyleSheet(GLOBAL_STYLES)

    # Defer import to allow file creation in same step if possible, 
    # but practically we need browser.window to exist.
    from browser.window import BrowserWindow
    
    window = BrowserWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
