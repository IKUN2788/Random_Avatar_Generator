import sys
import random
import string
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QByteArray, Qt, QSize
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter, QImage, QColor

# Try to import multiavatar
try:
    # First try importing the submodule (common structure)
    from multiavatar.multiavatar import multiavatar
    print(f"Successfully imported multiavatar from submodule.")
except ImportError:
    # Fallback: try importing the package directly
    try:
        import multiavatar
        if hasattr(multiavatar, 'multiavatar'):
            multiavatar = multiavatar.multiavatar
            print(f"Successfully imported multiavatar from package.")
        else:
            raise ImportError("Could not find multiavatar function in package")
    except Exception as e:
        print(f"Error importing multiavatar: {e}")
        print("Please ensure multiavatar is installed: pip install multiavatar")
        sys.exit(1)

# Debug/Verify multiavatar works
try:
    test_svg = multiavatar("test_verification", None, None)
    if test_svg:
        print("Multiavatar verification successful: Generated SVG sample.")
except Exception as e:
    print(f"Multiavatar verification failed: {e}")


class AvatarGenerator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("随机头像生成器")
        self.resize(400, 500)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)

        # 1. Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入文字生成头像...")
        self.input_field.textChanged.connect(self.generate_avatar)
        
        self.random_btn = QPushButton("随机生成")
        self.random_btn.clicked.connect(self.generate_random)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.random_btn)
        
        layout.addLayout(input_layout)

        # 2. Avatar Display
        # Using a container to center the SVG widget
        display_container = QWidget()
        display_layout = QVBoxLayout(display_container)
        display_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.svg_widget = QSvgWidget()
        self.svg_widget.setFixedSize(300, 300)
        
        display_layout.addWidget(self.svg_widget)
        layout.addWidget(display_container)

        # 3. Save buttons
        save_layout = QHBoxLayout()
        self.save_svg_btn = QPushButton("保存为 SVG")
        self.save_svg_btn.clicked.connect(self.save_svg)
        
        self.save_png_btn = QPushButton("保存为 PNG")
        self.save_png_btn.clicked.connect(self.save_png)
        
        save_layout.addWidget(self.save_svg_btn)
        save_layout.addWidget(self.save_png_btn)
        
        layout.addLayout(save_layout)

        # Initial generation
        self.current_svg = ""
        self.generate_random()

    def generate_random(self):
        # Generate a random string
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.input_field.setText(random_str)
        # generate_avatar will be called automatically due to textChanged signal

    def generate_avatar(self, text=None):
        if text is None:
            text = self.input_field.text()
        
        if not text:
            self.svg_widget.load(QByteArray())
            self.current_svg = ""
            return

        try:
            # Generate SVG using multiavatar
            svg_code = multiavatar(text, None, None)
            self.current_svg = svg_code
            
            # Load into widget
            self.svg_widget.load(QByteArray(svg_code.encode('utf-8')))
        except Exception as e:
            print(f"Error generating avatar: {e}")

    def save_svg(self):
        if not self.current_svg:
            QMessageBox.warning(self, "警告", "没有可保存的头像")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "保存 SVG", "", "SVG Files (*.svg)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_svg)
                QMessageBox.information(self, "成功", "SVG 保存成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def save_png(self):
        if not self.current_svg:
            QMessageBox.warning(self, "警告", "没有可保存的头像")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "保存 PNG", "", "PNG Files (*.png)")
        if file_path:
            try:
                # Render SVG to QImage
                renderer = QSvgRenderer(QByteArray(self.current_svg.encode('utf-8')))
                image = QImage(1024, 1024, QImage.Format.Format_ARGB32)
                image.fill(QColor(0, 0, 0, 0))  # Transparent background
                
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
                
                if image.save(file_path):
                    QMessageBox.information(self, "成功", "PNG 保存成功")
                else:
                    QMessageBox.critical(self, "错误", "保存 PNG 失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AvatarGenerator()
    window.show()
    sys.exit(app.exec())