import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import math

labels = {}
DEBUG = False
STEP = 40
SAVE_BUTTON_EXISTS = False
SAVED = False
delimeter: float = 0.001
SAVED_TEXT_SHOWN = False


class Point:

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
        self.modified = False

    def __float__(self, mode):
        if mode == 'X':
            return self.x
        else:
            return self.y

    def move(self, x_shift, y_shift):
        self.x += x_shift
        self.y += y_shift
        pass

    def __str__(self):
        result = "Point = (" + str(self.x) + ";" + str(self.y) + ")"
        return result


class Vector:

    def __init__(self, start: Point, end: Point, master: str = "None"):
        self.start = start
        self.end = end
        self.x_dir = 1
        self.y_dir = 1
        self.master = master
        if end.x < start.x:
            self.x_dir = -1
        if end.y < start.y:
            self.y_dir = -1
        self.angle, self.k = get_angle(start, end)
        self.normal = Point()
        if self.master == "rectangle":
            if end.x == start.x and end.y < start.y:
                self.normal.x = -1
                self.normal.y = 0
            elif end.x == start.x and end.y > start.y:
                self.normal.x = 1
                self.normal.y = 0
            elif end.x < start.x and end.y == start.y:
                self.normal.x = 0
                self.normal.y = 1
            elif end.x > start.x and end.y == start.y:
                self.normal.x = 0
                self.normal.y = -1
        else:
            k_normal = - 1 / self.k
            x_solutions = [sign * math.sqrt(1 / (k_normal * k_normal + 1)) for sign in (-1, 1)]
            y_solutions = [sign * (k_normal * math.sqrt(1 / (k_normal * k_normal + 1))) for sign in (-1, 1)]

    def __str__(self):
        result = ""
        result += "Start = (" + str(self.start.x) + ";" + str(self.start.y) + ")"
        result += "End = (" + str(self.end.x) + ";" + str(self.end.y) + ")"
        return result


def similar_vector(input_vector: Vector) -> Vector:
    pass


class LabelEntry:
    def __init__(self, root_window: tk.Tk, label_object: tk.Label, entry: tk.Entry, name: str):
        self.root = root_window
        self.label = label_object
        self.entry = entry
        self.name = name
        global labels
        labels.update({self.name: self})

    @classmethod
    def from_labels_text(cls, root_window, label_text: str, entry_default_text: str, name):
        entry = tk.Entry(root_window, width=20)
        entry.insert(0, entry_default_text)
        return cls(root_window, tk.Label(root_window, width=30, text=label_text), entry, name)

    def __str__(self):
        return

    def pack(self):
        self.label.pack()
        self.entry.pack()


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
        x_shift = (vector.normal.x * (diam / 2)) + (vector.normal.y * (diam / 2)) + offset
        y_shift = -(vector.normal.x * (diam / 2)) + (vector.normal.y * (diam / 2)) + offset
        start.move(x_shift, y_shift)
        start.modified = True
    if not end.modified:
        x_shift = (vector.normal.x * (diam / 2)) - (vector.normal.y * (diam / 2)) + offset
        y_shift = (vector.normal.x * (diam / 2)) + (vector.normal.y * (diam / 2)) + offset
        end.move(x_shift, y_shift)
        end.modified = True


def output_convertation(data, sign=1, step=STEP) -> str:
    result = (int(float(data) * step) * sign)
    return str(result)


def calculate(text_field: TextField, root_window: tk.Tk):
    global labels, SAVED, SAVE_BUTTON_EXISTS
    saved_text.pack_forget()
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
        new_button = tk.Button(root_window, width=30, text="Save", command=lambda: save_button(text_field))
        new_button.pack()
        plotter_button = tk.Button(root_window, width=30, command=lambda: show_plot(points), text="Show plot")
        plotter_button.pack()
        SAVE_BUTTON_EXISTS = True


def show_plot(points: List[Point]):
    plt.figure(figsize=(9, 9))
    plt.plot([points[i].x for i in range(len(points))] + [points[0].x]
             , [points[i].y for i in range(len(points))] + [points[0].y]
             , color='black', linewidth=1.5
             ,
             )
    plt.ylabel('Ycoord')
    plt.xlabel("Xcoord")
    plt.minorticks_on()
    plt.grid(which="major", color='grey', linewidth=0.75)
    plt.xticks(np.arange((int(points[0].x - 50) // 50 - 1) * 50, (int(points[2].x + 50) // 50 + 3) * 50, 100))
    plt.yticks(np.arange((int(points[1].y - 50) // 50 - 1) * 50, (int(points[0].y + 50) // 50 + 3) * 50, 100))
    for point in points:
        plt.annotate(xy=(point.x + 5, point.y + 5),
                     s="(" + "{:.4f}".format(point.x) + ";" + "{:.4f}".format(point.y) + ")")

    plt.show()


def save_button(text_field: TextField):
    global SAVED, SAVED_TEXT_SHOWN
    saved_text.pack_forget()
    filename = labels["length"].entry.get() + "x" + labels["width"].entry.get() \
               + "d" + labels["freza"].entry.get() + "(" + labels["zero_p"].entry.get() \
               + ";" + labels["zero_p"].entry.get() + ").plt"
    result = text_field.txt.get(1.0, tk.END)
    default_file = labels["path"].entry.get() + "\\" + filename
    file = open(default_file, "w")
    file.write(result)
    file.close()
    save_path.set("Saved to " + default_file)
    saved_text.pack()
    SAVED = True


def get_angle(start: Point, end: Point) -> List[float]:
    start_x = start.x
    start_y = start.y
    end_x = end.x
    end_y = end.y
    angle, k = float(), float()
    current_quarter = 0
    if (abs(start_x - end_x) < delimeter):
        if (start_y < end_y):
            angle = 90
        else:
            angle = -90
        return [angle, math.atan(angle)]
    elif (abs(start_y - end_y) < delimeter):
        if (start_x > end_x):
            angle = 180
        else:
            angle = 0
        return [angle, math.atan(angle)]
    else:
        k = (start_y - end_y) / (start_x - end_x)
        angle = math.atan(k) * 180 / math.pi
        quarters = dict()
        quarters.update({1: end_x > start_x and end_y > start_y})
        quarters.update({-1: end_x > start_x and end_y < start_y})
        quarters.update({-2: end_x < start_x and end_y < start_y})
        quarters.update({2: end_x < start_x and end_y > start_y})

        for key in quarters.keys():
            if (quarters[key]):
                current_quarter = key
                break

        angle = math.atan(k) * 180 / math.pi
        if (current_quarter % 2 == 0):
            angle += 90 * (current_quarter / abs(current_quarter))
    return [angle, k]


def path_taker_button(path_label_entry: LabelEntry):
    path_label_entry.entry.delete(0, tk.END)
    filepath = filedialog.askdirectory().replace("/", "\\")
    path_label_entry.entry.insert(0, filepath)


if __name__ == '__main__':
    root = tk.Tk()
    default_path = "\\\\SHIELD-35\\second\\"
    save_path = tk.StringVar(value="")
    saved_text = tk.Label(root, textvariable=save_path)
    thickness = LabelEntry.from_labels_text(root, "Толщина материала(мм)", "6", "thickness")
    length = LabelEntry.from_labels_text(root, "Длина(ось Х), мм", "1050", "length")
    width = LabelEntry.from_labels_text(root, "Ширина(ось Y), мм", "730", "width")
    freza = LabelEntry.from_labels_text(root, "Диаметр инструмента, мм", "3.175", "freza")
    x_feed = LabelEntry.from_labels_text(root, "Подача линейная, мм/сек", "60", "x_feed")
    z_feed = LabelEntry.from_labels_text(root, "Подача врезания, мм/сек", "30", "z_feed")
    zero_p = LabelEntry.from_labels_text(root, "Отступ от нуля(х и у), мм", "2", "zero_p")
    safety_height = LabelEntry.from_labels_text(root, "Высота безопасности, мм", "40", "safety_height")
    for label in labels.values():
        label.pack()
    text = TextField(root)
    text.pack(fill="both", expand=True)
    text.config(width=500, height=500)
    path = LabelEntry.from_labels_text(root, "Папка сохранения", default_path, "path")
    path.pack()
    path_button = tk.Button(root, width=30, text="Browse", command=lambda: path_taker_button(path))
    path_button.pack()
    button1 = tk.Button(root, width=30, command=lambda: calculate(text, root), text="show calculated")
    button1.pack()
    root.mainloop()
