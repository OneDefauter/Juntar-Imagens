import os
import shutil
import subprocess
import requests
import win32con
import win32api
import platform
import zipfile
import pickle
import tkinter as tk
from tkinter import filedialog, messagebox

# Obter o caminho absoluto do arquivo atual (app.py)
file_path = os.path.abspath(__file__)

# Obter apenas o nome do arquivo sem o caminho
file_name = os.path.basename(file_path)

# Obtém o nome do sistema operacional
sistema_operacional = platform.system()

if sistema_operacional != 'Windows':
    os.exit()

GITHUB_REPO = "https://api.github.com/repos/OneDefauter/Juntar-Imagens"
version = "v1.2"

try:
    response = requests.get(f"{GITHUB_REPO}/releases/latest")
    response.raise_for_status()
    latest_version = response.json()["tag_name"]
except requests.exceptions.RequestException as e:
    print(f"Erro ao verificar atualizações: {e}")

class ImageJoinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Juntar Imagens")
        self.image_folder = None
        self.image_list = []
        self.backup_var = tk.BooleanVar(value=False)
        self.extension_var = tk.StringVar(value=".jpg")
        self.quality_var = tk.IntVar(value=80)

        if not self.check_imagemagick_installed():
            if messagebox.askyesno("ImageMagick não está instalado", "ImageMagick não foi encontrado. Deseja baixar e instalar agora?"):
                self.download_imagemagick()
                messagebox.showinfo("Instalação Concluído", "O ImageMagick foi instalado com sucesso.")
            self.root.destroy()
            return
            
        # Caminho para o diretório atual (onde o código está sendo executado)
        self.current_dir = os.getcwd()

        # Diretório onde o arquivo settings.pickle será salvo
        self.settings_dir = os.path.join(os.environ.get("HOMEDRIVE"), os.environ.get("HOMEPATH"), "Juntar Imagens")

        # Carregar configurações do usuário
        self.load_settings()

        self.create_widgets()
    
    def save_settings(self):
        settings = {
            "backup_var": self.backup_var.get(),
            "extension_var": self.extension_var.get(),
            "quality_var": self.quality_var.get(),
        }

        with open("settings.pickle", "wb") as file:
            pickle.dump(settings, file)

    def load_settings(self):
        try:
            with open(f"{self.settings_dir}/settings.pickle", "rb") as file:
                settings = pickle.load(file)

            self.backup_var.set(settings["backup_var"])
            self.extension_var.set(settings["extension_var"])
            self.quality_var.set(settings["quality_var"])

        except FileNotFoundError:
            # Usar valores padrão caso o arquivo de configurações não exista
            self.backup_var.set(False)
            self.extension_var.set(".jpg")
            self.quality_var.set(80)
        except (pickle.PickleError, KeyError):
            # Tratar qualquer erro de desserialização ou chave ausente
            print("Erro ao carregar as configurações. Usando valores padrão.")
            self.backup_var.set(False)
            self.extension_var.set(".jpg")
            self.quality_var.set(80)

    def install_newversion(self):
        update_url = f"https://github.com/OneDefauter/Juntar-Imagens/archive/refs/tags/{latest_version}.zip"
        response = requests.get(update_url)
        response.raise_for_status()
        if os.path.exists(f"{latest_version}.zip"):
            os.remove(f"{latest_version}.zip")
        with open(f"{latest_version}.zip", "wb") as f:
            f.write(response.content)

        with zipfile.ZipFile(f"{latest_version}.zip", 'r') as zip_ref:
            zip_ref.extractall()

        os.remove(f"Juntar-Imagens-{latest_version.replace('v', '')}/.gitignore")
        os.remove(f"Juntar-Imagens-{latest_version.replace('v', '')}/app.py")
        os.remove(file_name)
        shutil.move(f"Juntar-Imagens-{latest_version.replace('v', '')}/app.exe", self.current_dir)
        if file_name != "app.exe":
            os.rename("app.exe", file_name)
        os.removedirs(f"Juntar-Imagens-{latest_version.replace('v', '')}")

    def check_imagemagick_installed(self):
        try:
            subprocess.run(["magick", "-version"], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            try:
                subprocess.run(["convert", "-version"], capture_output=True, check=True)
                return True
            except subprocess.CalledProcessError:
                return False

    def download_newverison(self):
        url = "https://github.com/OneDefauter/Menu_/releases/download/Req/ImageMagick.7.1.1.Q16-HDRI.64-bit.msi"
        filename = "ImageMagickInstaller.msi"

        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)

        try:
            subprocess.run(['msiexec', '/i', filename, '/passive'], check=True)
            os.remove(filename)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1602:
                print("A instalação foi cancelada pelo usuário.")
                os.exit()

    def download_imagemagick(self):
        url = "https://github.com/OneDefauter/Menu_/releases/download/Req/ImageMagick.7.1.1.Q16-HDRI.64-bit.msi"
        filename = "ImageMagickInstaller.msi"

        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)

        try:
            subprocess.run(['msiexec', '/i', filename, '/passive'], check=True)
            os.remove(filename)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1602:
                print("A instalação foi cancelada pelo usuário.")
                os.exit()

    def create_widgets(self):
        # Botão para adicionar a pasta de imagens
        tk.Button(self.root, text="Adicionar Pasta", command=self.select_image_folder).grid(row=0, column=0, padx=10, pady=10)

        # Caixa para marcar ou desmarcar a opção de backup
        tk.Checkbutton(self.root, text="Fazer Backup", variable=self.backup_var).grid(row=0, column=1, padx=10, pady=10)

        # Lista com as extensões de saída disponíveis
        tk.Label(self.root, text="Extensão de Saída:").grid(row=1, column=0, padx=10, pady=5)
        extensions = [".png", ".jpg"]
        tk.OptionMenu(self.root, self.extension_var, *extensions).grid(row=1, column=1, padx=10, pady=5)

        # Escala para selecionar o nível da imagem
        tk.Label(self.root, text="Nível de Qualidade:").grid(row=2, column=0, padx=10, pady=5)
        tk.Scale(self.root, from_=1, to=100, variable=self.quality_var, orient=tk.HORIZONTAL).grid(row=2, column=1, padx=10, pady=5)

        # Lista para selecionar as imagens a serem juntadas
        self.image_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, width=50)
        self.image_listbox.grid(row=3, columnspan=2, padx=10, pady=5)

        # Botão para juntar as imagens
        tk.Button(self.root, text="Juntar Imagens", command=self.join_images).grid(row=4, columnspan=2, padx=10, pady=10)

        # Botão para renomear os arquivos da pasta
        tk.Button(self.root, text="Renomear", command=self.rename_files).grid(row=4, column=1, padx=10, pady=10, rowspan=5)

    def select_image_folder(self):
        self.image_folder = filedialog.askdirectory(title="Selecione a pasta de imagens")
        self.load_image_list()

    def load_image_list(self):
        if self.image_folder:
            image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.image_listbox.delete(0, tk.END)
            for image_file in image_files:
                self.image_listbox.insert(tk.END, image_file)

    def join_images(self):
        if not self.image_folder:
            messagebox.showerror("Erro", "Selecione uma pasta de imagens primeiro.")
            return

        selected_images = [self.image_listbox.get(i) for i in self.image_listbox.curselection()]
        if len(selected_images) < 2:
            messagebox.showerror("Erro", "Selecione pelo menos duas imagens para juntar.")
            return
        
        input_images = [os.path.join(self.image_folder, image) for image in selected_images]
        output_folder = os.path.join(self.image_folder, "temp")
        backup = self.backup_var.get()
        extension = self.extension_var.get()
        quality = self.quality_var.get()

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        atributos_atuais = win32api.GetFileAttributes(output_folder)
        win32api.SetFileAttributes(output_folder, atributos_atuais | win32con.FILE_ATTRIBUTE_HIDDEN)

        # Obtendo o nome da primeira imagem selecionada
        first_image_name = sorted(selected_images)[0].split(".")[0]

        try:
            output_filename = os.path.join(output_folder, f"{first_image_name}{extension}")
            command = ["magick", "convert", "-append", "-quality", str(quality)] + input_images + [output_filename]
            subprocess.run(command, check=True)

            if backup:
                backup_path = os.path.join(self.image_folder, "Backup")
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)

                output_folder = os.path.join(self.image_folder, "Backup")

                for image_file in selected_images:
                    source_path = os.path.join(self.image_folder, image_file)
                    backup_path = os.path.join(output_folder, image_file)
                    shutil.move(source_path, backup_path)
            else:
                for image_file in selected_images:
                    source_path = os.path.join(self.image_folder, image_file)
                    os.remove(source_path)
            
            shutil.move(output_filename, self.image_folder)
            output_folder2 = os.path.join(self.image_folder, "temp")
            os.removedirs(output_folder2)

            messagebox.showinfo("Sucesso", "As imagens foram juntadas com sucesso!")
            self.load_image_list()  # Atualizar a lista de imagens após a junção
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao executar o ImageMagick: \n{e}")
        self.save_settings()

    def rename_files(self):
        if not self.image_folder:
            messagebox.showerror("Erro", "Selecione uma pasta de imagens primeiro.")
            return
        
        backup = self.backup_var.get()

        file_list = [f for f in os.listdir(self.image_folder) if os.path.isfile(os.path.join(self.image_folder, f))]
        file_list.sort()

        if backup:
            backup_path = os.path.join(self.image_folder, "Backup")
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            
            for image_file in file_list:
                source_path = os.path.join(self.image_folder, image_file)
                shutil.copy(source_path, backup_path)

        # Contador para numerar os arquivos
        count = 1

        for filename in file_list:
            base, ext = os.path.splitext(filename)
            new_filename = f"{base}__{ext}"
            os.rename(os.path.join(self.image_folder, filename), os.path.join(self.image_folder, new_filename))

        file_list = [f for f in os.listdir(self.image_folder) if os.path.isfile(os.path.join(self.image_folder, f))]
        file_list.sort()

        for filename in file_list:
            base, ext = os.path.splitext(filename)
            new_filename = f"{count:02d}{ext}"
            os.rename(os.path.join(self.image_folder, filename), os.path.join(self.image_folder, new_filename))
            count += 1

        messagebox.showinfo("Sucesso", "Os arquivos foram renomeados com sucesso!")
        self.load_image_list()  # Atualizar a lista de imagens após a renomeação

    def show_update_dialog(self):
        if messagebox.askyesno("Nova Atualização", f"Tem uma nova atualização.\nVersão atual: {version}\nVersão mais recente: {latest_version}\nDeseja atualizar agora?"):
            self.install_newversion()
            messagebox.showinfo("Atualização Concluída", "A atualização foi concluída com sucesso!")
            self.root.destroy()

    def check_for_updates(self):
        if version != latest_version:
            self.show_update_dialog()
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageJoinerApp(root)
    app.check_for_updates()
    root.mainloop()
