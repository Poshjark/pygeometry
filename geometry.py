from typing import List
import math

delimeter:float = 0.001

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

def get_straigth_angle(start:Point,end:Point,normal_point:Point):
    if end.x == start.x and end.y < start.y:
        x = -1
        y = 0
    elif end.x == start.x and end.y > start.y:
        x = 1
        y = 0
    elif end.x < start.x and end.y == start.y:
        x = 0
        y = 1
    elif end.x > start.x and end.y == start.y:
        x = 0
        y = -1
    else:
        x = 0
        y = 0
    normal_point.x = x
    normal_point.y = y

class Vector:

    def __init__(self, start: Point, end: Point,master:str="None"):
        self.start = start
        self.end = end
        self.x_dir = 1
        self.y_dir = 1
        self.master = master
        if end.x < start.x:
            self.x_dir = -1
        if end.y < start.y:
            self.y_dir = -1
        self.angle,self.k = get_angle(start,end)
        self.normal = Point()
        get_straigth_angle(self.start,self.end,self.normal)



    def __str__(self):
        result = ""
        result += "Start = (" + str(self.start.x) + ";" + str(self.start.y) + ")"
        result += "End = (" + str(self.end.x) + ";" + str(self.end.y) + ")"
        return result

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
        return [angle,math.atan(angle)]
    elif (abs(start_y - end_y) < delimeter):
        if (start_x > end_x):
            angle = 180
        else:
            angle = 0
        return [angle,math.atan(angle)]
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
    return [angle,k]
