import bpy
from mathutils import Vector

class anker_ct_save(bpy.types.Operator):
    """Store the cursor position (relative to the part)"""
    bl_idname       = "anker.ct_save"
    bl_label        = "Store relative Cursor"
    bl_options      = {'REGISTER'}
    
    def execute(self, context):
        ob = context.active_object
        delta =  bpy.context.scene.cursor.location - ob.location
        ob['ct_delta'] = delta
        return {'FINISHED'}

class anker_ct_load(bpy.types.Operator):
    """Set the cursor position to the stored (relative to the part)"""
    bl_idname       = "anker.ct_load"
    bl_label        = "Set Cursor postion to stored (relative Cursor)"
    bl_options      = {'REGISTER'}

    def execute(self, context):
        ob = context.active_object
        if ob['ct_delta']:
            rel = ob.location + Vector(ob['ct_delta'])
            bpy.context.scene.cursor.location = rel
        return {'FINISHED'}

class anker_ct_top(bpy.types.Operator):
    """Set the cursor position to the stored XY and Z top"""
    bl_idname       = "anker.ct_top"
    bl_label        = "Set Cursor postion to the stored XY and Z top"
    bl_options      = {'REGISTER'}

    def execute(self, context):
        ob = context.active_object
        if ob['ct_delta']:
            rel = ob.location + Vector((ob['ct_delta'][0], ob['ct_delta'][1], ob.dimensions.z/2 ))
            bpy.context.scene.cursor.location = rel
        return {'FINISHED'}

class anker_ct_bottom(bpy.types.Operator):
    """Set the cursor position to the stored XY and Z bottom"""
    bl_idname       = "anker.ct_bottom"
    bl_label        = "Set Cursor postion to the stored XY and Z bottom"
    bl_options      = {'REGISTER'}

    def execute(self, context):
        ob = context.active_object
        if ob['ct_delta']:
            rel = ob.location + Vector((ob['ct_delta'][0], ob['ct_delta'][1], ob.dimensions.z/-2 ))
            bpy.context.scene.cursor.location = rel
        return {'FINISHED'}

class anker_ct_enclose(bpy.types.Operator):
    """Enclose with Box"""
    bl_idname       = "anker.enclose"
    bl_label        = "construct an enclosing box"
    bl_options      = {'REGISTER'}
    def execute(self, context):
        enclose(context.selected_objects)
        return {'FINISHED'}

class anker_ct_center_children(bpy.types.Operator):
    """Center children"""
    bl_idname       = "anker.center_children"
    bl_label        = "Center children to parent position"
    bl_options      = {'REGISTER'}
    def execute(self, context):
        parent = context.active_object
        center_relative(parent.children, parent)
        return {'FINISHED'}

def column_func(vectors, column=0, func = min):
    els = [el[column] for el in vectors]
    res = func(els)
    return round(res, 6)

def get_bottom_left(objects):
    edges = [o.location - o.dimensions / 2 for o in objects]
    res = Vector(( column_func(edges,0,min), column_func(edges,1,min), column_func(edges,2,min)    ))
    return res

def get_top_right(objects):
    edges = [o.location + o.dimensions / 2 for o in objects]
    res = Vector(( column_func(edges,0,max), column_func(edges,1,max), column_func(edges,2,max)    ))
    return res

def get_bounds(objects):
    min = get_bottom_left(objects)
    max = get_top_right(objects)
    return (min,max)

def get_center(objects):
    (min, max) =get_bounds(objects)
    center = Vector (( (min.x+max.x)/2, (min.y+max.y)/2, (min.z+max.z)/2))
    return center

def get_bottom_center(objects):
    (min, max) =get_bounds(objects)
    center = Vector (( (min.x+max.x)/2, (min.y+max.y)/2, min.z))
    return center

def get_dimensions(objects):
    (min, max) =get_bounds(objects)
    res = max-min
    return res

def enclose(objects):
    if objects:
        loc = get_center(objects)
        dim = get_dimensions(objects)
        bpy.ops.mesh.primitive_cube_add(location=loc, scale=dim)
        enclosing = bpy.context.active_object
        enclosing.hide_render = True
        enclosing.display_type = 'WIRE'
        enclosing.show_name = True
        return enclosing

def center_relative(objects, relative_to_vector):
    if objects:
        center = get_bottom_center(objects)
        delta  = center - relative_to_vector
        for obj in objects:
            obj.location = obj.location - delta
