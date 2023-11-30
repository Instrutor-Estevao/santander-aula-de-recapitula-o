import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from threading import Thread
import urllib.parse

class AnalogStick(BoxLayout):
    def __init__(self, **kwargs):
        super(AnalogStick, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        # Adiciona os analógicos virtuais à esquerda
        self.add_widget(Image(source='analog_stick_bg.png', size_hint=(None, None), size=(150, 150)))
        self.slider_x = Slider(min=-1, max=1, value=0, size_hint=(None, None), size=(150, 10))
        self.slider_y = Slider(min=-1, max=1, value=0, orientation='vertical', size_hint=(None, None), size=(10, 150))

        self.slider_x.bind(value=self.update_values)
        self.slider_y.bind(value=self.update_values)

        self.add_widget(self.slider_x)
        self.add_widget(self.slider_y)

        # Mapeamento entre texto do botão e comando correspondente
        self.button_commands = {
            '✕': 'CROSS',
            '□': 'SQUARE',
            '△': 'TRIANGLE',
            '○': 'CIRCLE'
        }

        # Rótulo de status
        self.status_label = Label(text='Status: Unknown', font_size='15sp')
        self.add_widget(self.status_label)

    def update_values(self, instance, value):
        x = self.slider_x.value
        y = self.slider_y.value
        command = f'MOVE,{x},{y}'
        # Envia o comando em uma thread para não bloquear a interface do usuário
        Thread(target=self.send_command, args=(command,)).start()

    def send_command(self, command):
        server_url = "http://127.0.0.1:5557/command/" + command
        try:
            response = requests.get(server_url)
            response.raise_for_status()
            # Atualiza o rótulo de status na thread principal
            App.get_running_app().root.status_label.text = "Comando enviado com sucesso!"
        except requests.exceptions.HTTPError as errh:
            App.get_running_app().root.status_label.text = f"Erro HTTP: {errh}"
        except requests.exceptions.ConnectionError as errc:
            App.get_running_app().root.status_label.text = f"Erro de conexão: {errc}"
        except requests.exceptions.Timeout as errt:
            App.get_running_app().root.status_label.text = f"Timeout de solicitação: {errt}"
        except requests.exceptions.RequestException as err:
            App.get_running_app().root.status_label.text = f"Erro ao enviar comando para o servidor: {err}"

class JoystickApp(App):
    def build(self):
        layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)

        # Adiciona um analógico virtual à esquerda
        analog_stick = AnalogStick()
        layout.add_widget(analog_stick)

        # Adiciona os botões do joystick do PlayStation à direita
        button_layout = BoxLayout(orientation='vertical', spacing=10)

        # Adiciona espaço vazio para centralizar os botões
        button_layout.add_widget(Button(size_hint=(1, None), height=30, disabled=True))

        # Adiciona botões retangulares
        rectangular_buttons = ['✕', '□', '△', '○']
        for btn_text in rectangular_buttons:
            button = Button(
                text=btn_text,
                font_size='20sp',
                background_normal='',
                color=(1, 1, 1, 1)
            )
            # Liga o evento de pressionar do botão ao método send_command do analógico
            button.bind(on_press=lambda instance, stick=analog_stick, command_text=btn_text: stick.send_command(command_text))

            button_layout.add_widget(button)

        layout.add_widget(button_layout)

        return layout

if __name__ == '__main__':
    JoystickApp().run()
