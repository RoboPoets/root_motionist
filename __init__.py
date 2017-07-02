bl_info = {
    "name": "Root Motionist",
    "author": "POET Industries",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "category": "Animation"
}

import bpy
import inspect
import mathutils


class CreateRootMotion(bpy.types.Operator):
    """Extract motion from hip and save into root bone"""
    bl_idname = "anim.create_rm"
    bl_label = "Create Root Motion"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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
            ref_mat = world_mat(ref_skel, ref_hip)

            if ref_mat == world_mat(act_skel, act_hip):
                print("Frame %d: nothing to do" % f)
                continue

            act_hip.matrix = pose_mat(act_skel, act_hip, ref_mat)
            act_hip.keyframe_insert(data_path="rotation_quaternion")
            act_hip.keyframe_insert(data_path="location")

        return {'FINISHED'}


def active_armature(context):
    if context.active_object.type == 'ARMATURE':
        return context.active_object


def reference_armature(context):
    for obj in context.selected_objects:
        if obj.type == 'ARMATURE' and obj != context.active_object:
            return obj


def world_mat(armature, bone):
    return armature.convert_space(bone, bone.matrix, from_space='POSE', to_space='WORLD')


def pose_mat(armature, bone, mat):
    return armature.convert_space(bone, mat, from_space='WORLD', to_space='POSE')


def register():
    bpy.utils.register_class(CreateRootMotion)


def unregister():
    bpy.utils.unregister_class(CreateRootMotion)


if __name__ == "__main__":
    register()
