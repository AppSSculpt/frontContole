import tkinter as tk
from tkinter import simpledialog
import requests
from scapy.all import ARP, Ether, srp
import socket

class TVControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle da TV")
        self.tv_ip = ""

        # Configuração da interface
        self.label = tk.Label(root, text="Controle da TV")
        self.label.pack(pady=10)

        self.search_button = tk.Button(root, text="Buscar TVs", command=self.search_tv)
        self.search_button.pack(pady=10)

        self.tv_listbox = tk.Listbox(root, width=50, height=10)
        self.tv_listbox.pack(pady=10)
        self.tv_listbox.bind('<<ListboxSelect>>', self.on_tv_select)

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=20)

        # Botões de controle
        self.turn_on_button = tk.Button(self.control_frame, text="Ligar TV", command=self.turn_on_tv)
        self.turn_on_button.pack(side=tk.LEFT, padx=5)

        self.turn_off_button = tk.Button(self.control_frame, text="Desligar TV", command=self.turn_off_tv)
        self.turn_off_button.pack(side=tk.LEFT, padx=5)

        self.change_channel_button = tk.Button(self.control_frame, text="Mudar Canal", command=self.change_channel)
        self.change_channel_button.pack(side=tk.LEFT, padx=5)

        # Rótulo de status
        self.status_label = tk.Label(root, text="", fg="red")
        self.status_label.pack(pady=10)

        # Botões de navegação e controle
        self.navigation_frame = tk.Frame(root)
        self.navigation_frame.pack(pady=20)

        # Navegação
        self.create_navigation_buttons()

        # Controle adicional
        self.create_additional_buttons()

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def get_network_devices(self):
        local_ip = self.get_local_ip()
        print(f"Seu IP local é: {local_ip}")

        ip_base = '.'.join(local_ip.split('.')[:-1]) + '.1/24'

        arp = ARP(pdst=ip_base)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp

        result = srp(packet, timeout=3, verbose=0)[0]

        devices = []

        for sent, received in result:
            devices.append({'ip': received.psrc, 'mac': received.hwsrc, 'type': self.identify_device(received.psrc)})

        return devices

    def identify_device(self, ip):
        # Aqui você pode adicionar um método de identificação mais robusto
        return "TV"

    def search_tv(self):
        devices = self.get_network_devices()
        self.tv_listbox.delete(0, tk.END)  # Limpa a listbox

        if devices:
            for i, device in enumerate(devices):
                if device['type'] == "TV":
                    self.tv_listbox.insert(tk.END, f"IP: {device['ip']} | MAC: {device['mac']}")
        else:
            self.update_status("Nenhum dispositivo encontrado na rede.")

    def on_tv_select(self, event):
        selection = self.tv_listbox.curselection()
        if selection:
            index = selection[0]
            devices = self.get_network_devices()
            self.tv_ip = devices[index]['ip']
            self.update_status(f"Conectado à TV com IP: {self.tv_ip}")

    def turn_on_tv(self):
        if not self.tv_ip:
            self.update_status("Por favor, conecte-se a uma TV primeiro.")
            return
        try:
            response = requests.post(f"http://{self.tv_ip}:8060/keypress/PowerOn")
            if response.status_code == 200:
                self.update_status("TV ligada com sucesso.")
            else:
                self.update_status(f"Falha ao ligar a TV. Código de status: {response.status_code}")
        except Exception as e:
            self.update_status(f"Erro ao tentar ligar a TV: {e}")

    def turn_off_tv(self):
        if not self.tv_ip:
            self.update_status("Por favor, conecte-se a uma TV primeiro.")
            return
        try:
            response = requests.post(f"http://{self.tv_ip}:8060/keypress/PowerOff")
            if response.status_code == 200:
                self.update_status("TV desligada com sucesso.")
            else:
                self.update_status(f"Falha ao desligar a TV. Código de status: {response.status_code}")
        except Exception as e:
            self.update_status(f"Erro ao tentar desligar a TV: {e}")

    def change_channel(self):
        if not self.tv_ip:
            self.update_status("Por favor, conecte-se a uma TV primeiro.")
            return
        channel = simpledialog.askstring("Mudar Canal", "Digite o número do canal:")
        if channel:
            try:
                response = requests.post(f"http://{self.tv_ip}:8060/keypress/ChannelUp")
                if response.status_code == 200:
                    self.update_status(f"Canal alterado para {channel}.")
                else:
                    self.update_status(f"Falha ao mudar o canal. Código de status: {response.status_code}")
            except Exception as e:
                self.update_status(f"Erro ao tentar mudar o canal: {e}")

    def send_key_command(self, key):
        if not self.tv_ip:
            self.update_status("Por favor, conecte-se a uma TV primeiro.")
            return
        try:
            response = requests.post(f"http://{self.tv_ip}:8060/keypress/{key}")
            if response.status_code == 200:
                self.update_status(f"Comando '{key}' enviado com sucesso.")
            else:
                self.update_status(f"Falha ao enviar o comando '{key}'. Código de status: {response.status_code}")
        except Exception as e:
            self.update_status(f"Erro ao tentar enviar o comando '{key}': {e}")

    def update_status(self, message):
        self.status_label.config(text=message)

    def create_navigation_buttons(self):
        self.up_button = tk.Button(self.navigation_frame, text="↑", command=lambda: self.send_key_command('Up'))
        self.up_button.grid(row=0, column=1)

        self.left_button = tk.Button(self.navigation_frame, text="←", command=lambda: self.send_key_command('Left'))
        self.left_button.grid(row=1, column=0)

        self.right_button = tk.Button(self.navigation_frame, text="→", command=lambda: self.send_key_command('Right'))
        self.right_button.grid(row=1, column=2)

        self.down_button = tk.Button(self.navigation_frame, text="↓", command=lambda: self.send_key_command('Down'))
        self.down_button.grid(row=2, column=1)

        self.enter_button = tk.Button(self.navigation_frame, text="Enter", command=lambda: self.send_key_command('Enter'))
        self.enter_button.grid(row=1, column=1)

    def create_additional_buttons(self):
        self.home_button = tk.Button(self.navigation_frame, text="Home", command=lambda: self.send_key_command('Home'))
        self.home_button.grid(row=0, column=0)

        self.rev_button = tk.Button(self.navigation_frame, text="Rev", command=lambda: self.send_key_command('Rev'))
        self.rev_button.grid(row=0, column=2)

        self.fwd_button = tk.Button(self.navigation_frame, text="Fwd", command=lambda: self.send_key_command('Fwd'))
        self.fwd_button.grid(row=2, column=0)

        self.play_button = tk.Button(self.navigation_frame, text="Play", command=lambda: self.send_key_command('Play'))
        self.play_button.grid(row=2, column=2)

        self.select_button = tk.Button(self.navigation_frame, text="Select", command=lambda: self.send_key_command('Select'))
        self.select_button.grid(row=1, column=0)

        self.volume_down_button = tk.Button(self.navigation_frame, text="Volume Down", command=lambda: self.send_key_command('VolumeDown'))
        self.volume_down_button.grid(row=3, column=0)

        self.volume_mute_button = tk.Button(self.navigation_frame, text="Volume Mute", command=lambda: self.send_key_command('VolumeMute'))
        self.volume_mute_button.grid(row=3, column=1)

        self.volume_up_button = tk.Button(self.navigation_frame, text="Volume Up", command=lambda: self.send_key_command('VolumeUp'))
        self.volume_up_button.grid(row=3, column=2)

        self.input_hdmi1_button = tk.Button(self.navigation_frame, text="Input HDMI1", command=lambda: self.send_key_command('InputHDMI1'))
        self.input_hdmi1_button.grid(row=5, column=1)

        self.input_hdmi2_button = tk.Button(self.navigation_frame, text="Input HDMI2", command=lambda: self.send_key_command('InputHDMI2'))
        self.input_hdmi2_button.grid(row=5, column=2)

        self.input_vga_button = tk.Button(self.navigation_frame, text="Input VGA", command=lambda: self.send_key_command('InputVGA'))
        self.input_vga_button.grid(row=6, column=0)

        self.input_composite_button = tk.Button(self.navigation_frame, text="Input Composite", command=lambda: self.send_key_command('InputComposite'))
        self.input_composite_button.grid(row=6, column=1)

        self.input_component_button = tk.Button(self.navigation_frame, text="Input Component", command=lambda: self.send_key_command('InputComponent'))
        self.input_component_button.grid(row=6, column=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = TVControlApp(root)
    root.mainloop()
