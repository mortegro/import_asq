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

import bpy

from . import importasq
from .operators import utils

bl_info = {
    "name": "Import ASQ File",
    "description": "Import AnkerPlan2 models in .asq format",
    "author": "Matthias Bolz <mortegro@gmx.de>",
    "version": (0, 0, 1),
    "blender": (2, 90, 0),
    "location": "File > Import",
    "warning": "",
    "wiki_url": "https://github.com/mortegro/BlenderImportAsq",
    "tracker_url": "https://github.com/mortegro/BlenderImportAsq/issues",
    "category": "Import-Export"
    }

def menuImport(self, context):
    """Import menu listing label."""
    self.layout.operator(importasq.ImportAsqOps.bl_idname,
                         text="Ankerplan2 ASQ (.asq)")


def register():
    """Register Menu Listing."""
    bpy.utils.register_class(importasq.ImportAsqOps)
    bpy.utils.register_class(utils.OBJECT_OT_cursor_save)
    bpy.utils.register_class(utils.OBJECT_OT_cursor_load)
    bpy.utils.register_class(utils.OBJECT_OT_cursor_top)
    bpy.utils.register_class(utils.OBJECT_OT_cursor_bottom)
    bpy.utils.register_class(utils.OBJECT_OT_enclose_selected)
    bpy.utils.register_class(utils.OBJECT_OT_cursor_center_children)
    bpy.utils.register_class(utils.OBJECT_OT_setup_render)
    bpy.utils.register_class(utils.OBJECT_OT_position_render_camera)
    bpy.types.TOPBAR_MT_file_import.append(menuImport)

def unregister():
    """Unregister Menu Listing."""
    bpy.utils.unregister_class(importasq.ImportAsqOps)
    bpy.utils.unregister_class(utils.OBJECT_OT_cursor_save)
    bpy.utils.unregister_class(utils.OBJECT_OT_cursor_load)
    bpy.utils.unregister_class(utils.OBJECT_OT_cursor_top)
    bpy.utils.unregister_class(utils.OBJECT_OT_cursor_bottom)
    bpy.utils.unregister_class(utils.OBJECT_OT_enclose_selected)
    bpy.utils.unregister_class(utils.OBJECT_OT_cursor_center_children)
    bpy.utils.unregister_class(utils.OBJECT_OT_setup_render)
    bpy.utils.unregister_class(utils.OBJECT_OT_position_render_camera)

    bpy.types.TOPBAR_MT_file_import.remove(menuImport)

if __name__ == "__main__":
    register()
