import customtkinter as ctk
import socket
import threading
from PIL import Image

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()          
        self.geometry('400x300')    # задаємо розмір вікна
        self.title("LogiTalk")

        # Властивості для сокету
        self.client_socket = None
        self.connected = False
        self.username = None

        # налаштуємо сітку, щоб інтерфейс адаптувався при зміні розмуру вікна
        self.grid_rowconfigure(0, weight=1)     
        self.grid_rowconfigure(1, weight=0)     
        self.grid_columnconfigure(2, weight=1)  
        self.grid_columnconfigure(3, weight=0)  

        # Кнопка для відкриття\закриття бічного меню
        self.btn = ctk.CTkButton(
            self,
            text=">",
            width=30,
            height=30,
            corner_radius=5,
            command=self.toggle_show_menu
        )
        self.btn.grid(row=0, column=0, sticky='nw')     # розміщуємо у верхньому лівому куті

        # Бічне меню (фрейм), яке буде ховатися\показуватися
        self.frame = ctk.CTkFrame(self, width=200, corner_radius=0)

        self.label = ctk.CTkLabel(self.frame, text="Ваше Ім'я")
        self.label.pack(pady = 30)

        self.entry = ctk.CTkEntry(self.frame, placeholder_text="Введіть ім'я")
        self.entry.pack(padx=20, pady = 10, fill="x")
        # при натисканні на Enter підключаємось до сервера
        self.entry.bind('<Return>', lambda event: self.connect_to_server())

        self.label_theme = ctk.CTkOptionMenu(
            self.frame,
            values=["Темна", "Світла"],
            command=self.change_theme
        )
        self.label_theme.pack(side='bottom', fill='x', padx=20, pady=20)

        # властивість яка підказуватиме чи відкрите зараз меню
        self.is_show_menu = False

        # основна область (текстова область длячитання повідомлень)
        self.chat_text = ctk.CTkTextbox(self, state="disabled")
        self.chat_text.grid(row=0, column=2, sticky='nsew', padx=(0, 0), pady=30)

        # Поле для введення повідомлення
        self.message_input = ctk.CTkEntry(self, placeholder_text='Введіть повідомдення...', height=35)
        self.message_input.grid(row=1, column=2, sticky='ew', padx=(10, 0), pady=10 )

        # Кнопка для надсидання повідомлень
        self.send_button = ctk.CTkButton(
            self,
            text='>',
            width=40,
            height=35,
            corner_radius=8,
            command=self.send_message
        )
        self.send_button.grid(row=1, column=3, sticky='e', padx=(0,10), pady=10)


    # Метод для перемикання бічного меню
    def toggle_show_menu(self):
        if self.is_show_menu == True:
            # ховаємо меню
            self.frame.grid_remove()   # прибираємо з сітки
            self.btn.configure(text='>')
            self.is_show_menu = False
        else:
            # показуємо меню
            self.frame.grid(row=0, column=1, sticky='ns', rowspan=2, ipadx=10)
            self.btn.configure(text='<')
            self.is_show_menu = True

    
    # Метод для зміни теми оформлення
    def change_theme(self, value):
        if value == "Темна":
            ctk.set_appearance_mode('dark')
        else:
            ctk.set_appearance_mode('light')

    
    # Метод для підключення до сервера
    def connect_to_server(self):
        if self.connected == True:
            return
        
        self.username = self.entry.get().strip()

        if not self.username:
            self.add_message("Помилка: Введіть ім'я!")
            return
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("2.tcp.eu.ngrok.io", 16299))
            self.client_socket.send(self.username.encode())

            self.connected = True
            self.add_message(f"Підключено як {self.username}")
            # запускаємо потік для отримання повідомлень
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            self.add_message(f"Помилка підключення: {e}")
            self.connected = False


    # Метод для додавання повідомлень у віджет чату
    def add_message(self, msg):
        self.chat_text.configure(state='normal')
        self.chat_text.insert("end", msg + '\n')
        self.chat_text.see("end")
        self.chat_text.configure(state='disabled')


    # метод для отримання повідомлень
    def receive_messages(self):
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode()
                self.add_message(message)
            except:
                break

        self.connected=False
        self.add_message("Зʼєднання розірвано")
        if self.client_socket:
            self.client_socket.close()
    

    # метод для відправки повідомлень на сервер
    def send_message(self):
        if not self.connected:
            self.connect_to_server()
        
        if not self.connected:
            return
        
        message = self.message_input.get().strip()
        if not message:
            return 
        
        try:
            self.client_socket.send(message.encode())
            self.add_message(f"Ви: {message}")
            self.message_input.delete(0, "end")
        except:
            self.add_message("Помилка надсилання")
            self.connected=False


window = MainWindow()
window.mainloop()