import tkinter as tk
import os
import json
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk

canvas_w = 800
canvas_h = 600
pin_node_rad = 10
node_rad = 5
pin_hit_rad = pin_node_rad + 5
default_hit_rad = node_rad + 2

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Sambung sambung Node')
        self.geometry(f'{canvas_w}x{canvas_h+80}')

        self.default_nodes = []
        self.pin_nodes = []
        self.default_connection = []
        self.pin_connection = []

        self.selected_node = None
        self.mode = 'default'
        self.config_mode = False
        self.bg_image = None
        self.path_lines = []

        self.canvas = tk.Canvas(self, width=canvas_w, height=canvas_h, bg='white')
        self.canvas.pack(side='top', fill='both', expand=True)

        self.bot_frame = tk.Frame(self, bg='lightgrey')
        self.bot_frame.pack(side='bottom', fill='x')

        self.info = tk.Label(self.bot_frame, text='Mode: Normal', bg="#222", fg="white")
        self.info.pack(side='left', padx=10)

        self.canvas.bind('<Button-1>', self.on_click)

        self.load_bg('img/bg_map.png')
        self.create_main_buttons()

    def load_bg(self, file_path):
        if not os.path.exists(file_path):
            print(f"File {file_path} tidak ditemukan.")
            return

        image = Image.open(file_path)
        image = image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')

    def create_main_buttons(self):
        for items in self.bot_frame.winfo_children():
            if isinstance(items, tk.Button):
                items.destroy()
        
        tk.Button(self.bot_frame, text='Pin Node', command=self.set_pin_mode).pack(side='left')
        tk.Button(self.bot_frame, text='Connect Nodes', command=self.set_connect_mode).pack(side='left')
        tk.Button(self.bot_frame, text='Remove Node', command=self.set_remove_mode).pack(side='left')
        tk.Button(self.bot_frame, text='Config Mode', command=self.enter_config_mode).pack(side='left')

    def create_config_buttons(self):
        for items in self.bot_frame.winfo_children():
            if isinstance(items, tk.Button):
                items.destroy()
        
        tk.Button(self.bot_frame, text='Add Node', command=self.set_default_mode).pack(side='left')
        tk.Button(self.bot_frame, text='Remove Node', command=self.set_remove_mode).pack(side='left')
        tk.Button(self.bot_frame, text='Save Config', command=self.save_config).pack(side='left')
        tk.Button(self.bot_frame, text='Back', command=self.exit_config_mode).pack(side='left')

    def enter_config_mode(self):
        self.config_mode = True
        self.mode = 'default'
        self.create_config_buttons()
        self.update_info()
        print("Config mode")

    def exit_config_mode(self):
        self.config_mode = False
        self.mode = 'default'
        self.create_main_buttons()
        self.update_info()
        print("Exit config mode")

    def save_config(self):
        config = {
            'default_nodes': self.default_nodes,
            'default_connections': self.default_connection,
        }

        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", "Konfigurasi berhasil disimpan ke config.json")
            print("Config saved to config.json")
            self.clear_canvas()
            self.exit_config_mode()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan config: {str(e)}")
            print(f"Error saving config: {e}")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.load_bg('img/bg_map.png')

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

    # def set_djikstra_mode(self):
    #     self.mode = 'djikstra'
    #     self.selected_node = None
    #     self.update_info()

    def update_info(self):
        default_count = len(self.default_nodes)
        pin_count = len(self.pin_nodes)
        self.info.config(text=f'Mode: {self.mode} | Default: {default_count} | Pin: {pin_count} | Config: {self.config_mode}')

    def on_click(self, event):
        if self.config_mode:
            if self.mode == 'default':
                self.default_node(event.x, event.y)
            elif self.mode == 'remove':
                self.remove_node(event.x, event.y)
        else:
            if self.mode == 'pin':
                self.pin_node(event.x, event.y)
            elif self.mode == 'connect':
                self.connect_node(event.x, event.y)
            elif self.mode == 'remove':
                self.remove_node(event.x, event.y)
            else:
                pass
            
        self.update_info()

    def pin_node(self, x, y):
        name = simpledialog.askstring("Nama Node", "Masukkan nama node:")
        if not name: return

        node_id = self.canvas.create_oval(
            x - pin_node_rad, y - pin_node_rad, x + pin_node_rad, y + pin_node_rad,
            fill='green', outline='black', width=3
        )
        text_id = self.canvas.create_text(x, y - 30,
                                            text=name, fill='black', font=('Arial', 12, 'bold'))
        self.pin_nodes.append({
            'x': x,
            'y': y,
            'name': name,
            'node_id': node_id,
            'text_id': text_id
        })
        print(f"Pin node created at ({x}, {y})")

    def default_node(self, x, y):
        
        node_id = self.canvas.create_oval(
            x - node_rad, y - node_rad, x + node_rad, y + node_rad,
            fill='lightblue', outline='black', width=1.5
        )
        self.default_nodes.append({
            'x': x,
            'y': y,
            'node_id': node_id
        })
        print(f"Default node created at ({x}, {y})")
    
    def connect_node(self, x, y):
        hit_node = None
        node_type = None
        
        # Check if click hits any pin node
        for i, node in enumerate(self.pin_nodes):
            px, py = node['x'], node['y']
            if (x - px)**2 + (y - py)**2 <= pin_hit_rad**2:
                hit_node = (i, node)
                node_type = 'pin'
                break
        
        if hit_node is None:
            return
        
        # First node selected
        if self.selected_node is None:
            self.selected_node = {
                'index': hit_node[0],
                'type': node_type,
                'node': hit_node[1],
                'coords': (hit_node[1]['x'], hit_node[1]['y'])
            }
            print(f"Selected pin node: {hit_node[1]['name']}")
            return
        
        # Second node selected - create connection
        x1, y1 = self.selected_node['coords']
        x2, y2 = hit_node[1]['x'], hit_node[1]['y']
        
        # Draw line
        line_id = self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)
        
        # Store connection
        connection = {
            'from': self.selected_node,
            'to': {
                'index': hit_node[0],
                'type': node_type,
                'node': hit_node[1],
                'coords': (hit_node[1]['x'], hit_node[1]['y'])
            },
            'line_id': line_id
        }
        
        self.pin_connection.append(connection)
        print(f"Connected pin nodes: {self.selected_node['node']['name']} -> {hit_node[1]['name']}")
        
        self.selected_node = None
    
    def remove_node(self, x, y):
        if self.config_mode:
            for i, node in enumerate(self.default_nodes):
                px, py = node['x'], node['y']
                if (x - px)**2 + (y - py)**2 <= default_hit_rad**2:
                    self.canvas.delete(node['node_id'])
                    self.default_nodes.pop(i)
                    print(f"Default node removed at ({px}, {py})")
                    return
        else:
            for i, node in enumerate(self.pin_nodes):
                px, py = node['x'], node['y']
                if (x - px)**2 + (y - py)**2 <= pin_hit_rad**2:
                    self.canvas.delete(node['node_id'])
                    self.canvas.delete(node['text_id'])
                    self.pin_nodes.pop(i)
                    print(f"Pin node removed: {node['name']}")
                    return

if __name__ == '__main__':
    App().mainloop()

    #tugas: node yang ada namanya -> node pin , ini pake button (done)
    #tugas: tambahin node dummy, ini default (done)
    #tugas: load peta untuk jadi background, lalu disimpan konfigurasinya (done)