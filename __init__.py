bl_info = {
    "name": "Root Motionist",
    "author": "POET Industries",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "category": "Animation"
}

import inspect
import time

import bpy
import mathutils


class RootMotionData(bpy.types.PropertyGroup):
    hip = bpy.props.StringProperty(name="Hip Bone")
    root = bpy.props.StringProperty(name="Root Bone")
    copy = bpy.props.StringProperty(name="Debug Character")


class CreateRootMotion(bpy.types.Operator):
    """Transfer hip bone motion to root bone"""
    bl_idname = "anim.create_rm"
    bl_label = "Create Root Motion"
    bl_options = {'REGISTER', 'UNDO'}

    root = "root"
    hip = "pelvis"
    skel = None

    @classmethod
    def poll(cls, context):
        return active_armature(context) is not None

    def execute(self, context):
        ref = self.debug_character(context)
        context.scene.rm_data.copy = ref.name

        expr = "\"%s\"" % self.hip
        curves = self.skel.animation_data.action.fcurves
        for c in curves:
            if expr in c.data_path:
                curves.remove(c)

        hip = self.skel.pose.bones[self.hip]
        ref_hip = ref.pose.bones[self.hip]
        frames = self.skel.animation_data.action.frame_range
        for f in range(round(frames.x), round(frames.y) + 1):
            context.scene.frame_set(f)
            ref_mtx = world_mtx(ref, ref_hip)

            hip.matrix = pose_mtx(self.skel, hip, ref_mtx)
            hip.keyframe_insert(data_path="rotation_quaternion")
            hip.keyframe_insert(data_path="location")
            hip.keyframe_insert(data_path="location")

        return {'FINISHED'}

    def invoke(self, context, event):
        data = context.scene.rm_data

        self.root = data.root if data.root != "" else self.root
        self.hip = data.hip if data.hip != "" else self.hip
        self.skel = active_armature(context)

        if self.skel == None:
            return {'CANCELLED'}
        elif self.skel.animation_data.action == None:
            return {'CANCELLED'}

        return self.execute(context)

    def debug_character(self, context):
        char = self.skel.copy()
        char.data = self.skel.data.copy()
        char.animation_data.action = self.skel.animation_data.action.copy()
        char.name = "skel" + str(int(time.time()))
        context.scene.objects.link(char)

        if len(self.skel.children) != 0:
            mat = bpy.data.materials.new(name="mat" + str(int(time.time())))
            mat.diffuse_color = (0, 1, 0)

            for c in self.skel.children:
                mesh = c.copy()
                mesh.data = c.data.copy()
                mesh.parent = char
                mesh.modifiers["Armature"].object = char
                mesh.data.materials.append(mat)
                context.scene.objects.link(mesh)

        expr = "\"%s\"" % self.root
        for fc in char.animation_data.action.fcurves:
            if expr in fc.data_path:
                fc.mute = True

        return char


class Cleanup(bpy.types.Operator):
    """Remove temporary reference character and its properties"""
    bl_idname = "anim.cleanup_rm"
    bl_label = "Finalize Root Motion Operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.rm_data.copy != ""

    def execute(self, context):
        char = bpy.data.objects.get(context.scene.rm_data.copy)
        context.scene.rm_data.copy = ""
        if char == None:
            return {'CANCELLED'}

        for c in char.children:
            mat = c.data.materials[0]
            if mat != None:
                bpy.data.materials.remove(mat, True)
            bpy.data.objects.remove(c, True)

        anim = char.animation_data.action
        if anim != None:
            bpy.data.actions.remove(anim, True)

        context.scene.objects.unlink(char)
        bpy.data.objects.remove(char, True)

        return {'FINISHED'}


class MainPanel(bpy.types.Panel):
    bl_label = "Root Motionist"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Animation"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return active_armature(context) is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        col = layout.column(align=True)
        col.prop_search(context.scene.rm_data, "root",
                        obj.pose, "bones", text="Root")
        col.prop_search(context.scene.rm_data, "hip",
                        obj.pose, "bones", text="Hip")
        col.prop(obj.animation_data, "action", text="Anim")

        col = layout.column(align=True)
        col.label(text="Root Motion:")
        row = col.row(align=True)
        create_btn = row.operator("anim.create_rm", text="Create")
        #delete_btn = row.operator("anim.create_rm", text="Remove")
        col.operator("anim.cleanup_rm", text="Delete Ref Character")


def active_armature(context):
    if context.active_object != None:
        if context.active_object.type == 'ARMATURE':
            return context.active_object


def reference_armature(context):
    for obj in context.selected_objects:
        if obj.type == 'ARMATURE' and obj != context.active_object:
            return obj


def world_mtx(armature, bone):
    return armature.convert_space(bone, bone.matrix, from_space='POSE', to_space='WORLD')


def pose_mtx(armature, bone, mat):
    return armature.convert_space(bone, mat, from_space='WORLD', to_space='POSE')


def register():
    bpy.utils.register_class(RootMotionData)
    bpy.utils.register_class(CreateRootMotion)
    bpy.utils.register_class(Cleanup)
    bpy.utils.register_class(MainPanel)

    bpy.types.Scene.rm_data = bpy.props.PointerProperty(type=RootMotionData)


def unregister():
    del bpy.types.Scene.rm_data

    bpy.utils.unregister_class(RootMotionData)
    bpy.utils.unregister_class(CreateRootMotion)
    bpy.utils.unregister_class(Cleanup)
    bpy.utils.unregister_class(MainPanel)


if __name__ == "__main__":
    register()
