bl_info = {
    "name": "Root Motionist",
    "author": "POET Industries",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "category": "Animation"
}

import inspect

import bpy
import mathutils


class RootMotionData(bpy.types.PropertyGroup):
    hip = bpy.props.StringProperty(name="Hip Bone")
    root = bpy.props.StringProperty(name="Root Bone")


class CreateRootMotion(bpy.types.Operator):
    """Transfer hip bone motion to root bone"""
    bl_idname = "anim.create_rm"
    bl_label = "Create Root Motion"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return active_armature(context) is not None

    def execute(self, context):
        '''
        act_skel = active_armature(context)
        ref_skel = reference_armature(context)
        if act_skel == None or ref_skel == None:
            return {'CANCELLED'}

        act_hip = act_skel.pose.bones['pelvis']
        ref_hip = ref_skel.pose.bones['pelvis']
        if act_hip == None or ref_hip == None:
            return {'CANCELLED'}

        anim = act_skel.animation_data.action
        ref_anim = ref_skel.animation_data.action
        if anim == None or ref_anim == None:
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='POSE')
        for f in range(round(anim.frame_range.x), round(anim.frame_range.y) + 1):
            context.scene.frame_set(f)
            ref_mtx = world_mtx(ref_skel, ref_hip)

            if ref_mtx == world_mtx(act_skel, act_hip):
                print("Frame %d: nothing to do" % f)
                continue

            act_hip.matrix = pose_mtx(act_skel, act_hip, ref_mtx)
            act_hip.keyframe_insert(data_path="rotation_quaternion")
            act_hip.keyframe_insert(data_path="location")

        return {'FINISHED'}
        '''

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class MainPanel(bpy.types.Panel):
    bl_label = "Root Motionist"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Animation"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE'

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


def active_armature(context):
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
    bpy.utils.register_class(MainPanel)

    bpy.types.Scene.rm_data = bpy.props.PointerProperty(type=RootMotionData)


def unregister():
    del bpy.types.Scene.rm_data

    bpy.utils.unregister_class(RootMotionData)
    bpy.utils.unregister_class(CreateRootMotion)
    bpy.utils.unregister_class(MainPanel)


if __name__ == "__main__":
    register()
