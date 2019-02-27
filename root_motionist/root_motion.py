import time

import bpy
import mathutils

class RootMotionData(bpy.types.PropertyGroup):
    hip = bpy.props.StringProperty(name="Hip Bone")
    root = bpy.props.StringProperty(name="Root Bone")
    copy = bpy.props.StringProperty(name="Debug Character")
    step = bpy.props.IntProperty(name="Step Size", default=3, min=1)


class ANIM_OT_extract_root_motion(bpy.types.Operator):
    """Transfer hip bone motion to root bone"""
    bl_idname = "anim.rm_extract_root_motion"
    bl_label = "Create Root Motion"
    bl_options = {'REGISTER', 'UNDO'}

    skel = None

    @classmethod
    def poll(cls, context):
        return valid_armature(context) is not None

    def modal(self, context, event):
        ref = debug_character(context, self.skel)
        data = context.scene.rm_data
        frames = self.skel.animation_data.action.frame_range

        expr = "\"%s\"" % data.hip
        curves = self.skel.animation_data.action.fcurves
        for c in curves:
            if expr in c.data_path:
                curves.remove(c)

        root = self.skel.pose.bones[data.root]
        ref_hip = ref.pose.bones[data.hip]
        ref_mtx = world_mtx(ref, ref_hip)
        for f in steps(context, frames):
            context.scene.frame_set(f)
            mtx = world_mtx(ref, ref_hip)

            mtx_trans = mathutils.Matrix.Translation(mtx.translation - ref_mtx.translation)
            mtx_trans.translation.z = 0
            mtx_rot = mathutils.Matrix.Rotation(0, 4, 'X')
            mtx_scale = mathutils.Matrix.Scale(mtx.to_scale().x, 4)

            root.matrix = pose_mtx(self.skel, root, mtx_trans * mtx_rot * mtx_scale)
            root.keyframe_insert(data_path="location")
            root.keyframe_insert(data_path="rotation_quaternion")

        hip = self.skel.pose.bones[data.hip]
        for f in range(round(frames.x), round(frames.y) + 1):
            context.scene.frame_set(f)
            hip.matrix = pose_mtx(self.skel, hip, world_mtx(ref, ref_hip))
            hip.keyframe_insert(data_path="rotation_quaternion")
            hip.keyframe_insert(data_path="location")
            hip.keyframe_insert(data_path="scale")

        return {'FINISHED'}

    def invoke(self, context, event):
        self.skel = valid_armature(context)
        context.scene.frame_set(self.skel.animation_data.action.frame_range.x)

        data = context.scene.rm_data
        if data.root == "":
            data.root = self.skel.pose.bones[0].name
        if data.hip == "":
            data.hip = self.skel.pose.bones[1].name

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ANIM_OT_integrate_root_motion(bpy.types.Operator):
    """Transfer root bone motion to hip bone"""
    bl_idname = "anim.rm_integrate_rm"
    bl_label = "Integrate Root Motion"
    bl_options = {'REGISTER', 'UNDO'}

    skel = None

    @classmethod
    def poll(cls, context):
        return valid_armature(context) is not None

    def modal(self, context, event):
        ref = debug_character(context, self.skel)
        data = context.scene.rm_data

        root_expr = "\"%s\"" % data.root
        hip_expr = "\"%s\"" % data.hip
        curves = self.skel.animation_data.action.fcurves
        for c in curves:
            if root_expr in c.data_path or hip_expr in c.data_path:
                curves.remove(c)

        root = self.skel.pose.bones[data.root]
        root.keyframe_insert(data_path="rotation_quaternion")
        root.keyframe_insert(data_path="location")
        root.keyframe_insert(data_path="scale")

        hip = self.skel.pose.bones[data.hip]
        ref_hip = ref.pose.bones[data.hip]
        for f in steps(context, self.skel.animation_data.action.frame_range):
            context.scene.frame_set(f)
            ref_mtx = world_mtx(ref, ref_hip)

            hip.matrix = pose_mtx(self.skel, hip, ref_mtx)
            hip.keyframe_insert(data_path="rotation_quaternion")
            hip.keyframe_insert(data_path="location")
            hip.keyframe_insert(data_path="scale")

        root.keyframe_insert(data_path="rotation_quaternion")
        root.keyframe_insert(data_path="location")
        root.keyframe_insert(data_path="scale")

        return {'FINISHED'}

    def invoke(self, context, event):
        self.skel = valid_armature(context)
        context.scene.frame_set(self.skel.animation_data.action.frame_range.x)

        data = context.scene.rm_data
        if data.root == "":
            data.root = self.skel.pose.bones[0].name
        if data.hip == "":
            data.hip = self.skel.pose.bones[1].name

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ANIM_OT_animate_in_place(bpy.types.Operator):
    """Remove root motion from action, causing it to animate in-place"""
    bl_idname = "anim.rm_anim_in_place"
    bl_label = "Animate In Place"
    bl_options = {'REGISTER', 'UNDO'}

    skel = None

    @classmethod
    def poll(cls, context):
        return valid_armature(context) is not None

    def modal(self, context, event):
        data = context.scene.rm_data
        expr = "\"%s\"" % data.root
        curves = self.skel.animation_data.action.fcurves
        for c in curves:
            if expr in c.data_path:
                curves.remove(c)

        root = self.skel.pose.bones[data.root]
        frames = self.skel.animation_data.action.frame_range
        for f in [round(frames.x), round(frames.y)]:
            context.scene.frame_set(f)
            root.keyframe_insert(data_path="rotation_quaternion")
            root.keyframe_insert(data_path="location")
            root.keyframe_insert(data_path="scale")

        return {'FINISHED'}

    def invoke(self, context, event):
        self.skel = valid_armature(context)
        context.scene.frame_set(self.skel.animation_data.action.frame_range.x)

        data = context.scene.rm_data
        if data.root == "":
            data.root = self.skel.pose.bones[0].name

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ANIM_OT_remove_ref_character(bpy.types.Operator):
    """Remove reference character and its properties"""
    bl_idname = "anim.rm_remove_ref_char"
    bl_label = "Finalize Root Motion Operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.rm_data.copy != ""

    def execute(self, context):
        char = bpy.data.objects.get(context.scene.rm_data.copy)
        context.scene.rm_data.copy = ""
        if char is None:
            return {'CANCELLED'}

        anim = char.animation_data.action
        if anim != None:
            bpy.data.actions.remove(anim, True)

        context.scene.objects.unlink(char)
        bpy.data.objects.remove(char, True)

        return {'FINISHED'}


class PANEL_PT_main_panel(bpy.types.Panel):
    bl_idname = "PANEL_PT_root_motionist_main"
    bl_label = "Root Motionist"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Animation"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return valid_armature(context) is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        col = layout.column(align=True)
        col.prop_search(context.scene.rm_data, "root", obj.pose, "bones", text="Root")
        col.prop_search(context.scene.rm_data, "hip", obj.pose, "bones", text="Hip")
        col.prop(obj.animation_data, "action", text="Anim")

        row = layout.row()
        row.prop(context.scene.rm_data, "step")

        col = layout.column(align=True)
        col.label(text="Root Motion:")
        row = col.row(align=True)
        row.operator("anim.rm_extract_root_motion", text="Extract")
        row.operator("anim.rm_integrate_rm", text="Integrate")
        col.operator("anim.rm_anim_in_place", text="Animate In-Place")

        layout.operator("anim.rm_remove_ref_char", text="Delete Ref Character")


def valid_armature(context):
    skel = context.active_object
    if skel is not None and skel.type == 'ARMATURE':
        if len(skel.pose.bones) >= 2:
            if skel.animation_data.action is not None:
                return skel
    return None


def world_mtx(armature, bone):
    return armature.convert_space(bone, bone.matrix, from_space='POSE', to_space='WORLD')


def pose_mtx(armature, bone, mat):
    return armature.convert_space(bone, mat, from_space='WORLD', to_space='POSE')


def debug_character(context, original):
    char = bpy.data.objects.get(context.scene.rm_data.copy)
    if char is not None:
        return char
    char = original.copy()
    char.data = original.data.copy()
    char.animation_data.action = original.animation_data.action.copy()
    char.name = "skel" + str(int(time.time()))
    context.scene.rm_data.copy = char.name
    context.scene.objects.link(char)
    return char


def steps(context, frames):
    last = round(frames.y)
    frms = list(range(round(frames.x), last + 1, context.scene.rm_data.step))
    if frms[-1] != last:
        frms.append(last)
    return frms


def register():
    bpy.utils.register_class(RootMotionData)
    bpy.utils.register_class(ANIM_OT_extract_root_motion)
    bpy.utils.register_class(ANIM_OT_integrate_root_motion)
    bpy.utils.register_class(ANIM_OT_animate_in_place)
    bpy.utils.register_class(ANIM_OT_remove_ref_character)
    bpy.utils.register_class(PANEL_PT_main_panel)

    bpy.types.Scene.rm_data = bpy.props.PointerProperty(type=RootMotionData)


def unregister():
    del bpy.types.Scene.rm_data

    bpy.utils.unregister_class(RootMotionData)
    bpy.utils.unregister_class(ANIM_OT_extract_root_motion)
    bpy.utils.unregister_class(ANIM_OT_integrate_root_motion)
    bpy.utils.unregister_class(ANIM_OT_animate_in_place)
    bpy.utils.unregister_class(ANIM_OT_remove_ref_character)
    bpy.utils.unregister_class(PANEL_PT_main_panel)
