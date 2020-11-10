import bpy
from mathutils import Vector, Euler
from bpy.props import StringProperty, FloatProperty, EnumProperty, BoolProperty
import os
import math

class OBJECT_OT_cursor_save(bpy.types.Operator):
    """Save 3d Cursor Position relative to the part (relative to the part)"""
    bl_idname       = "view3d.cursor_save"
    bl_label        = "Save 3d Cursor Position"
    bl_options      = {'REGISTER'}
    
    def execute(self, context):
        ob = context.active_object
        delta =  bpy.context.scene.cursor.location - ob.location
        ob['ct_delta'] = delta
        return {'FINISHED'}

class OBJECT_OT_cursor_load(bpy.types.Operator):
    """Move the 3d Cursor to the saved cursor position (relative to the part)"""
    bl_idname       = "view3d.ct_load"
    bl_label        = "Load 3d Cursor Position"
    bl_options      = {'REGISTER'}

    def execute(self, context):
        ob = context.active_object
        if ob['ct_delta']:
            rel = ob.location + Vector(ob['ct_delta'])
            bpy.context.scene.cursor.location = rel
        return {'FINISHED'}

class OBJECT_OT_cursor_top(bpy.types.Operator):
    """Move the 3d Cursor to the saved cursor position and move it to Zmax(relative to the part)"""
    bl_idname       = "view3d.ct_top"
    bl_label        = "Load 3c Cursor move to Zmax"
    bl_options      = {'REGISTER'}

    def execute(self, context):
        ob = context.active_object
        if ob['ct_delta']:
            rel = ob.location + Vector((ob['ct_delta'][0], ob['ct_delta'][1], ob.dimensions.z/2 ))
            bpy.context.scene.cursor.location = rel
        return {'FINISHED'}

class OBJECT_OT_cursor_bottom(bpy.types.Operator):
    """Move the 3d Cursor to the saved cursor position and move it to Zmin(relative to the part)"""
    bl_idname       = "view3d.ct_bottom"
    bl_label        = "Load 3c Cursor move to Zmin"
    bl_options      = {'REGISTER'}

    def execute(self, context):
        ob = context.active_object
        if ob['ct_delta']:
            rel = ob.location + Vector((ob['ct_delta'][0], ob['ct_delta'][1], ob.dimensions.z/-2 ))
            bpy.context.scene.cursor.location = rel
        return {'FINISHED'}

class OBJECT_OT_enclose_selected(bpy.types.Operator):
    """Enclose all selected parts with a Box"""
    bl_idname       = "view3d.enclose_selected"
    bl_label        = "Enclose all selected objects with a box"
    bl_options      = {'REGISTER', 'UNDO'}
    name: StringProperty(
        name="Name for the enclosing box",
        default="Enclosing"
    )
    margin: FloatProperty(
        name="margin around the enclosing box",
        default=0
    )

    def execute(self, context):
        enclose(context.selected_objects, self.name, self.margin)
        return {'FINISHED'}

class OBJECT_OT_cursor_center_children(bpy.types.Operator):
    """Center children relative to the parent object"""
    bl_idname       = "view3d.center_children"
    bl_label        = "Center children to parent position"
    bl_options      = {'REGISTER'}
    def execute(self, context):
        parent = context.active_object
        center_relative(parent.children, parent)
        return {'FINISHED'}

class OBJECT_OT_setup_render(bpy.types.Operator):
    """Setup Render using presets"""
    bl_idname       = "scene.setup_render"
    bl_label        = "Setup Render using presets"
    bl_options      = {'REGISTER', 'UNDO'}
    preset: EnumProperty(
        name="Render Setting",
        default="REALISTIC_EEVEE",
        items=(
            ("REALISTIC_EEVEE", "Realistic Eevee", "Realistic Render settings using Eevee Renderer"),
            ("REALISTIC_CYCLES", "Realistic Cycles", "Realistic Render settings using Cycles Renderer"),
            ("INSTRUCTIONS_EEVEE", "Instructions Eevee", "Instructions Render settings using Eevee Renderer"),
        )
    )
    environment: EnumProperty(
        name="Environment Texture",
        default="sunflowers_1k.hdr",
        items=(
            ("sunflowers_1k.hdr", "Sunflower", "Sunflower 1k from HDRI-Haven"),
        )
    )

    setupCam: BoolProperty(
        name="Setup a camera",
        default=True
    )
    setupLighting: BoolProperty(
        name="Setup a Lighting",
        default=True
    )

    angleH: FloatProperty(
        name="Horizontal camera angle (Z)",
        default=45
    )
    angleV: FloatProperty(
        name="Vertical camera angle (X)",
        default=-15
    )
    def execute(self, context):
        context.scene.render.film_transparent = True

        if self.preset == "REALISTIC_EEVEE":
            context.scene.render.engine = 'BLENDER_EEVEE'
            context.scene.render.use_freestyle = False
        elif self.preset == "REALISTIC_CYCLES":
            context.scene.render.engine = 'BLENDER_EEVEE'
            context.scene.render.use_freestyle = False
        elif self.preset == "INSTRUCTIONS_EEVEE":
            bpy.context.scene.render.engine = 'BLENDER_EEVEE'
            context.scene.render.use_freestyle = True
        
        if self.setupLighting:
            setupHDRI(self.environment)
        
        if self.setupCam:
            cam = add_cam()
            context.scene.camera = cam
            position_cam(cam, self.angleH, self.angleV)
        return {'FINISHED'}  

class OBJECT_OT_position_render_camera(bpy.types.Operator):
    """Setup a rendering camera"""
    bl_idname       = "scene.position_render_camera"
    bl_label        = "Set up camera"
    bl_options      = {'REGISTER', 'UNDO'}
    angleH: FloatProperty(
        name="Horizontal camera angle (Z)",
        default=45
    )
    angleV: FloatProperty(
        name="Vertical camera angle (X)",
        default=-15
    )
    def execute(self, context):
        cam = add_cam()
        context.scene.camera = cam
        position_cam(cam, self.angleH, self.angleV)
        return {'FINISHED'}  

def setupHDRI(name):
    path = os.path.join(os.path.dirname(__file__), "..", "images", "hdri", name)
    world = bpy.context.scene.world
    world.use_nodes = True
    if not world.node_tree.nodes.get("ShaderNodeTexEnvironment"):
        enode = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        enode.image = bpy.data.images.load(path)
        node_tree = world.node_tree
        node_tree.links.new(enode.outputs['Color'], node_tree.nodes['Background'].inputs['Color'])

def position_cam(cam, angleH=45, angleV=-15):
    cam.rotation_euler = Euler((math.radians(90 + angleV), math.radians(0), math.radians(angleH)))
    bpy.ops.view3d.camera_to_view_selected()


def add_cam(name="RenderCam"):
    if bpy.context.collection.objects.find(name) < 0:
        cam = bpy.data.cameras.new(name)
        cam_obj1 = bpy.data.objects.new(name, cam)
        bpy.context.collection.objects.link(cam_obj1)
        return cam_obj1
    else:
        return bpy.context.collection.objects.get(name)

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

def enclose(objects, name="enclosing", margin=0):
    if objects:
        loc = get_center(objects)
        dim = get_dimensions(objects)
        dim = dim + Vector((margin, margin, margin/2))
        bpy.ops.mesh.primitive_cube_add(location=loc, scale=dim)
        enclosing = bpy.context.active_object
        base = Vector((loc.x, loc.y, loc.z - dim.z/2))
        bpy.context.scene.cursor.location = base
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        enclosing.hide_render = True
        enclosing.display_type = 'WIRE'
        enclosing.show_name = True
        enclosing.name = name
        return enclosing

def center_relative(objects, relative_to_vector):
    if objects:
        center = get_bottom_center(objects)
        delta  = center - relative_to_vector
        for obj in objects:
            obj.location = obj.location - delta
