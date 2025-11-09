import tkinter as tk
import os
from tkinter import simpledialog
from PIL import Image, ImageTk

canvas_w = 800
canvas_h = 600
pin_node_rad = 10
node_rad = 5
pin_hit_rad = pin_node_rad + 5
default_hit_rad = node_rad + 5

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Sambung sambung Node')
        self.geometry(f'{canvas_w}x{canvas_h+80}')
        self.nodes = []
        self.connections = []
        self.selected_node = None
        self.mode = 'default'
        self.bg_image = None

        self.canvas = tk.Canvas(self, width=canvas_w, height=canvas_h, bg='white')
        self.canvas.pack(side='top', fill='both', expand=True)

        bot_frame = tk.Frame(self, bg='lightgrey')
        bot_frame.pack(side='bottom', fill='x')

        tk.Button(bot_frame, text='Pin Node', command=self.set_pin_mode).pack(side='left')
        tk.Button(bot_frame, text='Default Node', command=self.set_default_mode).pack(side='left')
        tk.Button(bot_frame, text='Connect Nodes', command=self.set_connect_mode).pack(side='left')
        tk.Button(bot_frame, text='Remove Node', command=self.set_remove_mode).pack(side='left')

        self.info = tk.Label(bot_frame, text='Mode: add | Nodes: 0', bg="#222", fg="white")
        self.info.pack(side='left', padx=10)

        self.canvas.bind('<Button-1>', self.on_click)

        self.load_bg('img/bg_map.png')

    def load_bg(self, file_path):
        if not os.path.exists(file_path):
            print(f"File {file_path} tidak ditemukan.")
            return

        image = Image.open(file_path)
        image = image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')

    def set_pin_mode(self):
        self.mode = 'pin'
        self.update_info()

    def set_default_mode(self):
        self.mode = 'default'
        self.update_info()

    def set_connect_mode(self):
        self.mode = 'connect'
        self.selected_node = None
        self.update_info()
    
    def set_remove_mode(self):
        self.mode = 'remove'
        self.update_info()

    def update_info(self):
        self.info.config(text=f'Mode: {self.mode} | Nodes: {len(self.nodes)}')

    def on_click(self, event):
        if self.mode == 'pin':
            self.pin_node(event.x, event.y)
        elif self.mode == 'default':
            self.default_node(event.x, event.y)
        elif self.mode == 'remove':
            self.remove_node(event.x, event.y)
        elif self.mode == 'connect':
            self.connect_node(event.x, event.y)
        self.update_info()

    def pin_node(self, x, y):
        name = simpledialog.askstring("Nama Node", "Masukkan nama node:")
        if not name: return

        node_id = self.canvas.create_oval(
            x - pin_node_rad, y - pin_node_rad, x + pin_node_rad, y + pin_node_rad,
            fill='green', outline='black', width=3
        )
        text_id = self.canvas.create_text(x, y - 30
        , text=name, fill='black', font=('Arial', 12, 'bold'))
        self.nodes.append((x, y, name, node_id, text_id))

    def default_node(self, x, y):
        
        node_id = self.canvas.create_oval(
            x - node_rad, y - node_rad, x + node_rad, y + node_rad,
            fill='lightblue', outline='black', width=1.5
        )
        self.nodes.append((x, y, node_id))
    
    def connect_node(self, x, y):
        for node in self.nodes:
            if len(node) == 5:
                px, py, name, node_id, text_id = node
            elif len(node) == 3:
                px, py, node_id = node
            else: continue

            if (x - px)**2 + (y - py)**2 <= pin_hit_rad**2:
                if self.selected_node is None:
                    self.selected_node = (px, py)
                    print(f"Selected node: {name if len(node) == 5 else 'default node'}")
                else:
                    x1, y1 = self.selected_node
                    x2, y2 = px, py
                    self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)
                    self.connections.append(((x1, y1), (x2, y2)))
                    print(f"Connected nodes: {self.selected_node[2] if len(self.selected_node) == 5 else 'default node'} -> {name if len(node) == 5 else 'default node'}")
                    self.selected_node = None
                break
    
    def remove_node(self, x, y):
        for i, node in enumerate(self.nodes):
            if len(node) == 5:
                px, py, name, node_id, text_id = node
                if (x - px)**2 + (y - py)**2 <= pin_hit_rad**2:
                    print(f"Hit detected on pin node: {name}")
                    self.canvas.delete(node_id)
                    self.canvas.delete(text_id)
                    self.nodes.pop(i)
                    break
            elif len(node) == 3:
                px, py, node_id = node
                if (x - px)**2 + (y - py)**2 <= default_hit_rad**2:
                    print("Hit detected on default node")
                    self.canvas.delete(node_id)
                    self.nodes.pop(i)
                    break

if __name__ == '__main__':
    App().mainloop()

    #tugas: node yang ada namanya -> node pin , ini pake button
    #tugas: tambahin node dummy, ini default
    #tugas: load peta untuk jadi background, lalu disimpan konfigurasinya