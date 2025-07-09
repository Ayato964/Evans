import os.path
import sys
from pathlib import Path
from sys import meta_path
from time import sleep

from PySide6.QtGui import QPixmap

from controller import MusicList
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QPropertyAnimation, QParallelAnimationGroup, QRect, QEasingCurve, QAbstractAnimation, QObject

class _AbstractUI(QObject):
    def __init__(self, ui_path):
        super().__init__()
        loader = QUiLoader()
        self.ui: QWidget = loader.load(ui_path)

    def get_ui(self):
        return self.ui

# --- Evansページのクラス ---
class Evans(_AbstractUI):
    def __init__(self):
        super().__init__("scene/evans.ui")
        self.music_list_manager = MusicList()
        self.chooseMenu = self.ui.findChild(QWidget,"chooseMenu")
        print(self.chooseMenu.children())
        self.update_music(self.music_list_manager.get_idx())

        next = self.ui.findChild(QPushButton, "next")
        next.clicked.connect(self.next)

        back = self.ui.findChild(QPushButton, "back")
        back.clicked.connect(self.back)


    def back(self):
        image = self.chooseMenu.findChild(QLabel, "song_Image")
        if not image:
            return
        # アニメーションの終了位置を計算 (chooseMenuの右端の外)
        start_rect = image.geometry()
        end_rect = QRect(start_rect)
        end_rect.moveLeft(-self.chooseMenu.width())  # 右外へ

        # スライドアウト（フェードアウトしながら右へ）
        self.slide_animation(image,
                             start_rect=start_rect,
                             end_rect=end_rect,
                             duration=500,  # 少し速めに
                             start_val=1,  # 不透明から
                             end_val=0,
                             finish_action=self.back_2_animation)  # 透明へ

    def back_2_animation(self):
        # 1. 曲のインデックスを更新し、画像などの情報を更新
        self.music_list_manager.set_back()
        self.update_music(self.music_list_manager.get_idx())

        # 2. 新しくなった画像を、今度は左外からスライドインさせる
        image = self.chooseMenu.findChild(QLabel, "song_Image")
        if not image:
            return

        # スライドインの開始位置と終了位置を計算
        end_rect = QRect(image.geometry())  # 本来の位置
        end_rect.moveLeft(end_rect.width() - 400)
        start_rect = QRect(image.geometry())
        start_rect.moveLeft(end_rect.width() + 1000)  # 左外から

        # スライドイン（フェードインしながら元の位置へ）
        self.slide_animation(image,
                             start_rect=start_rect,
                             end_rect=end_rect,
                             duration=500,
                             start_val=0,  # 透明から
                             end_val=1,
                             finish_action=lambda : self.music_list_manager.play())  # 不透明へ

    def next(self):
        """ 現在の画像を右へスライドアウトさせる """
        image = self.chooseMenu.findChild(QLabel, "song_Image")
        if not image:
            return

        # アニメーションの終了位置を計算 (chooseMenuの右端の外)
        start_rect = image.geometry()
        end_rect = QRect(start_rect)
        end_rect.moveLeft(self.chooseMenu.width())  # 右外へ
        # スライドアウト（フェードアウトしながら右へ）

        self.slide_animation(image,
                             start_rect=start_rect,
                             end_rect=end_rect,
                             duration=500,  # 少し速めに
                             start_val=1,  # 不透明から
                             end_val=0,
                             finish_action=self._on_slide_out_finished)  # 透明へ

    def _on_slide_out_finished(self):
        """ スライドアウト完了後に呼ばれる処理 """

        # 1. 曲のインデックスを更新し、画像などの情報を更新
        self.music_list_manager.set_next()
        self.update_music(self.music_list_manager.get_idx())

        # 2. 新しくなった画像を、今度は左外からスライドインさせる
        image = self.chooseMenu.findChild(QLabel, "song_Image")
        if not image:
            return

        # スライドインの開始位置と終了位置を計算
        end_rect = QRect(image.geometry())  # 本来の位置
        end_rect.moveLeft(-end_rect.width() + 650)
        start_rect = QRect(image.geometry())
        start_rect.moveLeft(-end_rect.width() - 1000)  # 左外から

        # スライドイン（フェードインしながら元の位置へ）
        self.slide_animation(image,
                             start_rect=start_rect,
                             end_rect=end_rect,
                             duration=500,
                             start_val=0,  # 透明から
                             end_val=1,
                             finish_action=lambda : self.music_list_manager.play())  # 不透明へ


    def update_music(self, index):
        meta_data = self.music_list_manager[index]

        image_frame: QLabel = self.chooseMenu.findChild(QLabel, "song_Image")
        image_frame.setPixmap(QPixmap(os.path.join(meta_data["root"], meta_data["media"]["image"])))
        image_frame.setScaledContents(True)

        music_title: QLabel = self.chooseMenu.findChild(QLabel, "music_title")
        music_title.setText(meta_data["media"]["music"])

    def slide_animation(self,target_widget, start_rect, end_rect, duration=1000, start_val=0, end_val=1, finish_action=None):

        if not target_widget:
            print("エラー: 'song_Image' という名前のウィジェットが見つかりません。")
            return

        # 1. 透明度エフェクトの準備
        self.opacity_effect = QGraphicsOpacityEffect(target_widget)
        target_widget.setGraphicsEffect(self.opacity_effect)

        # 2. アニメーショングループの作成
        self.animation_group = QParallelAnimationGroup(self)

        # 3. 位置のアニメーションを作成
        anim_geometry = QPropertyAnimation(target_widget, b"geometry")
        anim_geometry.setDuration(duration)
        anim_geometry.setStartValue(start_rect)
        anim_geometry.setEndValue(end_rect)
        anim_geometry.setEasingCurve(QEasingCurve.OutCubic)

        # 4. 透明度のアニメーションを作成
        anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_opacity.setDuration(duration)
        anim_opacity.setStartValue(start_val)  # 開始時: 透明
        anim_opacity.setEndValue(end_val)  # 終了時: 不透明
        anim_opacity.setEasingCurve(QEasingCurve.InCubic)  # フェードインは徐々に表示される感じが良い場合が多い

        # 5. グループに2つのアニメーションを追加
        self.animation_group.addAnimation(anim_geometry)
        self.animation_group.addAnimation(anim_opacity)

        # 6. グループアニメーションを開始
        self.animation_group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        if finish_action is not None:
            self.animation_group.finished.connect(finish_action)