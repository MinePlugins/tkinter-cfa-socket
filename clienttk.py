import tkinter as tk
from tkinter import ttk
import pyglet
from client import Client
from tkinter import scrolledtext
import tkinter.font
import ctypes
import json
import configparser  # Fichier de configuration
import datetime
import emoji
import hashlib
from text_utils import with_surrogates
#
# Lecture de la configuration
#
COLUNM_REF = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
BOAT = [5, 4, 3, 3, 2]
config = configparser.ConfigParser()
config.read('config.ini')
color_sombre = config['theme']['color_sombre']
color_clair = config['theme']['color_clair']
color_text_clair = config['theme']['color_text_clair']
color_text_hightlight = config['theme']['color_text_hightlight']
color_close_button_hightlight = config['theme']['color_close_button_hightlight']
color_title_bar_text = config['theme']['color_title_bar_text']
color_button_battleship = config['theme']['color_button_battleship']
title = config['app']['title']
pyglet.font.add_file('resources/NotoSansMono-Regular.ttf')
pyglet.font.add_file('resources/NotoColorEmoji.ttf')


class BattleShip(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self, bg=color_clair)
        self.update_idletasks()
        self.attributes("-topmost", True)
        top = tkinter.Toplevel(self)
        top.iconbitmap(default='resources/applications_games.ico')
        top.title(title)
        top.attributes("-alpha", 0.0)
        def onRootIconify(event): top.withdraw()
        self.bind("<Unmap>", onRootIconify)
        def onRootDeiconify(event): top.deiconify()
        self.bind("<Map>", onRootDeiconify)
        self.overrideredirect(True)
        self.geometry('1410x490+200+200')
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
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, Dialog):

            frame = F(container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

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

        helv36 = tk.font.Font(family="Helvetica", size=14, weight="bold")
        self.controller = controller
        connection_text = tk.Label(
            self, text="Information de connection", font=helv36, bg=color_sombre, fg=color_text_clair)
        connection_text.grid(column=1, columnspan=2, row=0)
        user_name_label = tk.Label(
            self, text="User Name", bg=color_sombre, fg=color_text_clair)
        user_name_label.grid(column=1, row=1)
        self.user_name_entry = tk.Entry(
            self, bg=color_clair, fg=color_text_clair, relief="flat", insertbackground=color_text_clair)
        self.user_name_entry.insert(0, 'Quentin')
        self.user_name_entry.grid(column=2, row=1)

        server_label = tk.Label(self, text="Server",
                                bg=color_sombre, fg=color_text_clair)
        server_label.grid(column=1, row=2)
        self.server_entry = tk.Entry(
            self, bg=color_clair, fg=color_text_clair, relief="flat", insertbackground=color_text_clair)
        self.server_entry.insert(0, '127.0.0.1')
        self.server_entry.grid(column=2, row=2)

        port_label = tk.Label(
            self, text="Port", bg=color_sombre, fg=color_text_clair)
        port_label.grid(column=1, row=3)
        self.port_entry = tk.Entry(
            self, bg=color_clair, fg=color_text_clair, relief="flat", insertbackground=color_text_clair)
        self.port_entry.insert(0, '8080')
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

        btn_column.grid(column=1, row=4, columnspan=2, sticky="SEW")

    def send_text(self, text):
        self.controller.frames[Dialog].set_data(text)
        self.controller.show_frame(Dialog)


class Dialog(tk.Frame):
    def __init__(self, parent, controller):
        self.started = False
        self.id_to_delete_on_start = []
        self.ready = False
        self.his_ready = False
        self.my_turn = False
        self.my_hash = ""
        self.my_score = 0
        self.her_score = 0
        self.my_boats = []
        self.her_hash = ""
        self.join_time = datetime.datetime.now()
        tk.Frame.__init__(self, parent, bg=color_sombre)
        self.controller = controller
        self.battleship_grid_tk = tk.Canvas(
            self, width=670, height=440,  bd=0, highlightthickness=0, bg="#010101", relief="flat")
        self.battleship_grid_tk.grid(column=0, row=1, sticky="NSEW")
        self.draft = tk.Canvas(self, width=670, height=440)
        self.draft.delete(tk.ALL)
        self.create_grid()
        btn_ValidGame = tk.Button(self,
                                  text="Valider",
                                  activebackground=color_clair,
                                  activeforeground=color_button_battleship,
                                  bd=0,
                                  overrelief='flat',
                                  highlightcolor=color_button_battleship,
                                  relief="flat",
                                  command=lambda: self.launch_game())
        btn_ValidGame.grid(column=0, row=1, sticky="SE")
        self.st = scrolledtext.ScrolledText(
            self, state='disabled', bg=color_sombre, fg=color_text_hightlight, font='NotoSansMono')
        # action_man_bold = font.load('Action Man', bold=True)
        self.st.grid(column=1, row=1, sticky='NSEW')
        self.msg_entry = tk.Entry(self, bg=color_clair, fg=color_text_clair,
                                  relief="flat", insertbackground=color_text_clair)
        self.msg_entry.grid(column=1, row=2, sticky="W", ipadx=247)

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
        btn_column.grid(column=1, row=2, sticky="E")

        self.st.tag_config('sys', foreground='orange')
        self.st.tag_config('you', foreground='#fff',
                           background='#16a085', justify="right")
        self.st.tag_config('msg', foreground='#fff', background='#34495e')
        self.create_boat()
        self.create_page("En attente d'un autre joueur")

    def findXCenter(self, canvas, item):
      coords = canvas.bbox(item)
      xOffset = (500 / 2) - ((coords[2] - coords[0]) / 2)
      return xOffset

    def create_page(self, text):
        self.id_to_delete_on_start.append(self.battleship_grid_tk.create_rectangle(0,0,670,440, fill="#feca57", stipple="gray50"))
        id = self.battleship_grid_tk.create_text(320,200,fill="#341f97",font="Noto 30",
                        text=text)
        self.id_to_delete_on_start.append(id)
        xOffset = self.findXCenter(self.battleship_grid_tk, id)
        self.battleship_grid_tk.move(id, xOffset, 0)
    def delete_start_page(self):
        for i in self.id_to_delete_on_start:
            self.battleship_grid_tk.delete(i)
    def create_boat(self):
        self.boats = []
        for index, size in enumerate(BOAT):
            tags = "boat{}".format(index+1)
            total_size = (size * 40)
            total_space = (index * 40)
            total_space += 5*(index+1)
            self.boats.append([False, (0, 0, 0, 0), tags])
            self.battleship_grid_tk.create_rectangle(
                430+total_space, 20, 430+40+total_space, 20+total_size, fill="#95a5a6", outline='#7f8c8d', tags=tags)
            self.battleship_grid_tk.tag_bind(
                tags, "<ButtonRelease-1>", lambda e, tags=tags: self.release_check(e.x, e.y, e, tags, 0))
            self.battleship_grid_tk.tag_bind(
                tags, "<Button1-Motion>", lambda e, tags=tags: self.move_selected(e.x, e.y, e, tags, 0))
            self.battleship_grid_tk.tag_bind(
                tags, "<Button-2>", lambda e: print("press"))
            self.battleship_grid_tk.tag_bind(
                tags, "<Button-3>", lambda e, tags=tags: self.rotate(tags))

    def determine_boat_from_key(self, key):
        letter, number = key[:4], key[4:]
        return letter, int(number)

    def determine_boat_coord_init(self, index):
        index = index - 1
        size = BOAT[index]
        total_size = (size * 40)
        total_space = (index * 40)
        total_space += 5*(index+1)
        return 430+total_space, 20, 430+40+total_space, 20+total_size

    def rotate(self, tags, to_rinit=False):
        letter, number = self.determine_boat_from_key(tags)
        number = number-1
        coord = self.battleship_grid_tk.coords(tags)
        if to_rinit:
            if self.boats[number][0]:
                self.boats[number][0] = False
                self.battleship_grid_tk.coords(tags, *self.boats[number][1])
        else:
            if not self.boats[number][0]:
                self.boats[number][1] = coord
                self.boats[number][0] = True
                self.battleship_grid_tk.coords(
                    tags, coord[0], coord[1], coord[0]-abs(coord[1]-coord[3]), coord[1]+abs(coord[2]-coord[0]))
            else:
                # print(self.boats[number][1])
                self.boats[number][0] = False
                self.battleship_grid_tk.coords(tags, *self.boats[number][1])

    def create_grid(self):
        self.battleship_grid = []
        for index_x, letter in enumerate(COLUNM_REF):
            self.battleship_grid_tk.create_text(
                (index_x*40)+40, 8, fill="#37f122", text=letter.capitalize())
            self.battleship_grid_tk.create_text(
                8, (index_x*40)+40, fill="#37f122", text=index_x)
            line = []
            for index_y, number in enumerate(range(0, 10)):
                key = "{}{}".format(letter, number)
                case = {
                    'name': key,
                    'type': None,
                    'canva': self.battleship_grid_tk.create_rectangle((index_x*40)+19, (index_y*40)+19, (index_x*40)+40+19, (index_y*40)+40+19, fill="#010101", outline='#37f122', tags=key)
                }
                self.draft.create_rectangle((index_x*40)+19, (index_y*40)+19, (index_x*40) +
                                            40+19, (index_y*40)+40+19, fill="#010101", outline='#37f122', tags=key)
                line.append(case)
                self.battleship_grid_tk.tag_bind(key,"<Button-1>",lambda event, key=key: self.clicked(key))
            self.battleship_grid.append(line)

    def release_check(self, x1, y1, key, tags, min_pixels=5):
        clic = x1, y1
        letter, number = self.determine_boat_from_key(tags)
        canva = self.battleship_grid_tk.coords(tags)
        pos = self.determine_boat_coord_init(number)
        x = pos[0]-canva[0]
        y = pos[1]-canva[1]
        if canva[2] > 500 or canva[3] > 419:
            self.battleship_grid_tk.move(tags, x, y)
            self.rotate(tags, to_rinit=True)

    def move_selected(self, x1, y1, key, tags, min_pixels=5):
        # print(key)
        clic = x1, y1
        canva = self.battleship_grid_tk.coords(tags)
        nearest = self.draft.find_closest(*clic)
        # self.battleship_grid_tk.itemconfig("bateau1", fill='red')
        if not "boat" in nearest:
            nearest_coord = self.draft.coords(nearest)
            # print(nearest_coord)
            # print(canva)
            x = nearest_coord[0] - canva[0]
            y = nearest_coord[1] - canva[1]
            if nearest_coord[0] > 18 and nearest_coord[1] > 18 and nearest_coord[0] < 400 and nearest_coord[1] < 400:
                if canva[0] < 700 and canva[1] < 400 and canva[2] < 700 and canva[3] <= 419:
                    self.battleship_grid_tk.move(tags, x, y)
                # if canva[3] > 419:

    def launch_game(self):
        collision = self.check_colision()
        if collision:
            print(collision)
        else:
            for boat in self.boats:
                self.battleship_grid_tk.itemconfig(boat[2], stipple="gray25", state='disabled')
                self.my_boats.extend(self.determine_keys_from_boat(boat[2]))
            data = {
            'type': 'game',
            'hash': self.my_hash.hexdigest(),
            'data': {
                    'ready': True,
                },
            }
            self.ready = True
            self.client.send(data)
            if self.my_turn and self.his_ready:
                self.show_message("C'est a vous de commencer !", "sys")
            else:
                self.show_message("C'est au joueur d'en face de joué !", "sys")


    def check_colision(self):
        collision = False
        for boat in self.boats:
            if collision:
                return collision
            for boat_check in self.boats:
                if collision:
                    return collision
                if boat[2] != boat_check[2]:
                    coord_boat = self.battleship_grid_tk.coords(boat[2])
                    coord_boat_check = self.battleship_grid_tk.coords(
                        boat_check[2])
                    if int(coord_boat_check[0]) > int(coord_boat[2]) or\
                        int(coord_boat_check[2]) < int(coord_boat[0]) or\
                        int(coord_boat_check[1]) > int(coord_boat[3]) or\
                       int(coord_boat_check[3]) < int(coord_boat[1]):
                        # self.show_message("PAS DE COLLISION", "sys")
                        if coord_boat[0] < 18 or coord_boat[1] < 18 or coord_boat[2] > 420 or coord_boat[3] > 420:
                            collision = True
                            self.show_message(
                                "Vos bateaux doivent être dans la grille", "sys")
                            return collision

                    else:
                        collision = True
                        self.show_message(
                            "Vos bateaux ne doivent pas se toucher", "sys")
                        return collision
        return collision

    def determine_pos_from_key(self, key):
        letter, number = key[:1], key[1:]
        column = int(COLUNM_REF.index(letter))
        line = int(number)
        val = self.battleship_grid[column][line]
        column += 1
        line += 1
        return column, line, val['canva']
    
    def determine_keys_from_boat(self, tags):
        list_boats_keys = []
        coords = self.battleship_grid_tk.coords(tags)
        new_coords = (
        int((coords[0]-19)/40),
        int((coords[1]-19)/40),
        int((coords[2]-19)/40-1),
        int((coords[3]-19)/40-1)
        )
        if new_coords[0] == new_coords[2]:
            for i in range(new_coords[1],new_coords[3]+1):
                list_boats_keys.append('{}{}'.format(COLUNM_REF[new_coords[0]],i))
        else:
            for a in range(new_coords[0],new_coords[2]+1):
                if new_coords[1] == new_coords[3]:
                    list_boats_keys.append('{}{}'.format(COLUNM_REF[a],new_coords[1]))
        return list_boats_keys

    def clicked(self, key):
        if self.ready and self.his_ready and self.started and self.my_turn:
            column, line, canva = self.determine_pos_from_key(key)
            self.battleship_grid_tk.itemconfig(canva, fill='black', state='disabled')
            self.battleship_grid_tk.create_line(
                column*40-20, line*40-20, column*40+20, line*40+20, fill='red')
            self.battleship_grid_tk.create_line(
                column*40+20, line*40-20, column*40-20, line*40+20, fill='red')
            data = {
                'type': 'game',
                'hash': self.my_hash.hexdigest(),
                'data': {
                    'key': key,
                },
            }
            self.client.send(data)
            print(key)

    def exploded(self, key):
        if self.ready and self.his_ready and self.started:
            column, line, canva = self.determine_pos_from_key(key)
            self.battleship_grid_tk.itemconfig(canva, fill='blue')
            self.battleship_grid_tk.create_line(
                column*40-20, line*40-20, column*40+20, line*40+20, fill='green')
            self.battleship_grid_tk.create_line(
                column*40+20, line*40-20, column*40-20, line*40+20, fill='green')

    def touched(self, key):
        if self.ready and self.his_ready and self.started:
            column, line, canva = self.determine_pos_from_key(key)
            self.battleship_grid_tk.itemconfig(canva, fill='#6F1E51')
            self.battleship_grid_tk.create_line(
                column*40-20, line*40-20, column*40+20, line*40+20, fill='green')
            self.battleship_grid_tk.create_line(
                column*40+20, line*40-20, column*40-20, line*40+20, fill='green')

    def set_data(self, data):
        self.client = Client(data['username'], data['server'], data['port'])
        self.username = data['username']
        self.client.listen(self.handle)

    def send_msg(self, data):
        to_be_send = {
            'type': 'message',
            'hash': self.my_hash.hexdigest(),
            'data': {
                'message': data['msg'],
            },
        }
        if data['msg'] == '':
            self.show_message(
                "Vous ne pouvez pas envoyer de message vide", "sys")
        else:
            self.client.send(to_be_send)

    def show_message(self, msg, msg_type):
        msg = emoji.emojize(msg)
        msg = with_surrogates(msg)

        def append():
            self.st.configure(state='normal')
            self.st.insert(tk.END, msg + '\n', msg_type)
            self.st.configure(state='disabled')
            self.st.yview(tk.END)
        self.st.after(0, append)

    def handle(self, msg):
        msg_parsed = json.loads(msg)
        print(msg_parsed)
        if msg_parsed['username'] == self.username:
            username = "Vous"
            msg_type = "you"
        else:
            username = msg_parsed['username']
            msg_type = "msg"
        if 'type' in msg_parsed['message']:
            if msg_parsed['message']['type'] == "message" and (msg_parsed['message']['hash'] == self.my_hash.hexdigest() or msg_parsed['message']['hash'] == self.her_hash.hexdigest()):
                if msg_parsed['username'] == self.username:
                    message = "{} < {}".format(
                        msg_parsed['message']['data']['message'], username)
                else:
                    message = "{} > {}".format(
                        username, msg_parsed['message']['data']['message'])
                self.show_message(message, msg_type)
            elif msg_parsed['message']['type'] == "join":
                join_payload = {
                    'type': 'join',
                    'data': {
                            'election': self.client.election,
                    },
                }
                if (self.join_time - datetime.datetime.now()).total_seconds() > 10:
                    self.join_time = datetime.datetime.now()
                    self.client.send(join_payload)
                if msg_parsed['message']['data']['election'] > self.client.election and msg_parsed['username'] != self.username and self.started == False:
                    self.started = True
                    self.my_hash = hashlib.md5(
                        (str(self.client.election)+self.username).encode())
                    self.her_hash = hashlib.md5(
                        (str(msg_parsed['message']['data']['election'])+msg_parsed['username']).encode())
                    print(self.my_hash.hexdigest())
                    print(self.her_hash.hexdigest())
                    print("IL COMMENCE")
                    self.delete_start_page()
                    self.client.send(join_payload)
                elif msg_parsed['username'] != self.username and self.started == False:
                    self.started = True
                    self.my_hash = hashlib.md5(
                        (str(self.client.election)+self.username).encode())
                    self.her_hash = hashlib.md5(
                        (str(msg_parsed['message']['data']['election'])+msg_parsed['username']).encode())
                    print(self.my_hash.hexdigest())
                    print(self.her_hash.hexdigest())
                    self.my_turn = True
                    print("TU COMMENCE")
                    self.delete_start_page()
                    self.client.send(join_payload)
            elif msg_parsed['message']['type'] == "game" and msg_parsed['message']['hash'] == self.her_hash.hexdigest():
                if "ready" in msg_parsed['message']['data']:
                    self.show_message("Le joueur d'en face est prêt !", "sys")
                    if self.my_turn and self.ready:
                        self.show_message("C'est à vous de commencer !", "sys")
                    self.his_ready = True
                if "result" in msg_parsed['message']['data']:
                    if msg_parsed['message']['data']['result']:
                        self.my_turn = True
                        self.show_message("C'est encore à vous", "sys")
                        self.my_score += 1
                        self.touched(msg_parsed['message']['data']['result_key'])
                    else:
                        self.my_turn = False
                    if self.my_score == 17:
                        self.create_page("Vous avez gagné")
                        
                        win = {
                            'type': 'game',
                            'hash': self.my_hash.hexdigest(),
                            'data': 
                            {
                                'winner': self.my_hash.hexdigest(),
                                'looser': self.her_hash.hexdigest(),
                            },
                        } 
                        self.client.send(win)

                if "key" in msg_parsed['message']['data']:
                    if msg_parsed['message']['data']['key'] in self.my_boats:
                        touched = {
                            'type': 'game',
                            'hash': self.my_hash.hexdigest(),
                            'data': {
                                'result': True,
                                'result_key': msg_parsed['message']['data']['key']
                            }
                        }
                        self.exploded(msg_parsed['message']['data']['key'])
                        self.client.send(touched)
                        self.her_score += 1
                        self.my_turn = False
                        if self.her_score == 17:
                            self.create_page("Vous avez perdu")

                            # loose = {
                            #     'type': 'win',
                            #     'hash': self.my_hash.hexdigest(),
                            #     'data': 
                            #     {
                            #         'winner': self.her_hash.hexdigest(),
                            #         'looser': self.my_hash.hexdigest()
                            #     },
                            # } 
                            # self.client.send(loose)
                    else:
                        missed = {
                            'type': 'game',
                            'hash': self.my_hash.hexdigest(),
                            'data': {
                                'result': False,
                            },
                        }
                        self.show_message("C'est à vous", "sys")
                        self.client.send(missed)
                        self.my_turn = True
                    print(msg_parsed['message']['data']['key'])
            else:
                print(msg_parsed['message'])


if __name__ == "__main__":
    app = BattleShip()
    app.mainloop()
