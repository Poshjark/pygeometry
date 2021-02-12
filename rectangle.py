import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
from geometry import *

labels = {}
DEBUG = False
STEP = 40
SAVE_BUTTON_EXISTS = False
SAVED = False

SAVED_TEXT_SHOWN = False
default_path = "\\\\SHIELD-35\\second\\"


class LabelEntry:
    def __init__(self, root_window: tk.Tk, label_object: tk.Label, entry: tk.Entry, name: str):
        self.root = root_window
        self.label = label_object
        self.entry = entry
        self.name = name
        global labels
        labels.update({self.name: self})

    @classmethod
    def from_labels_text(cls, root_window, label_text: str, entry_default_text: str, name, width=20):
        entry = tk.Entry(root_window, width=width)
        entry.insert(0, entry_default_text)
        label = tk.Label(root_window, width=30, text=label_text)
        return cls(root_window, label, entry, name)

    def __str__(self):
        return

    def pack(self):
        self.label.pack()
        self.entry.pack()

    def pack_forget(self):
        self.label.pack_forget()
        self.entry.pack_forget()


class TextField(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.txt = tk.Text(self, bg="black", fg='white', wrap=tk.WORD)
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        scrollb = ttk.Scrollbar(self, command=self.txt.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set


def calc_coord(offset, diam, vector: Vector):
    start = vector.start
    end = vector.end
    if not start.modified:
        x_shift =  (vector.normal.x * (diam / 2)) + (vector.normal.y * (diam / 2)) + offset
        y_shift = -(vector.normal.x * (diam / 2)) + (vector.normal.y * (diam / 2)) + offset
        start.move(x_shift,y_shift)
        start.modified = True
    if not end.modified:
        x_shift = (vector.normal.x * (diam / 2)) - (vector.normal.y * (diam / 2)) + offset
        y_shift = (vector.normal.x * (diam / 2)) + (vector.normal.y * (diam / 2)) + offset
        end.move(x_shift, y_shift)
        end.modified = True

def output_convertation(data, sign=1, step=STEP) -> str:
    result = (int(float(data) * step) * sign)
    return str(result)

def show_plot(points: List[Point]):
    plt.figure(figsize=(9, 9))
    plt.plot([points[i].x for i in range(len(points))] + [points[0].x]
             , [points[i].y for i in range(len(points))] + [points[0].y]
             , color='black', linewidth=float(labels["freza"].entry.get())
             ,
             )
    plt.ylabel('Ycoord')
    plt.xlabel("Xcoord")
    plt.minorticks_on()
    plt.grid(which="major", color='grey', linewidth=0.75)
    plt.xticks(np.arange((int(points[0].x - 50) // 50 - 1) * 50, (int(points[2].x + 50) // 50 + 3) * 50, 100))
    plt.yticks(np.arange((int(points[1].y - 50) // 50 - 1) * 50, (int(points[0].y + 50) // 50 + 3) * 50, 100))
    for point in points:
        plt.annotate(xy=(point.x+5,point.y+5),s= "(" + "{:.4f}".format(point.x)  + ";" + "{:.4f}".format(point.y) + ")")

    plt.show()


class RectangleWindow:

    def __init__(self):
        self.root = tk.Tk()
        back_button = tk.Button(text="Back",command=self.back_button, anchor="w")
        back_button.pack_configure(side=tk.TOP)
        back_button.pack()
        if type(self) is LineWindow:
            self.axis = tk.StringVar()
            self.axis.set("X")
            tk.Radiobutton(self.root, variable=self.axis, value="X", text="Ось X", anchor=tk.E).pack()
            tk.Radiobutton(self.root, variable=self.axis, value="Y", text="Ось Y", anchor=tk.N).pack()
        self.root.iconbitmap("C:\\Users\\Frezer\\Desktop\\python_scripts\\rect_new\\rectangle.ico")
        self.root.title("Rectangle")
        self.save_path = tk.StringVar(value="")
        self.saved_text = tk.Label(self.root, textvariable=self.save_path)
        self.thickness = LabelEntry.from_labels_text(self.root, "Толщина материала(мм)", "6", "thickness")
        self.length = LabelEntry.from_labels_text(self.root, "Длина(ось Х), мм", "1050", "length")
        self.width = LabelEntry.from_labels_text(self.root, "Ширина(ось Y), мм", "730", "width")
        self.freza = LabelEntry.from_labels_text(self.root, "Диаметр инструмента, мм", "3.175", "freza")
        self.x_feed = LabelEntry.from_labels_text(self.root, "Подача линейная, мм/сек", "60", "x_feed")
        self.z_feed = LabelEntry.from_labels_text(self.root, "Подача врезания, мм/сек", "30", "z_feed")
        self.zero_p = LabelEntry.from_labels_text(self.root, "Отступ от нуля(х и у), мм", "2", "zero_p")
        self.safety_height = LabelEntry.from_labels_text(self.root, "Высота безопасности, мм", "40", "safety_height")
        for label in labels.values():
            label.pack()
        self.text = TextField(self.root)
        self.text.pack(fill="both", expand=True)
        self.text.config(width=500, height=500)
        self.path = LabelEntry.from_labels_text(self.root, "Папка сохранения", default_path, "path", width=100)
        self.path.pack()
        self.path_button = tk.Button(self.root, width=30, text="Browse", command=lambda: self.path_taker_button())
        self.path_button.pack()
        self.button1 = tk.Button(self.root, width=30, command=lambda: self.calculate(self.text, self.root), text="show calculated")
        self.button1.pack()

    def back_button(self):
        self.root.destroy()
        labels.clear()
        ChoiceWindow()
        return

    def calculate(self,text_field: TextField, root_window: tk.Tk):
        global labels, SAVED, SAVE_BUTTON_EXISTS
        self.saved_text.pack_forget()
        SAVED = False
        result = []
        start = "IN;PA;ZZ1;SP1;SF64;"
        end = "SP0;"
        first_coord = output_convertation(0 - float(labels["freza"].entry.get()) / 2
                                          + float(labels["zero_p"].entry.get())) \
                      + "," + output_convertation(float(labels["width"].entry.get())
                                                  + float(labels["freza"].entry.get()) / 2
                                                  + float(labels["zero_p"].entry.get())
                                                  )
        safe_height = output_convertation(labels["safety_height"].entry.get(), sign=-1) + ";"
        material_thickness = output_convertation(labels["thickness"].entry.get()) + ";"
        result.append(start + "PU" + first_coord + "," + safe_height)
        result.append("SF" + output_convertation(labels["z_feed"].entry.get(), step=1) + ";")
        result.append("PD" + first_coord + "," + material_thickness)
        result.append("SF" + output_convertation(labels["x_feed"].entry.get(), step=1) + ";")
        x = float(labels["length"].entry.get())
        y = float(labels["width"].entry.get())
        points = [Point(0, y), Point(0, 0), Point(x, 0), Point(x, y), Point(0, y)]
        vectors = [Vector(points[i], points[i + 1], master="rectangle") for i in range(len(points) - 1)]

        for vector in vectors:
            calc_coord(float(labels["zero_p"].entry.get()), float(labels["freza"].entry.get()), vector)
            if DEBUG:
                print(vector)

        for vector in vectors:
            result.append("PD" + output_convertation(vector.end.x)
                          + "," + output_convertation(vector.end.y) + ","
                          + output_convertation(labels["thickness"].entry.get()) + ";")
            if DEBUG:
                print(vector.angle, end="\n")
        result.append("SF64;")
        result.append("PU" + first_coord + "," + safe_height)
        result.append("SF64;")
        result.append("PU" + "0,0," + safe_height)
        result.append(end)
        text_field.txt.delete(1.0, tk.END)
        text_field.txt.insert(1.0, "".join(result))

        if not SAVE_BUTTON_EXISTS:
            new_button = tk.Button(root_window, width=30, text="Save", command=lambda: self.save_button())
            new_button.pack()
            plotter_button = tk.Button(root_window, width=30, command=lambda: show_plot(points), text="Show plot")
            plotter_button.pack()
            SAVE_BUTTON_EXISTS = True

    def path_taker_button(self):
        path_label_entry = self.path
        path_label_entry.entry.delete(0, tk.END)
        filepath = filedialog.askdirectory(initialdir=default_path).replace("/", "\\")
        if not filepath:
            path_label_entry.entry.insert(0, default_path)
        path_label_entry.entry.insert(0, filepath)

    def save_button(self):
        global SAVED, SAVED_TEXT_SHOWN
        self.saved_text.pack_forget()
        filename = labels["length"].entry.get() + "x" + labels["width"].entry.get() \
                   + "d" + labels["freza"].entry.get() + "(" + labels["zero_p"].entry.get() \
                   + ";" + labels["zero_p"].entry.get() + ").plt"
        result = self.text.txt.get(1.0, tk.END)
        default_file = labels["path"].entry.get() + filename
        file = open(default_file, "w")
        file.write(result)
        file.close()
        self.save_path.set("Saved to " + default_file)
        self.saved_text.pack()
        SAVED = True

    def mainloop(self):
        print("Parent mainloop!\n")
        self.root.mainloop()

class LineWindow(RectangleWindow):

    def __init__(self):
        super(LineWindow, self).__init__()
        self.root.iconbitmap("C:\\Users\\Frezer\\Desktop\\python_scripts\\rect_new\\line.ico")
        self.root.title("Line")
        self.width.pack_forget()
        self.zero_p.entry.delete(0,tk.END)
        self.zero_p.entry.insert(0,"0")
        self.length.entry.delete(0, tk.END)
        self.length.entry.insert(0, "1000")
        self.freza.entry.delete(0, tk.END)
        self.freza.entry.insert(0, "4")
        self.freza.entry.pack_configure()


    def calculate(self, text_field: TextField, root_window: tk.Tk):
        global labels, SAVED, SAVE_BUTTON_EXISTS
        self.saved_text.pack_forget()
        SAVED = False
        result = []
        start = "IN;PA;ZZ1;SP1;SF64;"
        end = "SP0;"
        zero_p = float(labels["zero_p"].entry.get())
        first_coord = output_convertation(float(labels["zero_p"].entry.get())) \
                      + "," + output_convertation(float(labels["zero_p"].entry.get()))
        safe_height = output_convertation(labels["safety_height"].entry.get(), sign=-1) + ";"
        material_thickness = output_convertation(labels["thickness"].entry.get()) + ";"
        result.append(start + "PU" + first_coord + "," + safe_height)
        result.append("SF" + output_convertation(labels["z_feed"].entry.get(), step=1) + ";")
        result.append("PD" + first_coord + "," + material_thickness)
        result.append("SF" + output_convertation(labels["x_feed"].entry.get(), step=1) + ";")
        length = float(self.length.entry.get())
        start_point = Point(zero_p,zero_p)
        end_point = Point(zero_p + length,zero_p) if self.axis.get() == "X" else Point(zero_p, zero_p + length)
        points = [start_point,end_point]
        vectors = [Vector(points[i], points[i + 1], master="line") for i in range(len(points) - 1)]
        for vector in vectors:
            result.append("PD" + output_convertation(vector.end.x)
                          + "," + output_convertation(vector.end.y) + ","
                          + output_convertation(labels["thickness"].entry.get()) + ";")
            if DEBUG:
                print(vector.angle, end="\n")
        result.append("SF64;")
        result.append("PU" + first_coord + "," + safe_height)
        result.append("SF64;")
        result.append("PU" + "0,0," + safe_height)
        result.append(end)
        text_field.txt.delete(1.0, tk.END)
        text_field.txt.insert(1.0, "".join(result))

        if not SAVE_BUTTON_EXISTS:
            new_button = tk.Button(root_window, width=30, text="Save", command=lambda: self.save_button())
            new_button.pack()
            plotter_button = tk.Button(root_window, width=30, command=lambda: show_plot(points), text="Show plot")
            plotter_button.pack()
            SAVE_BUTTON_EXISTS = True

    def save_button(self):
        global SAVED, SAVED_TEXT_SHOWN
        self.saved_text.pack_forget()
        filename = "Line" + self.axis.get() + labels["length"].entry.get() + "mm" \
                   + "d" + labels["freza"].entry.get() + "(" + labels["zero_p"].entry.get() \
                   + ";" + labels["zero_p"].entry.get() + ").plt"
        result = self.text.txt.get(1.0, tk.END)
        default_file = labels["path"].entry.get() + filename
        file = open(default_file, "w")
        file.write(result)
        file.close()
        self.save_path.set("Saved to " + default_file)
        self.saved_text.pack()
        SAVED = True

class ChoiceWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.configure(width=500, height=500)
        self.label = tk.Label(text="Choose mode")
        self.label.pack()
        tk.Button(text="Rectangle",command=self.rect_button_action).pack()
        tk.Button(text="Line",command=self.line_button_action).pack()
        self.root.mainloop()

    def rect_button_action(self):
        self.root.destroy()
        RectangleWindow().mainloop()


    def line_button_action(self):
        self.root.destroy()
        LineWindow().mainloop()


if __name__ == "__main__":
    ChoiceWindow()