# Root Motionist

Root Motionist is a [Blender](https://www.blender.org/) add-on for adding root
motion to animated characters. For more info about what root motion is and when
it is useful, see the [Unreal Engine Documentation](https://docs.unrealengine.com/latest/INT/Engine/Animation/RootMotion/)
about the topic.

Many popular character creation and animation tools use their own skeleton
layouts for internal processing, matching animations to characters and when
exporting to formats such as FBX or OBJ. Those skeletons are usually rooted
at the hip joint, making it the first bone in the hierarchy with all other
bones being descendants of it. When an animation moves a character around
in space, it is this bone that drives the motion.

Game engines like Unity and Unreal require an additional root bone, located
at ground level at the skeleton's origin, for root motion to work. This bone
needs to drive the motion instead of the hip bone. In order for that to work,
all animation data that drives a character's movement through space needs to
be transferred to the root bone while preserving the actual animation.

Root Motionist takes care of transferring the animation data between hip and
root bones while preserving the animation of the character as a whole. It
generates root motion with near perfect results in a fraction of a second.

# Installation

- Extract the *root_motion* folder to Blender's add-on directory, usually
located at *[Blender directory]/[version]/scripts/addons/*
- Enable the add-on in Blender's user preferences under the category *Add-ons*

# Usage

There are two ways to access Root Motionist's functions.

1. Direct access to its operators via the toolbox menu. Recommended only if
you're familiar with Root Motionist and don't need to set up the data
necessary for Root Motionist to work properly.
2. Through a panel in the *Animation* tab in the toolbar on the left of the 3D
viewport. This is the recommended way for beginners because it provides convenient
access to all settings and properties that need to be set before Root Motionist
can do its work.

The following sections give a brief overview of the Root Motionist panel in
the toolbar. The Animation tab is only visible in **Object Mode**, the panel
only when the active object in the viewport is an armature.

### Prerequisites

The character's skeleton is expected to already have a root bone, located at
(0,0,0) in the skeleton's local space, i.e. on the ground between its feet.
Inserting a root bone and parenting the original skeleton to that bone is
fairly easy and straightforward in Blender.

The root bone should also have the character's movement roughly keyframed: If
the character turns 90 degrees, the bone should do that; if the  character
moves a total of four steps forward, the root bone should have that distance
keyframed at the end of the animation. This will of course completely displace
the character's movement, but that's no problem. After all, correcting this is
exactly what Root Motionist is for. These adjustments need not be precise
and it is usually sufficient to set three to five keys even for fairly involved
animations. If there's something to watch out for, it's that the position on
the first and the last frame are chosen with some care because they are usually
the bridge to animations that follow. (Then again, such animation transitions
usually involve some amount of blending, masking small discrepancies between
poses.)

It is planned to reduce the amount of pre-work in future releases so that, for
example, a root bone is inserted automatically if it doesn't already exist.
For now, these are the two steps that have to be taken manually.

### Setup Parameters

There are three setup parameters that determine which bones to use and on which
animation to work on.

1. **Root** provides a dropdown selection for choosing which one of the
skeleton's bones should act as the root bone. This will be the one that drives
the character's motion and should generally be the root of the bone hierarchy.
2. **Hip** selects the bone that is the current motion driver, usually positioned
around the skeleton's mid section. When importing from third-party packages,
this is usually the original root of the bone hierarchy, but there might be
skeleton setups with an already existing root bone and some helper bones
(IK drivers for example) between that and the actual hip bone.
3. **Anim** is for selecting which animation to transform. It provides a list
of all the animations that currently exist in the blend file. As of v0.2.0
Root Motionist works directly on that animation, so if you want to be extra
safe, you have to create a safety copy by yourself.

### Create Root Motion

A click on **Create** starts the conversion. After it has finished, two things
will have happened. First, the animation is the same as it was originally, right
after being imported into Blender, only now with the root bone driving all
movement of the character in the world. Second, a copy of the character will
have appeared in exactly the same place. This is the reference character, and
it can be used to check if the conversion result is satisfactory. This character
plays the original animation and if all went well, both characters are
overlapping completely when playing back the animation.

The corresponding toolbox operator is called *Create Root Motion*.

### Remove Root Motion
**Remove** does the opposite of **Create**. It operates on a character that
contains root motion and transfers the relevant animation data to the hip bone.
This can be used for reverting the changes from the previous step as well as
for "cleaning out" root motion from third-party animations when the pipeline
requires root motion to not be present. Like **Create**, **Remove**, too,
creates a reference character.

The corresponding toolbox operator is called *Remove Root Motion*.

### Animate In-Place

Visually, the animation is the same before and after creating or removing root
motion; the character performs the exact same movement, only the motion through
the world is driven by another bone than before. **Animate In-Place** differs
in that it not only removes any motion from the root bone, it also clears any
animation data that would move the character through the world.

This is useful when the animation itself is needed and would normally move the
character, but movement is intended to be driven outside of the character, for
example by player input or AI controllers. Mocap data often fits this.
**Animate In-Place** provides a one-click solution for extracting the animation
without the need to manually reset movement.

The corresponding toolbox operator is called *Clear Root Motion*.

### Delete Reference Character

The button **Delete Ref Character** deletes all intermediate data that was
created while converting between animations. This includes the reference
skeleton and all meshes bound to it, the debug material used for distinguishing
between original and reference character, and the reference animation.

Although the reference character can be reused between operations, it is
advisable to delete it before performing an operation of a different kind than
the one that was just performed. This guarantees that no data is lost after
certain combinations of creating, clearing and removing root motion.
