import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
import time
import numpy as np
import face_recognition
from datetime import datetime
from enum import Enum
import mysql.connector

# Configurações de conexão com o banco de dados
db = mysql.connector.connect(
    host="joaomiranda.xyz",
    user="trabalhofinal",
    password="12345678",
    database="gestao_animais"
)
cursor = db.cursor()

# Criar o diretório para armazenar as imagens capturadas
if not os.path.exists("ImagesBasic"):
    os.makedirs("ImagesBasic")

# Função para capturar a imagem
def capture_image():
    name_window = tk.Toplevel(root)
    name_window.title("Nome do Novo Usuário")

    name_label = ttk.Label(name_window, text="Nome do Usuário:")
    name_label.grid(row=0, column=0, padx=5, pady=5)
    name_entry = ttk.Entry(name_window)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    def save_image_with_name():
        name = name_entry.get().strip()
        if name:
            ret, frame = cap.read()
            if ret:
                timestamp = time.strftime("%Y%m%d%H%M%S")
                image_path = os.path.join("ImagesBasic", f"{name}_{timestamp}.jpg")
                cv2.imwrite(image_path, frame)
                print(f"Imagem capturada e salva como: {image_path}")
                name_window.destroy()
            else:
                print("Erro ao capturar imagem.")
        else:
            print("Por favor, insira um nome válido.")

    save_button = ttk.Button(name_window, text="Salvar", command=save_image_with_name)
    save_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    root.wait_window(name_window)

def recognize_faces():
    path = 'ImagesBasic'
    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        with open('Attendance.csv', 'r+') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString}')

    encodeListKnown = findEncodings(images)

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Função para abrir a janela da agenda
def open_agenda():
    agenda_window = tk.Toplevel(root)
    agenda_window.title("Agenda")

    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    horas = [f"{h:02d}:00" for h in range(24)]

    def add_appointment():
        dia = day_combobox.get()
        mes = month_combobox.get()
        hora = hour_combobox.get()
        compromisso = appointment_entry.get()
        if dia and mes and hora and compromisso:
            appointment = f"{dia} de {mes} às {hora}: {compromisso}"
            appointments_listbox.insert(tk.END, appointment)
            appointment_entry.delete(0, tk.END)
            sort_appointments()

    def sort_appointments():
        appointments = list(appointments_listbox.get(0, tk.END))
        appointments.sort(key=lambda x: (meses.index(x.split()[2]), int(x.split()[0]), x.split()[4]))
        appointments_listbox.delete(0, tk.END)
        for appointment in appointments:
            appointments_listbox.insert(tk.END, appointment)

    tk.Label(agenda_window, text="Dia:").pack(pady=5)
    day_combobox = ttk.Combobox(agenda_window, values=list(range(1, 32)), width=5)
    day_combobox.pack(pady=5)

    tk.Label(agenda_window, text="Mês:").pack(pady=5)
    month_combobox = ttk.Combobox(agenda_window, values=meses)
    month_combobox.pack(pady=5)

    tk.Label(agenda_window, text="Hora:").pack(pady=5)
    hour_combobox = ttk.Combobox(agenda_window, values=horas)
    hour_combobox.pack(pady=5)

    tk.Label(agenda_window, text="Compromisso:").pack(pady=5)
    appointment_entry = tk.Entry(agenda_window, width=40)
    appointment_entry.pack(pady=5)

    add_appointment_button = tk.Button(agenda_window, text="Adicionar Compromisso", command=add_appointment)
    add_appointment_button.pack(pady=5)

    appointments_listbox = tk.Listbox(agenda_window, width=50, height=10)
    appointments_listbox.pack(pady=10)

class TipoServico(Enum):
    Consulta_de_rotina = "Consulta de rotina"
    Vacinação = "Vacinação"
    Cirurgia = "Cirurgia"
    Análise = "Análise"
    Exame_clínico = "Exame clínico"
    Eutanásia = "Eutanásia"
    Desparatisação = "Desparatisação"
    Internamento = "Internamento"
    Serviços_de_apoio = "Serviços de apoio"
    Urgência = "Urgência"

class Fatura:
    def __init__(self, id_fatura, nome_cliente, tipo_servico, descricao, preco):
        self.id_fatura = id_fatura
        self.nome_cliente = nome_cliente
        self.tipo_servico = tipo_servico
        self.descricao = descricao
        self.preco = preco

    def imprimir_fatura(self):
        return (f"========== Fatura ==========\n"
                f"ID da Fatura: {self.id_fatura}\n"
                f"Nome do Cliente: {self.nome_cliente}\n"
                f"Tipo de Serviço: {self.tipo_servico.value}\n"
                f"Descrição: {self.descricao}\n"
                f"Preço: €{self.preco:.2f}\n"
                f"============================\n")

class AplicacaoFatura:
    def __init__(self, root):
        self.root = root
        self.faturas = []
        self.proximo_id_fatura = 1

        self.label_nome_cliente = ttk.Label(root, text="Nome do Cliente:")
        self.label_nome_cliente.grid(row=0, column=0, padx=10, pady=5)
        self.entry_nome_cliente = ttk.Entry(root)
        self.entry_nome_cliente.grid(row=0, column=1, padx=10, pady=5)

        self.label_tipo_servico = ttk.Label(root, text="Tipo de Serviço:")
        self.label_tipo_servico.grid(row=1, column=0, padx=10, pady=5)
        self.combo_tipo_servico = ttk.Combobox(root, values=[tipo.value for tipo in TipoServico], state="readonly")
        self.combo_tipo_servico.grid(row=1, column=1, padx=10, pady=5)

        self.label_descricao = ttk.Label(root, text="Descrição:")
        self.label_descricao.grid(row=2, column=0, padx=10, pady=5)
        self.entry_descricao = ttk.Entry(root)
        self.entry_descricao.grid(row=2, column=1, padx=10, pady=5)

        self.label_preco = ttk.Label(root, text="Preço: €")
        self.label_preco.grid(row=3, column=0, padx=10, pady=5)
        self.entry_preco = ttk.Entry(root)
        self.entry_preco.grid(row=3, column=1, padx=10, pady=5)

        self.botao_adicionar = ttk.Button(root, text="Adicionar Fatura", command=self.adicionar_fatura)
        self.botao_adicionar.grid(row=4, column=0, columnspan=2, pady=10)

        self.botao_mostrar = ttk.Button(root, text="Mostrar Faturas", command=self.mostrar_faturas)
        self.botao_mostrar.grid(row=5, column=0, columnspan=2, pady=10)
    def adicionar_fatura(self):
        nome_cliente = self.entry_nome_cliente.get()
        tipo_servico = self.combo_tipo_servico.get()
        descricao = self.entry_descricao.get()
        preco = self.entry_preco.get()

        if not nome_cliente or not tipo_servico or not descricao or not preco:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número válido!")
            return

        tipo_servico_enum = next(ts for ts in TipoServico if ts.value == tipo_servico)
        id_fatura = self.proximo_id_fatura
        self.proximo_id_fatura += 1

        fatura = Fatura(id_fatura, nome_cliente, tipo_servico_enum, descricao, preco)
        self.faturas.append(fatura)

        messagebox.showinfo("Sucesso", "Fatura adicionada com sucesso!")

        self.entry_nome_cliente.delete(0, tk.END)
        self.combo_tipo_servico.set('')
        self.entry_descricao.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)

    def mostrar_faturas(self):
        janela_faturas = tk.Toplevel(self.root)
        janela_faturas.title("Faturas")

        text_area = tk.Text(janela_faturas, wrap='word')
        text_area.pack(expand=True, fill='both')

        for fatura in self.faturas:
            text_area.insert(tk.END, fatura.imprimir_fatura())

        text_area.config(state='disabled')

class GerenciadorDonos:
    def __init__(self, root):
        self.root = root

        # Widgets para entrada de dados do dono
        self.label_nome_dono = ttk.Label(root, text="Nome do Dono:")
        self.label_nome_dono.grid(row=0, column=0, padx=10, pady=5)
        self.entry_nome_dono = ttk.Entry(root)
        self.entry_nome_dono.grid(row=0, column=1, padx=10, pady=5)

        self.label_endereco = ttk.Label(root, text="Endereço:")
        self.label_endereco.grid(row=1, column=0, padx=10, pady=5)
        self.entry_endereco = ttk.Entry(root)
        self.entry_endereco.grid(row=1, column=1, padx=10, pady=5)

        self.label_telefone = ttk.Label(root, text="Telefone:")
        self.label_telefone.grid(row=2, column=0, padx=10, pady=5)
        self.entry_telefone = ttk.Entry(root)
        self.entry_telefone.grid(row=2, column=1, padx=10, pady=5)

        # Botão para adicionar dono
        self.botao_adicionar_dono = ttk.Button(root, text="Adicionar Dono", command=self.adicionar_dono)
        self.botao_adicionar_dono.grid(row=3, column=0, columnspan=2, pady=10)

    # Método para adicionar dono ao banco de dados
    def adicionar_dono(self):
        nome_dono = self.entry_nome_dono.get()
        endereco = self.entry_endereco.get()
        telefone = self.entry_telefone.get()

        # Verificar se todos os campos foram preenchidos
        if not nome_dono or not endereco or not telefone:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        # Inserir dono no banco de dados
        try:
            cursor.execute("INSERT INTO donos (nome, endereco, telefone) VALUES (%s, %s, %s)",
                           (nome_dono, endereco, telefone))
            db.commit()
            messagebox.showinfo("Sucesso", "Dono adicionado com sucesso!")
        except Exception as e:
            db.rollback()
            messagebox.showerror("Erro", f"Erro ao adicionar dono: {e}")

        # Limpar os campos de entrada após adicionar o dono
        self.entry_nome_dono.delete(0, tk.END)
        self.entry_endereco.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)

class GerenciadorAnimais:
    def __init__(self, root):
        self.root = root

        # Widgets para entrada de dados do animal
        self.label_nome_animal = ttk.Label(root, text="Nome do Animal:")
        self.label_nome_animal.grid(row=0, column=0, padx=10, pady=5)
        self.entry_nome_animal = ttk.Entry(root)
        self.entry_nome_animal.grid(row=0, column=1, padx=10, pady=5)

        self.label_especie = ttk.Label(root, text="Espécie:")
        self.label_especie.grid(row=1, column=0, padx=10, pady=5)
        self.entry_especie = ttk.Entry(root)
        self.entry_especie.grid(row=1, column=1, padx=10, pady=5)

        self.label_raca = ttk.Label(root, text="Raça:")
        self.label_raca.grid(row=2, column=0, padx=10, pady=5)
        self.entry_raca = ttk.Entry(root)
        self.entry_raca.grid(row=2, column=1, padx=10, pady=5)

        self.label_idade = ttk.Label(root, text="Idade:")
        self.label_idade.grid(row=3, column=0, padx=10, pady=5)
        self.entry_idade = ttk.Entry(root)
        self.entry_idade.grid(row=3, column=1, padx=10, pady=5)

        self.label_id_cliente = ttk.Label(root, text="ID do Cliente:")
        self.label_id_cliente.grid(row=4, column=0, padx=10, pady=5)
        self.entry_id_cliente = ttk.Entry(root)
        self.entry_id_cliente.grid(row=4, column=1, padx=10, pady=5)

        # Botão para adicionar animal
        self.botao_adicionar_animal = ttk.Button(root, text="Adicionar Animal", command=self.adicionar_animal)
        self.botao_adicionar_animal.grid(row=5, column=0, columnspan=2, pady=10)

    # Método para adicionar animal ao banco de dados
    def adicionar_animal(self):
        nome_animal = self.entry_nome_animal.get()
        especie = self.entry_especie.get()
        raca = self.entry_raca.get()
        idade = self.entry_idade.get()
        id_cliente = self.entry_id_cliente.get()

        # Verificar se todos os campos foram preenchidos
        if not nome_animal or not especie or not raca or not idade or not id_cliente:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        # Inserir animal no banco de dados
        try:
            cursor.execute("INSERT INTO animais (nome, especie, raca, idade, id_dono) VALUES (%s, %s, %s, %s, %s)",
                           (nome_animal, especie, raca, idade, id_cliente))
            db.commit()
            messagebox.showinfo("Sucesso", "Animal adicionado com sucesso!")
        except Exception as e:
            db.rollback()
            messagebox.showerror("Erro", f"Erro ao adicionar animal: {e}")

        # Limpar os campos de entrada após adicionar o animal
        self.entry_nome_animal.delete(0, tk.END)
        self.entry_especie.delete(0, tk.END)
        self.entry_raca.delete(0, tk.END)
        self.entry_idade.delete(0, tk.END)
        self.entry_id_cliente.delete(0, tk.END)
class DonoAnimal:
    def __init__(self, nome_dono, nome_animal, especie, raca, idade):
        self.nome_dono = nome_dono
        self.nome_animal = nome_animal
        self.especie = especie
        self.raca = raca
        self.idade = idade

    def __str__(self):
        return (f"Dono: {self.nome_dono}, Animal: {self.nome_animal}, "
                f"Espécie: {self.especie}, Raça: {self.raca}, Idade: {self.idade}")

class AplicacaoGestao:
    def __init__(self, root):
        self.root = root
        self.donos_animais = []

        self.label_nome_dono = ttk.Label(root, text="Nome do Dono:")
        self.label_nome_dono.grid(row=0, column=0, padx=10, pady=5)
        self.entry_nome_dono = ttk.Entry(root)
        self.entry_nome_dono.grid(row=0, column=1, padx=10, pady=5)

        self.label_nome_animal = ttk.Label(root, text="Nome do Animal:")
        self.label_nome_animal.grid(row=1, column=0, padx=10, pady=5)
        self.entry_nome_animal = ttk.Entry(root)
        self.entry_nome_animal.grid(row=1, column=1, padx=10, pady=5)

        self.label_especie = ttk.Label(root, text="Espécie:")
        self.label_especie.grid(row=2, column=0, padx=10, pady=5)
        self.entry_especie = ttk.Entry(root)
        self.entry_especie.grid(row=2, column=1, padx=10, pady=5)

        self.label_raca = ttk.Label(root, text="Raça:")
        self.label_raca.grid(row=3, column=0, padx=10, pady=5)
        self.entry_raca = ttk.Entry(root)
        self.entry_raca.grid(row=3, column=1, padx=10, pady=5)

        self.label_idade = ttk.Label(root, text="Idade:")
        self.label_idade.grid(row=4, column=0, padx=10, pady=5)
        self.entry_idade = ttk.Entry(root)
        self.entry_idade.grid(row=4, column=1, padx=10, pady=5)

        self.botao_adicionar = ttk.Button(root, text="Adicionar Animal", command=self.adicionar_animal)
        self.botao_adicionar.grid(row=5, column=0, columnspan=2, pady=10)

        self.botao_mostrar = ttk.Button(root, text="Mostrar Donos e Animais", command=self.mostrar_donos_animais)
        self.botao_mostrar.grid(row=6, column=0, columnspan=2, pady=10)

    def adicionar_animal(self):
        nome_dono = self.entry_nome_dono.get()
        nome_animal = self.entry_nome_animal.get()
        especie = self.entry_especie.get()
        raca = self.entry_raca.get()
        idade = self.entry_idade.get()

        if not nome_dono or not nome_animal or not especie or not raca or not idade:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            idade = int(idade)
        except ValueError:
            messagebox.showerror("Erro", "Idade deve ser um número válido!")
            return

        dono_animal = DonoAnimal(nome_dono, nome_animal, especie, raca, idade)
        self.donos_animais.append(dono_animal)

        messagebox.showinfo("Sucesso", "Animal adicionado com sucesso!")

        self.entry_nome_dono.delete(0, tk.END)
        self.entry_nome_animal.delete(0, tk.END)
        self.entry_especie.delete(0, tk.END)
        self.entry_raca.delete(0, tk.END)
        self.entry_idade.delete(0, tk.END)

    def mostrar_donos_animais(self):
        janela_donos_animais = tk.Toplevel(self.root)
        janela_donos_animais.title("Donos e Animais")

        text_area = tk.Text(janela_donos_animais, wrap='word')
        text_area.pack(expand=True, fill='both')

        for dono_animal in self.donos_animais:
            text_area.insert(tk.END, str(dono_animal) + "\n")

        text_area.config(state='disabled')

def main():
    global root, cap
    root = tk.Tk()
    root.title("Sistema de Gestão de Consultório Veterinário")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    frame_captura = ttk.Frame(notebook)
    frame_agenda = ttk.Frame(notebook)
    frame_fatura = ttk.Frame(notebook)
    frame_animais = ttk.Frame(notebook)
    frame_donos = ttk.Frame(notebook)  # Adicionando o frame para a guia de donos

    notebook.add(frame_captura, text="Gestão de Utilizadores")
    notebook.add(frame_agenda, text="Agenda")
    notebook.add(frame_fatura, text="Faturamento")
    notebook.add(frame_animais, text="Gestão de Animais")
    notebook.add(frame_donos, text="Gestão de Donos")  # Adicionando a guia de gestão de donos

    # Frame de Captura e Reconhecimento
    capture_button = tk.Button(frame_captura, text="Novo Usuário", command=capture_image)
    capture_button.grid(row=0, column=0, padx=10, pady=10)

    add_user_button = tk.Button(frame_captura, text="Reconhecer Usuário", command=recognize_faces)
    add_user_button.grid(row=0, column=1, padx=10, pady=10)

    # Frame da Agenda
    open_agenda_button = tk.Button(frame_agenda, text="Abrir Agenda", command=open_agenda)
    open_agenda_button.pack(pady=20)

    # Frame de Faturamento
    AplicacaoFatura(frame_fatura)

    # Adicionando o gerenciador de animais ao frame correspondente
    GerenciadorAnimais(frame_animais)

    # Adicionando o gerenciador de donos ao frame correspondente
    GerenciadorDonos(frame_donos)

    cap = cv2.VideoCapture(0)
    root.mainloop()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
