import bpy
import itertools
import math
import json
import tqdm
import numpy as np
from fractions import Fraction
from numbers import Number
from collections import namedtuple


def reset_scene():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for i, obj in enumerate(bpy.data.objects):
        if obj.type == "MESH":
            obj.select_set(True)
        else:
            obj.select_set(False)
    bpy.ops.object.delete()


def draw_polygon(points, x_off, y_off, z_off):
    for x, y in points:
        bpy.context.scene.cursor.location = ((x+1)/2+x_off, (y+1)/2+y_off, z_off)
        bpy.ops.mesh.primitive_vert_add()
    
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.convex_hull()
    bpy.ops.object.mode_set(mode="OBJECT")


def draw_polyhedron(layers, x_off, y_off, z_off):
    for z, layer in layers:
        for x, y in layer:
            bpy.context.scene.cursor.location = ((x+1)/2+x_off, (y+1)/2+y_off, z+z_off)
            bpy.ops.mesh.primitive_vert_add()
    
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.convex_hull()
    bpy.ops.object.mode_set(mode="OBJECT")


reset_scene()

with open("ph.json") as fd:
    polyhedrons = tuple(json.load(fd))

import random

x, y, z = 0, 0, 0
for polyhedron in random.choices(polyhedrons, k=128):
    draw_polyhedron(polyhedron, x, y, z)
    
    y += 2
    if y >= 16:
        y = 0
        x += 2
 
print("done")
