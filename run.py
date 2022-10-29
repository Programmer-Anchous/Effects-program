import sys
from pyautogui import size
from requests import get
from io import BytesIO

from PIL import Image
from PIL.ImageQt import ImageQt

from main import Ui_MainWindow
from load_image import Ui_Form
from effects import *

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtWidgets import QFileDialog


WINDOW_SIZE = (1238, 859)
IMAGE_FRAME_SIZE = (895, 775)
SCREEN_SIZE = tuple(size())
WINDOW_POSITIONS = (
            SCREEN_SIZE[0] // 2 - WINDOW_SIZE[0] // 2,
            SCREEN_SIZE[1] // 2 - WINDOW_SIZE[1] // 2
        )


class LoadImage(QMainWindow, Ui_Form):
    def __init__(self, parent):
         super(LoadImage, self).__init__(parent)
         self.setupUi(self)
         self.initUI()
        
    def initUI(self):
        WINDOW_SIZE = (601, 323)
        WINDOW_POSITIONS = (
            SCREEN_SIZE[0] // 2 - WINDOW_SIZE[0] // 2,
            SCREEN_SIZE[1] // 2 - WINDOW_SIZE[1] // 2
        )
        self.setGeometry(*WINDOW_POSITIONS, *WINDOW_SIZE)
        self.setFixedSize(*WINDOW_SIZE)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
    
    def initUI(self):
        self.open_url_form = LoadImage(self)

        self.setGeometry(*WINDOW_POSITIONS, *WINDOW_SIZE)
        self.setFixedSize(*WINDOW_SIZE)

        self.history = []
        self.sliders_history = []
        self.image_index = 0

        self.scaled_size = [None, None]

        # file open/save
        self.actionopen.triggered.connect(self.load_image)
        self.actionsave.triggered.connect(self.save_image)

        self.actionopen_from_URL.triggered.connect(self.load_from_url_form)
        self.open_url_form.load_url_btn.clicked.connect(self.load_from_url)

        # theme
        self.action_darktheme.triggered.connect(self.set_dark_theme)
        self.action_lighttheme.triggered.connect(self.set_light_theme)

        # connecting preset buttons
        self.btns_preset = [
            self.btn_preset_1,
            self.btn_preset_2,
            self.btn_preset_3,
            self.btn_preset_4,
            self.btn_preset_5,
            self.btn_preset_6,
            self.btn_preset_7,
            self.btn_preset_8,
            self.btn_preset_9,
            self.btn_preset_10
        ]

        for btn in self.btns_preset:
            btn.clicked.connect(self.set_presets)
        
        # connecting special effects buttons
        self.btn_box_blur.clicked.connect(self.set_box_blur)
        self.gaussian_blur.clicked.connect(self.set_gaussian_blur)
        self.btn_unsharp_mask.clicked.connect(self.set_unsharp_mask)
        self.btn_stereo.clicked.connect(self.set_stereo)
        self.btn_square_effect.clicked.connect(self.set_square_effect)
        self.btn_black_and_white.clicked.connect(self.set_black_and_white)
        self.btn_negative.clicked.connect(self.set_negative)

        # connecting back/reset buttons
        self.btn_reset.clicked.connect(self.recet_image)
        self.btn_back.clicked.connect(self.previous_image)

        # connecting sliders
        self.red_slider.valueChanged.connect(self.change_channels(self.red_slider, (1, 0, 0)))
        self.green_slider.valueChanged.connect(self.change_channels(self.green_slider, (0, 1, 0)))
        self.blue_slider.valueChanged.connect(self.change_channels(self.blue_slider, (0, 0, 1)))

        self.red_slider.sliderReleased.connect(self.apply_channel_changes(self.red_slider, (1, 0, 0)))
        self.green_slider.sliderReleased.connect(self.apply_channel_changes(self.green_slider, (0, 1, 0)))
        self.blue_slider.sliderReleased.connect(self.apply_channel_changes(self.blue_slider, (0, 0, 1)))

        self.rgb_sliders = [
            self.red_slider,
            self.green_slider,
            self.blue_slider
        ]
        
        self.alpha_slider.valueChanged.connect(self.change_transparency)
    
    def change_transparency(self):
        if self.check_if_image_opened():  # check for image opened
                return
        self.image_PIL = transparensy(self.image_PIL, self.sender().value())
        self.update_image()
    
    def change_channels(self, slider, chan):
        def inner():
            if self.check_if_image_opened():  # check for image opened
                return
            val = slider.value()
            rgb = tuple(map(lambda n: val if n == 1 else 50, chan))
            self.image.setPixmap(convert_to_qt(channels(self.image_PIL.resize(self.scaled_size), rgb)))
        return inner
    
    def apply_channel_changes(self, slider, chan):
        def inner():
            if self.check_if_image_opened():  # check for image opened
                return
            val = slider.value()
            rgb = tuple(map(lambda n: val if n == 1 else 50, chan))
            self.image_PIL = channels(self.image_PIL, rgb)
            self.update_image()
            self.alpha_slider.setValue(255)  # we cannot change RGB-channel with changed alpha channel
        return inner
    
    def set_box_blur(self):
        if self.check_if_image_opened():  # check for image opened
                return
        raduis = self.spin_box_blur_raduis.value()
        self.image_PIL = box_blur(self.image_PIL, raduis)
        self.update_image()

    def set_gaussian_blur(self):
        if self.check_if_image_opened():  # check for image opened
                return
        raduis = self.spin_gaussian_blur_raduis.value()
        self.image_PIL = gaussian_blur(self.image_PIL, raduis)
        self.update_image()
    
    def set_unsharp_mask(self):
        if self.check_if_image_opened():  # check for image opened
                return
        raduis = self.unsharp_mask_raduis_spin.value()
        percent = self.unsharp_mask_percent_spin.value()
        threshold = self.unsharp_mask_threshold_spin.value()
        self.image_PIL = unsharp_mask(self.image_PIL, raduis, percent, threshold)
        self.update_image()
    
    def set_stereo(self):
        if self.check_if_image_opened():  # check for image opened
                return
        delta = self.stereo_delta_spin.value()
        self.image_PIL = stereo_effect(self.image_PIL, delta)
        self.update_image()
    
    def set_square_effect(self):
        if self.check_if_image_opened():  # check for image opened
                return
        area = self.square_effect_area_spin.value()
        self.image_PIL = lightest_pixel_effect(self.image_PIL, area)
        self.update_image()
    
    def set_black_and_white(self):
        if self.check_if_image_opened():  # check for image opened
                return
        self.image_PIL = black_and_white_effect(self.image_PIL)
        self.update_image()
    
    def set_negative(self):
        if self.check_if_image_opened():  # check for image opened
                return
        self.image_PIL = negative_effect(self.image_PIL)
        self.update_image()

    def set_presets(self):
        if self.check_if_image_opened():  # check for image opened
                return
        self.image_PIL = preset_filters(self.image_PIL, filters[self.sender().text()])
        self.update_image()
    
    def convert_image(self, image):
        self.history = []
        self.sliders_history = []


        # делаем изображение меньше, если оно не влезает в рамки
        width, height = image.size

        scale1 = scale2 = 1

        if width > IMAGE_FRAME_SIZE[0]:
            scale1 = IMAGE_FRAME_SIZE[0] / width
        if height > IMAGE_FRAME_SIZE[1]:
            scale2 = IMAGE_FRAME_SIZE[1] / height
        
        scale = scale1 if scale1 < scale2 else scale2
        self.scaled_size = (int(width * scale), int(height * scale))
    
        # self.image_PIL = self.image_PIL.resize(self.scaled_size)
        self.origin_image = self.image_PIL.copy()
        self.history.append(self.origin_image)
        #________________________________________

        self.image.move(0, 0)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.update_image()
        self.recet_image()

    def load_image(self):
        filename = QFileDialog.getOpenFileName(
            self, 'Choose photo', '',
            'Pictures (*.png *.jpg);; Pictures (*.png);; Pictures (*.jpg)')[0].strip()
        if not filename:
            return
        # filename = "/home/anchous/Pictures/waves.png"
        self.image_PIL = Image.open(filename)

        self.convert_image(self.image_PIL)

    def save_image(self):
        filename = QFileDialog.getSaveFileName(
            self, 'Save photo', '',
            'Pictures (*.png);; Pictures (*.jpg)')[0].strip()
        if not filename:
            return
        self.image_PIL.save(filename)

    def load_from_url_form(self):
        self.open_url_form.show()
    
    def load_from_url(self):
        try:
            url = self.open_url_form.url_text.toPlainText()
            response = get(url)
            self.image_PIL = Image.open(BytesIO(response.content))

            self.convert_image(self.image_PIL)
            self.open_url_form.url_text.setPlainText("")
            self.open_url_form.close()
        except Exception:
            return

    def update_image(self):
        self.history.append(self.image_PIL)
        self.sliders_history.append(
            (
                self.alpha_slider.value(),
                self.red_slider.value(),
                self.green_slider.value(),
                self.blue_slider.value()
            )
        )
        self.image_index += 1
        self.image.setPixmap(convert_to_qt(self.image_PIL.resize(self.scaled_size)))
    
    def previous_image(self):
        if self.image_index > 0:
            del self.history[self.image_index:]
            del self.sliders_history[self.image_index:]
            self.image_index -= 1
            self.image_PIL = self.history[self.image_index]

            self.alpha_slider.setValue(self.sliders_history[-1][0])
            self.red_slider.setValue(self.sliders_history[-1][1])
            self.green_slider.setValue(self.sliders_history[-1][2])
            self.blue_slider.setValue(self.sliders_history[-1][3])

            # updating image without history logging
            self.image.setPixmap(convert_to_qt(self.image_PIL.resize(self.scaled_size)))

    def recet_image(self):
        self.image_PIL = self.origin_image.copy()
        for sl in self.rgb_sliders:
            sl.setValue(50)
        self.alpha_slider.setValue(255)
        self.update_image()

        self.image_index = 0
        self.history = [self.image_PIL]
        self.sliders_history = [(255, 50, 50, 50)]

    def set_dark_theme(self):
        self.setStyleSheet("background-color: #353535;\ncolor: #dddddd;")
        self.frame.setStyleSheet("background-color: #282828;")
        self.tabs_effects.setStyleSheet("background-color: #353535;\ncolor: #dddddd;")
    
    def set_light_theme(self):
        self.setStyleSheet("background-color: #dddddd;\ncolor: #202020;")
        self.frame.setStyleSheet("background-color: #cccccc;")
        self.tabs_effects.setStyleSheet("background-color: #dddddd;\ncolor: #202020;")

    def check_if_image_opened(self):
        try:
            self.image_PIL  # check if image opened
            return False
        except AttributeError:
            return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())