# -*- coding: utf-8 -*-
"""Import LDraw GPLv2 license.

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

This file defines the importer for Blender.
It stores and recalls preferences for the importer.
The execute() function kicks off the import process.
The python module loadasq does the actual work.
"""

import configparser
import os
import bpy
from bpy.props import (StringProperty,
                       EnumProperty,
                       BoolProperty,
                       FloatProperty
                       )
from bpy_extras.io_utils import ImportHelper
from .loadasq import loadasq

"""
Example preferences file:

[DEFAULT]

[importasq]
asqDirectory     = ""
gaps               = True
createInstances    = True
stoneLib           = "realistic"
materialLib        = "realistic"
(etc)
"""


class Preferences():
    """Import ASQ - Preferences"""
    __sectionName   = 'importasq'

    def __init__(self):
        self.__ldPath        = None
        self.__prefsPath     = os.path.dirname(__file__)
        self.__prefsFilepath = os.path.join(self.__prefsPath, "ImportAsqPreferences.ini")
        self.__config        = configparser.RawConfigParser()
        self.__prefsRead     = self.__config.read(self.__prefsFilepath)
        if self.__prefsRead and not self.__config[Preferences.__sectionName]:
            self.__prefsRead = False

    def get(self, option, default):
        if not self.__prefsRead:
            return default
        if type(default) is bool:
            return self.__config.getboolean(Preferences.__sectionName, option, fallback=default)
        elif type(default) is float:
            return self.__config.getfloat(Preferences.__sectionName, option, fallback=default)
        elif type(default) is int:
            return self.__config.getint(Preferences.__sectionName, option, fallback=default)
        else:
            return self.__config.get(Preferences.__sectionName, option, fallback=default)

    def set(self, option, value):
        if not (Preferences.__sectionName in self.__config):
            self.__config[Preferences.__sectionName] = {}
        self.__config[Preferences.__sectionName][option] = str(value)

    def save(self):
        try:
            with open(self.__prefsFilepath, 'w') as configfile:
                self.__config.write(configfile)
            return True
        except Exception:
            # Fail gracefully
            e = sys.exc_info()[0]
            debugPrint("WARNING: Could not save preferences. {0}".format(e))
            return False

class ImportAsqOps(bpy.types.Operator, ImportHelper):
    """Import ASQ - Import Operator."""
    bl_idname       = "import_scene.importasq"
    bl_description  = "Import AnkerPlan2 ASQ models (.asq)"
    bl_label        = "Import ASQ Models"
    bl_space_type   = "PROPERTIES"
    bl_region_type  = "WINDOW"
    bl_options      = {'REGISTER', 'UNDO', 'PRESET'}
    # Instance the preferences system
    prefs = Preferences()
    # File type filter in file browser
    filename_ext = ".asq"
    filter_glob: StringProperty(
        default="*.asq",
        options={'HIDDEN'}
    )

    stoneLib: EnumProperty(
        name="Stones",
        description="Used stone library i.e. for Realism or Schematic look",
        default=prefs.get("stoneLib", "realistic"),
        items=(
            ("realistic", "Realistic Stones", "Anker Stones with realistic look."),
            ("instruction", "Instructions Stones", "Anker Stones for Instructions (without bevel and carvings)."),
        )
    )

    materialLib: EnumProperty(
        name="Material",
        description="Material to use,  i.e. for Realism or Schematic look",
        default=prefs.get("materialLib", "realistic"),
        items=(
            ("noise", "Noise ", "Render with noisy generated texture."),
            ("instruction", "Instruction", "Render to look like the instruction book pictures."),
            ("realistic", "Realistic", "Render to look realistic."),
            ("texture", "Texture ", "Render to look realistic with image texture."),
        )
    )

    magnification: EnumProperty(
        name="Magnification",
        description="Scale to magnify the stones",
        default=prefs.get("magnification", "50"),
        items=(
            ("1", "1:1", "Original stone size"),
            ("50", "50:1 ", "magnify by factor 50"),
        )
    )

    addGaps: BoolProperty(
        name="Add space between each part:",
        description="Add a small space between each part",
        default=prefs.get("addGaps", False)
    )


    clearScene: BoolProperty(
        name="Clear Scene:",
        description="Clear Scene before import",
        default=prefs.get("clearScene", False)
    )

    setupCam: BoolProperty(
        name="Setup a camera",
        default=prefs.get("setupCam", False)
    )

    cameraMargin: FloatProperty(
        name="Margin for Camera auto zoom",
        default=prefs.get("cameraMargin", 0.04)
    )

    angleH: FloatProperty(
        name="Horizontal camera angle (Z)",
        default=prefs.get("angleH", 45.0)
    )
    angleV: FloatProperty(
        name="Vertical camera angle (X)",
        default=prefs.get("angleV", -15.0)
    )

    setupRendering: BoolProperty(
        name="Setup scene for Rendering",
        default=prefs.get("setupRendering", True)
    )

    preset: EnumProperty(
        name="Render Setting",
        default=prefs.get("preset", "REALISTIC_EEVEE"),
        items=(
            ("REALISTIC_EEVEE", "Realistic Eevee", "Realistic Render settings using Eevee Renderer"),
            ("REALISTIC_CYCLES", "Realistic Cycles", "Realistic Render settings using Cycles Renderer"),
            ("INSTRUCTIONS_EEVEE", "Instructions Eevee", "Instructions Render settings using Eevee Renderer"),
        )
    )

    setupLighting: BoolProperty(
        name="Setup a Lighting",
        default=prefs.get("setupLighting", True)
    )

    environment: EnumProperty(
        name="Environment Texture",
        default=prefs.get("environment", "sunflowers_1k.hdr"),
        items=(
            ("sunflowers_1k.hdr", "Sunflower", "Sunflower 1k from HDRI-Haven"),
            ("abandoned_parking_1k.hdr", "Parking Lot", "Parking Lot 1k from HDRI-Haven"),
            ("small_cathedral_02_1k.hdr", "Cathedral", "Cathedral 1k from HDRI-Haven"),
        )
    )

    link: BoolProperty(
        name="Link",
        description="Link Objects to library",
        default=prefs.get("link", True)
    )

    def draw(self, context):
        """Display import options."""
        layout = self.layout
        layout.use_property_split = True # Active single-column layout
        box = layout.box()
        box.label(text="Import Options", icon='PREFERENCES')
        box.prop(self, "stoneLib", expand=True)
        box.prop(self, "materialLib", expand=True)
        box.prop(self, "magnification", expand=True)
        box.prop(self, "setupCam", expand=True)
        box.prop(self, "cameraMargin", expand=True)
        box.prop(self, "angleH", expand=True)
        box.prop(self, "angleV", expand=True)
        box.prop(self, "setupRendering", expand=True)
        box.prop(self, "preset", expand=True)
        box.prop(self, "setupLighting", expand=True)
        box.prop(self, "environment", expand=False)
        box.prop(self, "clearScene")
        #box.prop(self, "addGaps")
        #box.prop(self, "link")

    def execute(self, context):
        """Start the import process."""
        # Read current preferences from the UI and save them
        ImportAsqOps.prefs.set("stoneLib",      self.stoneLib)
        ImportAsqOps.prefs.set("materialLib",   self.materialLib)
        ImportAsqOps.prefs.set("magnification", self.magnification)
        ImportAsqOps.prefs.set("setupCam",      self.setupCam)
        ImportAsqOps.prefs.set("cameraMargin",  self.cameraMargin)
        ImportAsqOps.prefs.set("angleH",        self.angleH)
        ImportAsqOps.prefs.set("angleV",        self.angleV)
        ImportAsqOps.prefs.set("setupRendering",self.setupRendering)
        ImportAsqOps.prefs.set("preset",        self.preset)
        ImportAsqOps.prefs.set("setupLighting", self.setupLighting)
        ImportAsqOps.prefs.set("environment",   self.environment)
        ImportAsqOps.prefs.set("clearScene",    self.clearScene)
        #ImportAsqOps.prefs.set("addGaps",       self.addGaps)
        #ImportAsqOps.prefs.set("link",          self.link)
        ImportAsqOps.prefs.save()

        # Set import options and import
        loadasq.Options.stoneLib                = self.stoneLib
        loadasq.Options.materialLib             = self.materialLib
        loadasq.Options.magnification           = self.magnification
        loadasq.Options.setupCam                = self.setupCam
        loadasq.Options.cameraMargin            = self.cameraMargin
        loadasq.Options.angleH                  = self.angleH
        loadasq.Options.angleV                  = self.angleV
        loadasq.Options.setupRendering          = self.setupRendering
        loadasq.Options.preset                  = self.preset
        loadasq.Options.setupLighting           = self.setupLighting
        loadasq.Options.environment             = self.environment
        loadasq.Options.clearScene              = self.clearScene
        #loadasq.Options.addGaps                 = self.addGaps
        #loadasq.Options.link                    = self.link
        loadasq.loadFromFile(self, self.filepath)
        return {'FINISHED'}
