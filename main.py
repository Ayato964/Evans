import sys
# QWidgetを追加でインポートします
from PySide6.QtWidgets import QApplication, QMainWindow
# QCloseEventをインポートしておくと、型ヒントが使えて便利です
from PySide6.QtGui import QCloseEvent
from evans import _AbstractUI, Evans


# --- メインウィンドウのクラス ---
class MainWindow(QMainWindow):
    def __init__(self, first_page: _AbstractUI):
        super().__init__()

        # 【修正点】渡されたページオブジェクトへの参照を保持します。
        # これにより、UIオブジェクトが予期せず削除されるのを防ぎます。
        self.current_page = first_page

        self.setCentralWidget(self.current_page.get_ui())
        self.setWindowTitle("Application")  # ウィンドウのタイトルを設定
        self.resize(800, 600)

    def closeEvent(self, event: QCloseEvent):
        """
        ウィンドウの「×」ボタンが押されたときに自動的に呼び出されるメソッド。
        """
        print("closeEventが呼び出されました。")
        QApplication.instance().quit()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Evansページを作成
    evans_page = Evans()

    # MainWindowにページを渡してインスタンス化
    window = MainWindow(evans_page)

    window.show()
    sys.exit(app.exec())
