import tkinter as tk
import os
import json
import math
import heapq
from tkinter import simpledialog, messagebox, filedialog
from PIL import Image, ImageTk

canvas_w = 800
canvas_h = 600
pin_node_rad = 10
node_rad = 3
pin_hit_rad = pin_node_rad + 5
default_hit_rad = node_rad + 2
config_path = "config.json"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MapGraph')
        self.geometry(f'{canvas_w}x{canvas_h+80}')
        self.nodes = []
        self.connections = []
        self.selected_node = None
        self.mode = 'default'
        self.bg_image = None
        self.path_lines = []

        self.canvas = tk.Canvas(self, width=canvas_w, height=canvas_h, bg='white')
        self.canvas.pack(side='top', fill='both', expand=True)

        bot_frame = tk.Frame(self, bg='lightgrey')
        bot_frame.pack(side='bottom', fill='x')

        tk.Button(bot_frame, text='Pin Node', command=self.set_pin_mode).pack(side='left')
        tk.Button(bot_frame, text='Default Node', command=self.set_default_mode).pack(side='left')
        tk.Button(bot_frame, text='Connect Nodes', command=self.set_connect_mode).pack(side='left')
        tk.Button(bot_frame, text='Remove Node', command=self.set_remove_mode).pack(side='left')
        tk.Button(bot_frame, text='Djikstra', command=self.set_djikstra_mode).pack(side='left')
        tk.Button(bot_frame, text='Export', command=self.export_json).pack(side='right')
        tk.Button(bot_frame, text='Import', command=self.import_json).pack(side='right')

        self.info = tk.Label(bot_frame, text='Mode: default | Nodes: 0 | Koneksi: 0', bg="#222", fg="white")
        self.info.pack(side='left', padx=10)

        self.canvas.bind('<Button-1>', self.on_click)

        self.load_bg('img/bg_map2.png') # <- you can change this with your own map

        self.update_info()

        self.nodes = []
        self.connections = []

        self.spawn_nodes_from_data()

    def export_json(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if not file_path:
            return

        data = {
            "nodes": [],
            "connections": self.connections
        }

        for node in self.nodes:
            if node["type"] == "pin":
                data["nodes"].append({
                    "type": "pin",
                    "x": node["x"],
                    "y": node["y"],
                    "name": node["name"]
                })
            elif node["type"] == "default":
                data["nodes"].append({
                    "type": "default",
                    "x": node["x"],
                    "y": node["y"]
                })

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print("Export berhasil:", file_path)

    def import_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")]
        )
        if not file_path:
            return

        with open(file_path, "r") as f:
            data = json.load(f)

        self.nodes = []
        self.connections = []
        self.canvas.delete("all")

        if self.bg_image:
            self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')

        for n in data["nodes"]:
            if n["type"] == "pin":
                x, y, name = n["x"], n["y"], n["name"]
                px, py, pname, node_id, text_id = self.draw_pin_node(x, y, name)
                self.nodes.append({"x": x, "y": y, "name": name, "type": "pin",
                                "node_id": node_id, "text_id": text_id})
            else:
                x, y = n["x"], n["y"]
                x2, y2, node_id = self.draw_default_node(x, y)
                self.nodes.append({"x": x, "y": y, "type": "default",
                                "node_id": node_id})

        for a, b in data["connections"]:
            self.connections.append((a, b))

            x1, y1 = self.nodes[a]['x'], self.nodes[a]['y']
            x2, y2 = self.nodes[b]['x'], self.nodes[b]['y']

            self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)

        print("Import berhasil", file_path)

    def load_bg(self, file_path):
        if not os.path.exists(file_path):
            print(f"File {file_path} tidak ditemukan.")
            return

        image = Image.open(file_path)
        image = image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
    
    def spawn_nodes_from_data(self):
        new_nodes = []
    
        for node in self.nodes:
            if len(node) == 5:
                x, y, name = node[0], node[1], node[2]
                new_node = self.draw_pin_node(x, y, name)
                new_nodes.append(new_node)

            elif len(node) == 3:
                # default node
                x, y = node[0], node[1]
                new_node = self.draw_default_node(x, y)
                new_nodes.append(new_node)

        self.nodes = new_nodes

        for (a, b) in self.connections:
            x1, y1 = a
            x2, y2 = b
            self.draw_connection(x1, y1, x2, y2)

    def draw_pin_node(self, x, y, name):
        node_id = self.canvas.create_oval(
            x - pin_node_rad, y - pin_node_rad,
            x + pin_node_rad, y + pin_node_rad,
            fill='green', outline='black', width=3
        )
        text_id = self.canvas.create_text(
            x, y - 30, text=name,
            fill='black', font=('Arial', 12, 'bold')
        )
        return (x, y, name, node_id, text_id)
    
    def draw_default_node(self, x, y):
        node_id = self.canvas.create_oval(
            x - node_rad, y - node_rad,
            x + node_rad, y + node_rad,
            fill='lightblue', outline='black', width=1.5
        )
        return (x, y, node_id)
    def draw_connection(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)

    def set_pin_mode(self):
        self.mode = 'pin'
        self.selected_node = None
        self.update_info()

    def set_default_mode(self):
        self.mode = 'default'
        self.selected_node = None
        self.update_info()

    def set_connect_mode(self):
        self.mode = 'connect'
        self.selected_node = None
        self.update_info()
    
    def set_remove_mode(self):
        self.mode = 'remove'
        self.selected_node = None
        self.update_info()
    
    def set_djikstra_mode(self):
        self.mode = 'djikstra'
        self.selected_node = None
        self.clear_path_lines()
        self.update_info()

    def update_info(self):
        self.info.config(text=f'Mode: {self.mode} | Nodes: {len(self.nodes)} | Koneksi: {len(self.connections)}')

    def on_click(self, event):
        if self.mode == 'pin':
            self.pin_node(event.x, event.y)
        elif self.mode == 'default':
            self.default_node(event.x, event.y)
        elif self.mode == 'remove':
            self.remove_node(event.x, event.y)
        elif self.mode == 'connect':
            self.connect_node(event.x, event.y)
        elif self.mode == 'djikstra':
            self.select_djikstra(event.x, event.y)
        self.update_info()

    def pin_node(self, x, y):
        name = simpledialog.askstring("Nama Node", "Masukkan nama node:")
        if not name: return

        node_id = self.canvas.create_oval(
            x - pin_node_rad, y - pin_node_rad, x + pin_node_rad, y + pin_node_rad,
            fill='green', outline='black', width=3
        )
        text_id = self.canvas.create_text(x, y - 30, text=name, fill='black', font=('Arial', 12, 'bold'))
        self.nodes.append(({'x': x, 'y': y, 'type' : 'pin', 'name': name, 'node_id': node_id, 'text_id': text_id}))

    def default_node(self, x, y):
        
        node_id = self.canvas.create_oval(
            x - node_rad, y - node_rad, x + node_rad, y + node_rad,
            fill='lightblue', outline='black', width=1.5
        )
        self.nodes.append({'x': x, 'y': y, 'type': 'default', 'node_id': node_id})
    
    def connect_node(self, x, y):
        clicked_node = self.find_node_index(x, y)
        if clicked_node is None: return

        if self.selected_node is None:
            self.selected_node = clicked_node
            print(f'Node dipilih: {clicked_node} ({self.nodes[clicked_node].get("name", "default")})')
        else:
            if self.selected_node == clicked_node:
                messagebox.showwarning('Peringatan', 'Ga bisa connect ke node yang sama oi')
                self.selected_node = None
                return
            
            a, b = self.selected_node, clicked_node
            if (a, b) in self.connections or (b, a) in self.connections:
                messagebox.showwarning('Peringatan', 'Udah connect bro')
                self.selected_node = None
                return
            self.connections.append((a,b))
            x1, y1 = self.nodes[a]['x'], self.nodes[a]['y']
            x2, y2 = self.nodes[b]['x'], self.nodes[b]['y']
            self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)
            print(f'Terkoneksi: {a} -> {b}')
            self.selected_node = None
    
    def remove_node(self, x, y):
        index = self.find_node_index(x, y)
        if index is None: return

        node = self.nodes[index]
        try:
            self.canvas.delete(node['node_id'])
        except Exception: pass

        if 'text_id' in node:
            try:
                self.canvas.delete(node['text_id'])
            except Exception: pass

        new_connections = []
        for a, b in self.connections:
            if a == index or b == index:
                continue
            new_a = a - 1 if a > index else a
            new_b = b - 1 if b > index else b
            new_connections.append((new_a, new_b))
            self.nodes.pop(index)
            self.redraw_all()

    def find_node_index(self, x, y):
        for i, node in enumerate(self.nodes):
            nx, ny = node['x'], node['y']
            hit_rad = pin_hit_rad if node['type'] == 'pin' else default_hit_rad
            if (x - nx)**2 + (y - ny)**2 <= hit_rad**2:
                return i
        return None
    
    def redraw_all(self):
        self.canvas.delete('all')
        if self.bg_image:
            self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')

        for a, b in self.connections:
            x1, y1 = self.nodes[a]['x'], self.nodes[a]['y']
            x2, y2 = self.nodes[b]['x'], self.nodes[b]['y']
            self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)

        for node in self.nodes:
            x, y = node['x'], node['y']
            if node['type'] == 'pin':
                node_id = self.canvas.create_oval(
                    x - pin_node_rad, y - pin_node_rad, x + pin_node_rad, y + pin_node_rad,
                    fill='green', outline='black', width=3
                )
                text_id = self.canvas.create_text(x, y - 30, text=node['name'], fill='black', font=('Arial', 12, 'bold'))
                node['node_id'] = node_id
                node['text_id'] = text_id
            else:
                node_id = self.canvas.create_oval(
                    x - node_rad, y - node_rad, x + node_rad, y + node_rad,
                    fill='lightblue', outline='black', width=1.5
                )
                node['node_id'] = node_id

    def select_djikstra(self, x, y):
        index = self.find_node_index(x, y)
        if index is None: return

        if self.selected_node is None:
            self.selected_node = index
            print(f'Node awal djikstra: {index} ({self.nodes[index].get("name", "default")})')
            self.update_info()
            return
            
        start_index = self.selected_node
        end_index = index
        if start_index == end_index:
            messagebox.showwarning('Peringatan', 'Node awal dan akhir jangan sama')
            self.selected_node = None
            return
            
        self.clear_path_lines()
        graph = self.build_graph()
        dist, prev = self.run_djikstra(graph, start_index)
        if end_index not in dist or dist[end_index] == float('inf'):
            messagebox.showwarning('Peringatan', 'Tidak ada jalur antara kedua node')
            self.selected_node = None
            return
            
        path = []
        cur = end_index
        while cur is not None:
            path.append(cur)
            cur = prev.get(cur)
        path.reverse()

        for i in range(len(path)-1):
            a, b = path[i], path[i+1]
            x1, y1 = self.nodes[a]['x'], self.nodes[a]['y']
            x2, y2 = self.nodes[b]['x'], self.nodes[b]['y']
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill='lightgreen', width=4)
            self.path_lines.append(line_id)

        names = [self.nodes[i].get('name', f'node{i}') for i in path]
        messagebox.showinfo('Djikstra', f'Node yang dilalui: {len(path)}\nJarak: {dist[end_index]:.2f}')
        self.selected_node = None
        self.update_info()

    def clear_path_lines(self):
        for line_id in self.path_lines:
            try:
                self.canvas.delete(line_id)
            except Exception:
                pass
        self.path_lines = []

    def build_graph(self):
        g = {i: [] for i in range(len(self.nodes))}
        for a, b in self.connections:
            x1, y1 = self.nodes[a]['x'], self.nodes[a]['y']
            x2, y2 = self.nodes[b]['x'], self.nodes[b]['y']
            w = math.hypot(x1-x2, y1-y2)
            g[a].append((b, w))
            g[b].append((a, w))
        return g
    
    def run_djikstra(self, graph, start):
        dist = {node: float('inf') for node in graph}
        prev = {node: None for node in graph}
        dist[start] = 0
        heap = [(0, start)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, w in graph[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        return dist, prev
if __name__ == '__main__':
    App().mainloop()

    #tugas: tambahin algoritma djikstra buat nyari jalur terpendek antara dua node yang dipilih (done)