#################################################################
# Copyright (c) 2017-2019 Robo Poets
#
# This code is distributed under the MIT License. For a complete
# list of terms see accompanying LICENSE file or the copy at
# https://opensource.org/licenses/MIT
#################################################################

bl_info = {
    "name": "Root Motionist",
    "author": "POET Industries",
    "version": (0, 4, 0),
    "blender": (2, 78, 0),
    "category": "Animation"
}

import bpy, importlib
from . import   (
                root_motion,
                motion_matching,
                )

def register():
    importlib.reload(root_motion)
    root_motion.register()
    importlib.reload(motion_matching)
    motion_matching.register()

def unregister():
    root_motion.unregister()
    motion_matching.unregister()

if __name__ == "__main__":
    register()
