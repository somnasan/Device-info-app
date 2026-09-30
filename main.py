from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
import socket


def get_ip():
    """Получаем локальный IP-адрес устройства."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Не удалось получить IP"


def get_device_info():
    """Собираем информацию об устройстве."""
    info = {}

    if platform == "android":
        from jnius import autoclass

        # Версия Android
        Build_VERSION = autoclass("android.os.Build$VERSION")
        info["Версия Android"] = Build_VERSION.RELEASE

        # Модель и производитель
        Build = autoclass("android.os.Build")
        info["Модель"] = Build.MODEL
        info["Производитель"] = Build.MANUFACTURER
        info["Устройство"] = Build.DEVICE

        # Разрешение экрана
        from android.runnable import run_on_ui_thread
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        metrics = activity.getResources().getDisplayMetrics()
        info["Экран"] = f"{metrics.widthPixels} x {metrics.heightPixels} px"
        info["Плотность"] = f"{metrics.densityDpi} dpi"

        # Батарея
        try:
            Context = autoclass("android.content.Context")
            Intent = autoclass("android.content.Intent")
            IntentFilter = autoclass("android.content.IntentFilter")
            battery = activity.registerReceiver(None, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            level = battery.getIntExtra("level", -1)
            scale = battery.getIntExtra("scale", -1)
            if level != -1 and scale != -1:
                info["Батарея"] = f"{int(level * 100 / scale)}%"
        except Exception:
            info["Батарея"] = "Недоступно"

    else:
        # На компьютере (для теста)
        info["Платформа"] = platform
        info["Примечание"] = "Полная информация доступна только на Android"

    # IP-адрес — работает везде
    info["IP-адрес"] = get_ip()

    return info


class InfoScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)

        self.label = Label(
            text="Нажми кнопку, чтобы получить информацию",
            size_hint_y=None,
            halign="left",
            valign="middle",
            font_size="16sp",
        )
        self.label.bind(
            width=lambda *x: setattr(self.label, "text_size", (self.label.width, None))
        )

        scroll = ScrollView()
        scroll.add_widget(self.label)
        self.add_widget(scroll)

        btn = Button(text="Показать информацию", size_hint_y=None, height=60)
        btn.bind(on_press=self.show_info)
        self.add_widget(btn)

    def show_info(self, instance):
        info = get_device_info()
        text = "\n".join(f"[b]{k}:[/b] {v}" for k, v in info.items())
        self.label.text = text
        self.label.markup = True


class DeviceInfoApp(App):
    def build(self):
        self.title = "Инфо об устройстве"
        return InfoScreen()


if __name__ == "__main__":
    DeviceInfoApp().run()
