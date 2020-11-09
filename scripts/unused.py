# **************************************************************************************
def calcObjectBounding(ob):
    coords = []
    for v in ob.data.vertices:
        loc = ob.matrix_world @ v.co
        coords.append(loc)
    xX = [co[0] for co in coords]
    yY = [co[1] for co in coords]
    zZ = [co[2] for co in coords]
    minVector = Vector((min(xX),min(yY),min(zZ)))
    maxVector = Vector((max(xX),max(yY),max(zZ)))
    meanVector = Vector((sum(xX)(len/(xX)),sum(yY)/len(yY),sum(zZ)/len(zZ)))
    return (minVector, meanVector, maxVector)
    ob.location = ob.location - Vector(( ob['meanVector'][0], ob['meanVector'][1], ob['meanVector'][2]))

    # **************************************************************************************
# rotate_object(obj, angle, direction, point)
# UNTESTED
# obj - a Blender object
# angle - angle in radians
# direction - axis to rotate around (a vector from the origin)
# point - point to rotate around (a vector)
def rotate_object(obj, angle, direction, point):
             R = Matrix.Rotation(angle, 4, direction)
             T = Matrix.Translation(point)
             M = T @ R @ T.inverted()
             obj.location = M @ obj.location
             obj.rotation_euler.rotate(M)

# **************************************************************************************
def setupLineset(lineset, thickness, group):
    lineset.select_silhouette = True
    lineset.select_border = False
    lineset.select_contour = False
    lineset.select_suggestive_contour = False
    lineset.select_ridge_valley = False
    lineset.select_crease = False
    lineset.select_edge_mark = True
    lineset.select_external_contour = False
    lineset.select_material_boundary = False
    lineset.edge_type_combination = 'OR'
    lineset.edge_type_negation = 'INCLUSIVE'
    lineset.select_by_collection = True
    lineset.collection = bpy.data.collections[bpy.data.collections.find(group)]
    # Set line color
    lineset.linestyle.color = (0.0, 0.0, 0.0)
    # Set material to override color
    if 'LegoMaterial' not in lineset.linestyle.color_modifiers:
        lineset.linestyle.color_modifiers.new('LegoMaterial', 'MATERIAL')
    # Use square caps
    lineset.linestyle.caps = 'SQUARE'       # Can be 'ROUND', 'BUTT', or 'SQUARE'
    # Draw inside the edge of the object
    lineset.linestyle.thickness_position = 'INSIDE'
    # Set Thickness
    lineset.linestyle.thickness = thickness

# **************************************************************************************
def setupRealisticLook():
    scene = bpy.context.scene
    render = scene.render
    # Use cycles render
    scene.render.engine = 'CYCLES'
    render.use_freestyle = False
    # Change camera back to Perspective
    if scene.camera is not None:
        scene.camera.data.type = 'PERSP'
    # Turn off cycles transparency
    scene.cycles.film_transparent = False
    # Get the render/view layers we are interested in:
    layers = getLayers(scene)
    # Create Compositing Nodes
    scene.use_nodes = True

# **************************************************************************************
def setupInstructionsLook():
    scene = bpy.context.scene
    render = scene.render
    render.use_freestyle = True
    render.engine = 'BLENDER_EEVEE'
    # Change camera to Orthographic
    if scene.camera is not None:
        scene.camera.data.type = 'ORTHO'
    # Turn on cycles transparency
    scene.cycles.film_transparent = True
    # Find or create the render/view layers we are interested in:
    layers = getLayers(scene)
    # Create Compositing Nodes
    scene.use_nodes = True


# **************************************************************************************
def linkToCollection(collectionName, ob):
    # Add object to the appropriate collection
    if bpy.data.collections[collectionName].objects.find(ob.name) < 0:
        bpy.data.collections[collectionName].objects.link(ob)

# **************************************************************************************
def unlinkFromScene(ob):
    if bpy.context.collection.objects.find(ob.name) >= 0:
        bpy.context.collection.objects.unlink(ob)

# **************************************************************************************
def selectObject(ob, onlyThis=False):
    if onlyThis:
        bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(state=True)
    bpy.context.view_layer.objects.active = ob

# **************************************************************************************
def deselectObject(ob):
    ob.select_set(state=False)
    bpy.context.view_layer.objects.active = None
