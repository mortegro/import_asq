import bpy
import math
from mathutils import Vector

def get_label(label, location=(0,0,0), rotation=(0,0,0), scale=(1, 1, 1)):
    bpy.data.curves.new(type="FONT",name="Font Curve").body = label
    font_obj = bpy.data.objects.new("Font Object", bpy.data.curves["Font Curve"])
    font_obj.data.align_x = "CENTER"
    font_obj.data.align_y = "CENTER"
    font_obj.location = location
    font_obj.rotation_euler = rotation
    bpy.context.scene.collection.objects.link(font_obj)
    return font_obj

def get_axis_vector(scalar, plane="XY"):
    if plane == "XY":
        return Vector((scalar, scalar, 1))
    elif plane == "XZ":
        return Vector((scalar, 1, scalar))
    elif plane == "YZ":
        return Vector((1, scalar, scalar))
    else:
        return Vector((1, 1, 1))

def get_scale_factor(o1, o2, *plane, portion=0.8):
    (dx1, dy1, dz1) = o1.dimensions
    (dx2, dy2, dz2) = o2.dimensions
    res = 1 / max(dx1/dx2, dy1/dy2, dz1/dz2) * portion
    if not plane:
        return res
    else:
        return get_axis_vector(res,plane)

def get_label_location(obj, plane="XY", dist=0.01, direction=1):
    axis_vec = get_axis_vector(0, plane) * direction
    half_dim = axis_vec * obj.dimensions * 0.5
    loc = obj.location + half_dim # + axis_vec*dist
    return loc


# def addLabels(ob, label, distance=0.01):
#     (px, py, pz) = ob.location
#     (dx, dy, dz) = ob.dimensions
#     (rx, ry, rz) = ob.rotation_euler
#     top = addLabel(label, (px, py, pz+dz/2 + distance), (rx, ry, rz))
#     print (top.dimensions)
#     print (calcScale(top.dimensions , ob.dimensions))
#     top.dimensions =  top.dimensions * calcScale(top.dimensions , ob.dimensions)
#     top.name = 'FrontLabel'
    
#     bottom = addLabel(label, (px, py, pz-dz/2 - distance), (rx, ry +math.pi , rz))
#     bottom.dimensions =  bottom.dimensions * calcScale(bottom.dimensions , ob.dimensions)
#     bottom.name = 'BottomLabel'

#     back = addLabel(label, (px, py+dy/2+distance, pz),  (rx-math.pi/2, ry  , rz))
#     back.dimensions =  back.dimensions * calcScale(back.dimensions , ob.dimensions)
#     back.name = 'BackLabel'

#     front = addLabel(label, (px, py-dy/2-distance, pz), (rx+math.pi/2 , ry , rz))
#     front.dimensions =  front.dimensions * calcScale(front.dimensions , ob.dimensions)
#     front.name = 'FrontLabel'

#     right = addLabel(label, (px+dx/2+distance, py, pz), (rx, ry +math.pi/2 , rz))
#     right.dimensions =  right.dimensions * calcScale(right.dimensions , ob.dimensions)
#     right.name = 'RightLabel'

#     left = addLabel(label, (px-dy/2-distance, py, pz), (rx, ry +math.pi/-2 , rz))
#     left.dimensions =  left.dimensions * calcScale(left.dimensions , ob.dimensions)
#     left.name = 'LeftLabel'


def addLabel(obj):
    text = obj['ankerdata']['nr']
    label = get_label(text)
    label.location = get_label_location(obj)
    factor = get_scale_factor(label, obj)
    label.dimensions = label.dimensions * factor
    return label


for o in bpy.context.selected_objects:
    addLabel(o)
