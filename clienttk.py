import tkinter as tk
from tkinter import ttk
from client import Client
from tkinter import scrolledtext

class tkinterApp(tk.Tk):
     
    def __init__(self, *args, **kwargs): 
         
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)  
        container.pack(side = "top", fill = "both", expand = True) 
  
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

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        user_name_label = ttk.Label(self, text="User Name")
        user_name_label.grid(column=1, row=4)
        self.user_name_entry = ttk.Entry(self)
        self.user_name_entry.grid(column=3, row=4)

        server_label = ttk.Label(self, text="Server")
        server_label.grid(column=1, row=5)
        self.server_entry = ttk.Entry(self)
        self.server_entry.grid(column=3, row=5)

        port_label = ttk.Label(self, text="Port")
        port_label.grid(column=1, row=6)
        self.port_entry = ttk.Entry(self)
        self.port_entry.grid(column=3, row=6)

        btn_column = ttk.Button(self, text="Valider", command=lambda: self.send_text({
                                                            'username': self.user_name_entry.get(),
                                                            'server':   self.server_entry.get(),
                                                            'port':     int(self.port_entry.get())
                                                            }))
        btn_column.grid(column=3)

    def send_text(self, text):
        self.controller.frames[Dialog].set_data(text)
        self.controller.show_frame(Dialog)

class Dialog(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.st = scrolledtext.ScrolledText(self, state='disabled')
        self.st.configure(font='TkFixedFont')
        self.st.grid(column=0, row=1, sticky='w', columnspan=4)
        self.msg_entry = ttk.Entry(self)
        self.msg_entry.grid(column=3, row=2,sticky="NSEW")
        btn_column = ttk.Button(self, text="Send ->", command=lambda: self.send_msg({
                                                            'msg': self.msg_entry.get(),
                                                           }))
        btn_column.grid(column=3)

    def set_data(self, data):
        self.client = Client(data['username'], data['server'], data['port'])
        self.client.listen(self.handle)

    def send_msg(self, data):
        self.client.send(data['msg'])

    def handle(self, msg):
        self.st.configure(state='normal')
        self.st.insert(tk.END, msg + '\n')
        self.st.configure(state='disabled')

if __name__ == "__main__":
    app = tkinterApp()
    app.mainloop()