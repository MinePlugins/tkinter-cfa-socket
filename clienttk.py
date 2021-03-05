import tkinter as tk
from tkinter import ttk
from client import Client
from tkinter import scrolledtext
import tkinter.font
import ctypes
import configparser # Fichier de configuration

#
# Lecture de la configuration
#

config = configparser.ConfigParser()
config.read('config.ini')

color_sombre = config['theme']['color_sombre']
color_clair =  config['theme']['color_clair']
color_text_clair = config['theme']['color_text_clair']
color_text_hightlight = config['theme']['color_text_hightlight']
color_close_button_hightlight = config['theme']['color_close_button_hightlight']
color_title_bar_text = config['theme']['color_title_bar_text']
title = config['app']['title']

class BattleShip(tk.Tk):
     
    def __init__(self, *args, **kwargs): 
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self, bg=color_clair)  
        self.update_idletasks()
        self.attributes("-topmost", True)
        top = tkinter.Toplevel(self)
        top.iconbitmap(default='applications_games.ico')
        top.title(title)
        top.attributes("-alpha",0.0)
        def onRootIconify(event): top.withdraw()
        self.bind("<Unmap>", onRootIconify)
        def onRootDeiconify(event): top.deiconify()
        self.bind("<Map>", onRootDeiconify)
        self.overrideredirect(True)
        self.geometry('1200x480+200+200')
        title_bar = tk.Frame(self, bg=color_clair, relief='flat', bd=0)
        close_button = tk.Button(title_bar, 
                                    bd=0, 
                                    relief='flat', 
                                    text='X',
                                    width=5,
                                    bg=color_clair, 
                                    fg="#8c8c8d", 
                                    activebackground=color_close_button_hightlight, 
                                    overrelief='flat', 
                                    activeforeground="#fefcfc",
                                    command=self.destroy)
        title_text = tk.Label(title_bar, 
                                    text=title,
                                    relief='flat', 
                                    width=5,
                                    padx=10,
                                    bg=color_clair, 
                                    fg="#8c8c8d")
        title_text.pack(side=tk.LEFT)
        close_button.pack(side=tk.RIGHT)
        title_bar.pack(expand=0, fill=tk.X)
        title_bar.bind('<B1-Motion>', self.move_window)
        container.pack(side="top", fill='both', expand=1) 
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        self.frames = {}  
        for F in (StartPage, Dialog):
  
            frame = F(container, self)
            self.frames[F] = frame 
  
            frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(StartPage)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
    def pass_data_dialog(self, text):
        self.frames[self.pages[1]].get_text(text)

    def move_window(self, event):
        self.geometry('+{0}+{1}'.format(event.x_root, event.y_root))


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=color_sombre)
        helv36 = tk.font.Font(family="Helvetica",size=14,weight="bold")
        self.controller = controller
        connection_text = tk.Label(self, text="Information de connection",font=helv36, bg=color_sombre, fg=color_text_clair)
        connection_text.grid(column=1, columnspan=2, row=0)
        user_name_label = tk.Label(self, text="User Name",bg=color_sombre, fg=color_text_clair)
        user_name_label.grid(column=1, row=1)
        self.user_name_entry = tk.Entry(self, bg=color_clair, fg=color_text_clair, relief="flat", insertbackground=color_text_clair)
        self.user_name_entry.grid(column=2, row=1)

        server_label = tk.Label(self, text="Server",bg=color_sombre, fg=color_text_clair)
        server_label.grid(column=1, row=2)
        self.server_entry = tk.Entry(self, bg=color_clair, fg=color_text_clair, relief="flat", insertbackground=color_text_clair)
        self.server_entry.grid(column=2, row=2)

        port_label = tk.Label(self, text="Port",bg=color_sombre, fg=color_text_clair)
        port_label.grid(column=1, row=3)
        self.port_entry = tk.Entry(self, bg=color_clair, fg=color_text_clair, relief="flat", insertbackground=color_text_clair)
        self.port_entry.grid(column=2, row=3)

        btn_column = tk.Button(self, 
                                    text="Valider", 
                                    bg=color_clair, 
                                    fg=color_text_clair, 
                                    activebackground=color_clair,
                                    activeforeground=color_text_clair,
                                    bd=0,
                                    overrelief='flat',
                                    highlightcolor=color_text_hightlight,
                                    relief="flat",
                                    command=lambda: self.send_text({
                                                                    'username': self.user_name_entry.get(),
                                                                    'server':   self.server_entry.get(),
                                                                    'port':     int(self.port_entry.get())
                                                                    }))
                                    
        btn_column.grid(column=1, row=4, columnspan=2,sticky="SEW")

    def send_text(self, text):
        self.controller.frames[Dialog].set_data(text)
        self.controller.show_frame(Dialog)

class Dialog(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg=color_sombre)
        self.controller = controller
        rectangle_1 = tk.Label(self, text="Plateau de Jeux", bg="green", fg="white")
        rectangle_1.grid(column=0, row=1, ipadx=200, ipady=200, sticky="NSEW")
        self.st = scrolledtext.ScrolledText(self, state='disabled',bg=color_sombre, fg=color_text_hightlight)
        self.st.configure(font='TkFixedFont')
        self.st.grid(column=1, row=1, sticky='NSEW', ipadx=10, ipady=10)
        self.msg_entry = tk.Entry(self, bg=color_clair, fg=color_text_clair, relief="flat", insertbackground=color_text_clair)
        self.msg_entry.grid(column=1, row=2,sticky="W", ipadx=50)
        btn_column = tk.Button(self, 
                                text="Send ->", 
                                bg=color_clair, 
                                fg=color_text_clair, 
                                activebackground=color_clair,
                                activeforeground=color_text_clair,
                                bd=0,
                                overrelief='flat',
                                highlightcolor=color_text_hightlight,
                                relief="flat",
                                command=lambda: self.send_msg({
                                                            'msg': self.msg_entry.get(),
                                                           }))
        btn_column.grid(column=1, row=2,sticky="E")
        self.st.tag_config('name', foreground='green')
        self.st.tag_config('msg', foreground='red')
    def set_data(self, data):
        self.client = Client(data['username'], data['server'], data['port'])
        self.client.listen(self.handle)

    def send_msg(self, data):
        self.client.send(data['msg'])

    def handle(self, msg):
        def append():
            self.st.configure(state='normal')
            self.st.insert(tk.END, msg + '\n', 'msg')
            self.st.configure(state='disabled')
            self.st.yview(tk.END)
        self.st.after(0, append)

if __name__ == "__main__":
    app = BattleShip()
    app.mainloop()