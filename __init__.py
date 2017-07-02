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
        skel = active_armature(context)
        if skel == None:
            return {'CANCELLED'}

        hip = skel.pose.bones['pelvis']
        root = skel.pose.bones['root']
        if hip == None or root == None:
            return {'CANCELLED'}

        act = skel.animation_data.action
        if act == None:
            return {'CANCELLED'}

        context.scene.objects.active = skel
        bpy.ops.object.mode_set(mode='POSE')
        context.scene.frame_set(act.frame_range.x)

        prev_mat = world_mat(skel, hip)

        for f in range(round(act.frame_range.x) + 1, round(act.frame_range.y) + 1):
            context.scene.frame_set(f)
            hmat = world_mat(skel, hip)
            rmat = world_mat(skel, root)

            if prev_mat.translation != hmat.translation:
                print("moved")

            if prev_mat.to_euler() != hmat.to_euler():
                diff = hmat.to_euler().z - prev_mat.to_euler().z
                print(diff)
                rmat3 = rmat.to_3x3()
                rmat3.rotate(mathutils.Euler((0, 0, diff)))

                root.matrix = pose_mat(skel, root, rmat3.to_4x4())
                context.scene.update()
                hip.matrix = pose_mat(skel, hip, hmat)

                root.keyframe_insert(data_path="rotation_quaternion")
                hip.keyframe_insert(data_path="rotation_quaternion")

            prev_mat = hmat

        return {'FINISHED'}


def active_armature(context):
    for o in context.selected_objects:
        if o.type == 'ARMATURE':
            return o


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
