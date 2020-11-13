# -*- coding: utf-8 -*-
"""Load LDraw GPLv2 license.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""

"""
Import ASQ

This module loads AnkerPlan2 Asq compatible files into Blender. Set the 
Options first, then call loadFromFile() function with the full 
filepath of a file to load.

Accepts .asq files.

Highly inspired by Toby Nelsons ImportLdraw project.
"""

import os
import sys
import math
import traceback
import glob
import datetime
import struct
import re
import copy
import platform
import itertools
import operator
from pprint import pprint
import sqlite3
import bpy
from mathutils import Matrix,Euler,Vector,Quaternion
import bmesh
from ..operators.utils import enclose, center_relative, setupRendering, setupHDRI, position_cam, add_cam

global linkedTemplateBricks
linkedTemplateBricks=[]

# **************************************************************************************
# **************************************************************************************
class Options:
    """User Options"""
    stoneLib           = "realistic"    # "realistic", "instructions" Stones to use.
    materialLib        = "realistic"    # "realistic", "texture", "instructions" Material to use.
    addGaps            = False           # Introduces a tiny space between each brick
    gapAmount          = 0.1            # Percent
    clearScene         = False
    center             = True
    link               = False
    setupCam           = False
    angleH             = 45 
    angleV             =-15
    setupRendering     = True
    preset             = "REALISTIC_EEVEE"
    setupLighting      = True
    environment        = "sunflowers_1k.hdr"
    cameraMargin       = 2
    magnification      = 50
    scriptDirectory    = os.path.dirname( os.path.realpath(__file__) )
    verbose            = 1              # 1 = Show messages while working, 0 = Only show warnings/errors
    nks                = 6

# **************************************************************************************
def linkToScene(ob):
    if bpy.context.collection.objects.find(ob.name) < 0:
        bpy.context.collection.objects.link(ob)

# **************************************************************************************
def setParent(objects, parent):
    for o in objects:
        o.parent = parent
        
# **************************************************************************************
def internalPrint(message):
    """Debug print with identification timestamp."""
    # Current timestamp (with milliseconds trimmed to two places)
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-4]
    message = "{0} [importasq] {1}".format(timestamp, message)
    print("{0}".format(message))

# **************************************************************************************
def debugPrint(message):
    """Debug print with identification timestamp."""
    if Options.verbose > 0:
        internalPrint(message) 

# **************************************************************************************
def printError(message):
    internalPrint("ERROR: {0}".format(message))

# **************************************************************************************
def clearScene():
    # Clear Scene
    bpy.ops.object.select_all(action="SELECT") 
    bpy.ops.object.delete(use_global=False, confirm=False)

# **************************************************************************************
def linkLibrary():
    global linkedTemplateBricks
    if not bpy.data.scenes.get("library"):
        debugPrint("Linking Stones from Library")
        filepath = os.path.join(Options.scriptDirectory, "..", "lib", "anker_library.blend" )
        if not os.path.isfile(filepath):
            debugPrint("Library file not found: "+filepath)
            return
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.scenes = ["library"]
            data_to.materials = data_from.materials
        debugPrint("Linked {0} bricks from library".format(len(bpy.data.scenes['library'].objects)))
    else:
        debugPrint("Library already linked")
    linkedTemplateBricks = bpy.data.scenes['library'].objects
    return linkedTemplateBricks

# **************************************************************************************
def hotStonesReplace(stone):
    appendF = ["GKNF101", "GKNF101","GKNF102","GKNF112","GKNF113","GKNF114","GKNF115","GKNF124","GKNF126",]
    if stone['shapeId'] in appendF:
        stone['shapeId'] = "{}F".format(stone['shapeId'])
    return stone

# **************************************************************************************
def loadBricksFromAsq(file):
    searchSQL = """SELECT BuildingShapePlacement.ShapeId, BuildingShapePlacement.PositionX, BuildingShapePlacement.PositionY, BuildingShapePlacement.PositionZ, BuildingShapePlacement.RotationW,BuildingShapePlacement.RotationX,BuildingShapePlacement.RotationY,BuildingShapePlacement.RotationZ, Material.KeyCode, IFNULL(LayerShapePlacement.LayerId, 0)
    FROM BuildingShapePlacement
    LEFT JOIN LayerShapePlacement on BuildingShapePlacement.BuildingShapePlacementId=LayerShapePlacement.BuildingShapePlacementId
	LEFT JOIN Material on BuildingShapePlacement.MaterialId = Material.MaterialId
    WHERE BuildingShapePlacement.BuildingId=1
    """
    keys = ["shapeId","x","y","z","rw","rx","ry","rz","material","layer"]
    debugPrint("Loading file " + str(file))
    with sqlite3.connect(file) as conn:
        cur = conn.cursor()
        cur.execute(searchSQL)
        stones = cur.fetchall()
    debugPrint("Found {0} stones in {1}".format(len(stones), file))
    asqStones = map(lambda stone: dict(zip(keys, stone)), stones)
    return asqStones

# **************************************************************************************
def asqToBlenderCoordinates(asqStone):
    # Converts coordinates from asq to blender
    if asqStone:
        quaternion = Quaternion( (asqStone['rw'], asqStone['rx'], asqStone['ry'], asqStone['rz']) )
        r_transform = Euler((math.radians(90),0,0))
        quaternion.rotate(r_transform)
        euler = quaternion.to_euler()
        blenderStone = {
            'shapeId': asqStone['shapeId'],
            'x': round(asqStone['x']/1000, Options.nks), 
            'y': round(asqStone['z']/-1000, Options.nks), 
            'z': round(asqStone['y']/1000, Options.nks),
            'rx': euler.x,
            'ry': euler.y,
            'rz': euler.z,
            'material': asqStone['material'],
            'layer': asqStone['layer']
        }
        return blenderStone
    else:
        return {}

# **************************************************************************************
def asqToBlender(asqStones):
    # Converts an list of stones from asq to blender coordinates
    blenderStones = map(asqToBlenderCoordinates, asqStones)
    return blenderStones

# **************************************************************************************
def assignBrickMaterial(blenderObject, keyCode, materialLib = "realistic"):
    mat = bpy.data.materials.get("Anker_{0}_{1}".format(keyCode, materialLib))
    if mat is None:
        debugPrint("Material with number {0} not found in {1} library.".format(keyCode, materialLib))
    else:
        blenderObject.data.materials.append(None)
        blenderObject.material_slots[0].link = 'OBJECT'
        blenderObject.material_slots[0].material = mat
    return

def apply_rotation(ob):
    ob.data.transform(ob.matrix_world)
    ob.matrix_world = Matrix()

# **************************************************************************************
def createBrickObjects(blenderBricklist):
    global linkedTemplateBricks
    buildingBricks = []
    fac = Options.magnification

    for s in blenderBricklist:
        templateName = "{0}_{1}".format(s['shapeId'], Options.stoneLib)
        if templateName in linkedTemplateBricks:
            template_ob = linkedTemplateBricks[templateName]
            ob = template_ob.copy()
            if not Options.link:
                ob.data = ob.data.copy()
            ob["ankerdata"] = template_ob["ankerdata"]
            ob["layer"] = s['layer']
            # Set rotation
            rotation = (s['rx'], s['ry'], s['rz'])
            ob.rotation_euler = rotation
            # Set location and scale
            location = (s['x']*fac, s['y']*fac, s['z']*fac)
            ob.location = location
            # Set scale because library is 50x bigger
            scale = (fac/50,fac/50,fac/50)
            ob.scale = scale
            # Store InstanceData
            ob["instancedata"] = {
                "rotation": rotation,
                "location": location,
                "scale": scale
            }
            # Assign material
            assignBrickMaterial(ob, s['material'], Options.materialLib)
            linkToScene(ob)
            buildingBricks.append(ob)
        else:
            debugPrint("Stone {0} not found in loaded library.".format(str(templateName)))
    return buildingBricks

# **************************************************************************************
def deselectAll():
    bpy.ops.object.select_all(action='DESELECT')

# **************************************************************************************
def selectAll(objects):
    deselectAll()
    for ob in objects:
        ob.select_set(True)

# **************************************************************************************
def applyScaleAndRotation(objects):
    selectAll(objects)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    deselectAll()

# **************************************************************************************
def buildBuilding(name, blenderBricks):
    # Load Library
    linkLibrary()

    # Switch to Object mode and deselect all
    if bpy.ops.object.mode_set.poll():
       bpy.ops.object.mode_set(mode='OBJECT')

    # Clear Scene or deselect
    if Options.clearScene:
        clearScene()
    else:
        bpy.ops.object.select_all(action='DESELECT')


    # Replace stones
    blenderBricks = map(hotStonesReplace, blenderBricks)

    # Create Building
    buildingBricks = createBrickObjects(blenderBricks )
    applyScaleAndRotation(buildingBricks)

    # Center
    if Options.center:
        center_relative(buildingBricks, bpy.context.scene.cursor.location)

    # Create Parent
    parent = enclose(buildingBricks, margin=Options.cameraMargin*Options.magnification)
    parent.name = name
    linkToScene(parent)
    setParent(buildingBricks, parent)

    # Setup File Units
    if Options.magnification < 10:
        bpy.context.scene.unit_settings.length_unit = 'CENTIMETERS'
    else:
        bpy.context.scene.unit_settings.length_unit = 'METERS'

    # Setup Rendering
        setupRendering(Options.preset)
        
    if Options.setupLighting:
        setupHDRI(Options.environment)
        
    # Setup Camera
    if Options.setupCam:
        cam = add_cam()
        bpy.context.scene.camera = cam
        position_cam(cam, Options.angleH, Options.angleV)

    # Apply rotations
    #if not Options.link:
    #    for ob in parent.children:
    #        apply_rotation(ob)

    return parent

# **************************************************************************************
def loadFromFile(context, filename, isFullFilepath=True):
    file = os.path.expanduser(filename)
    if os.path.isfile(file):
        filename = os.path.basename(file)
        name = os.path.splitext(filename)[0] or 'Building'
        asqBricks = loadBricksFromAsq(file)
        blenderBricks = asqToBlender(asqBricks)
        rootOb = buildBuilding(name, blenderBricks)
        debugPrint("Load Done")
        return rootOb
    else:
        debugPrint("File not found.")
