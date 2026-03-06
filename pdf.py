import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QFileDialog,
    QMessageBox, QVBoxLayout, QToolBar, QAction,
    QLineEdit, QStatusBar, QInputDialog
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt


class PDFEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer & Highlighter Pro")
        self.setGeometry(100, 100, 1000, 700)

        self.doc = None
        self.current_page = 0
        self.zoom = 1.0
        self.file_path = None

        self.init_ui()
        self.apply_styles()

    # ---------------- UI ----------------
    def init_ui(self):
        self.pdf_label = QLabel("📄 Open a PDF to start")
        self.pdf_label.setAlignment(Qt.AlignCenter)

        self.toolbar = QToolBar()

        self.open_action = QAction("Open", self)
        self.prev_action = QAction("◀ Prev", self)
        self.next_action = QAction("Next ▶", self)
        self.zoom_in_action = QAction("Zoom +", self)
        self.zoom_out_action = QAction("Zoom -", self)
        self.highlight_action = QAction("Highlight Page", self)
        self.search_action = QAction("Search", self)
        self.save_action = QAction("Save", self)

        self.toolbar.addActions([
            self.open_action, self.prev_action, self.next_action,
            self.zoom_in_action, self.zoom_out_action,
            self.highlight_action, self.search_action, self.save_action
        ])

        self.status = QStatusBar()

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.pdf_label, 1)
        layout.addWidget(self.status)

        self.setLayout(layout)

        # Signals
        self.open_action.triggered.connect(self.open_pdf)
        self.prev_action.triggered.connect(self.prev_page)
        self.next_action.triggered.connect(self.next_page)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.highlight_action.triggered.connect(self.highlight_page)
        self.search_action.triggered.connect(self.search_text)
        self.save_action.triggered.connect(self.save_pdf)

    # ---------------- PDF Logic ----------------
    def open_pdf(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)"
        )
        if self.file_path:
            try:
                self.doc = fitz.open(self.file_path)
                self.current_page = 0
                self.zoom = 1.0
                self.render_page()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def render_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.current_page)
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)

        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)

        self.pdf_label.setPixmap(QPixmap.fromImage(image))
        self.status.showMessage(
            f"Page {self.current_page + 1} / {len(self.doc)} | Zoom {int(self.zoom * 100)}%"
        )

    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.render_page()

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.render_page()

    def zoom_in(self):
        self.zoom += 0.1
        self.render_page()

    def zoom_out(self):
        if self.zoom > 0.2:
            self.zoom -= 0.1
            self.render_page()

    # ---------------- Features ----------------
    def highlight_page(self):
        if not self.doc:
            return
        page = self.doc.load_page(self.current_page)
        for word in page.get_text("words"):
            rect = fitz.Rect(word[:4])
            page.add_highlight_annot(rect)
        QMessageBox.information(self, "Done", "Page highlighted")
        self.render_page()

    def search_text(self):
        if not self.doc:
            return

        text, ok = QInputDialog.getText(self, "Search", "Enter text:")
        if ok and text:
            page = self.doc.load_page(self.current_page)
            matches = page.search_for(text)

            if not matches:
                QMessageBox.information(self, "Search", "No matches found.")
                return

            for rect in matches:
                page.add_highlight_annot(rect)

            QMessageBox.information(
                self, "Search", f"Found {len(matches)} matches."
            )
            self.render_page()

    def save_pdf(self):
        if not self.doc:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "", "PDF Files (*.pdf)"
        )
        if path:
            self.doc.save(path)
            QMessageBox.information(self, "Saved", "PDF saved successfully.")

    # ---------------- Styling ----------------
    def apply_styles(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #ffffff;
            font-size: 14px;
        }
        QToolBar {
            background: #1e1e1e;
            spacing: 6px;
        }
        QToolButton {
            background: #2a2a2a;
            border-radius: 6px;
            padding: 6px;
        }
        QToolButton:hover {
            background: #00c853;
            color: black;
        }
        QLabel {
            background: #000000;
            border-radius: 10px;
        }
        QStatusBar {
            background: #1e1e1e;
        }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFEditor()
    window.show()
    sys.exit(app.exec_())
