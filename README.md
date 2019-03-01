# Root Motionist

Root Motionist is a [Blender](https://www.blender.org/) add-on for adding and
dealing with root motion on animated characters. For more info about what root
motion is and when it is useful, see the [Unreal Engine Documentation]
(https://docs.unrealengine.com/latest/INT/Engine/Animation/RootMotion/)
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
generates root motion with near perfect results with minimal manual work.

# Installation

- Extract the *root_motion* folder to Blender's add-on directory, usually
located at *[Blender directory]/[version]/scripts/addons/*
- Enable the add-on in Blender's user preferences under the category *Add-ons*

# Usage

All of Root Motionist's functions can be found in panels in the *Animation* tab
inside the 3D viewport's toolbar. The Animation tab is only visible in
**Object Mode**, the panels only when the active object in the viewport is an
armature.

## Root Motionist Panel

This section gives a brief overview of the Root Motionist panel.

### Setup Parameters

There are three required setup parameters that determine which bones to use and
whichanimation to work on.

1. **Root** provides a dropdown selection for choosing which one of the
skeleton's bones should act as the root bone. If root motion exists, this will
be the one that drives the character's motion. It should be the root of the bone
hierarchy.
2. **Hip** is the bone that is the motion driver before root motion is extracted
or after it is removed, usually positioned around the skeleton's mid section.
When importing from third-party packages, this is often the original root of the
bone hierarchy, but there might be skeleton setups with an already existing root
bone.
3. **Anim** is for selecting which animation to transform. It provides a list
of all the animations that currently exist in the blend file. As of v0.2.0
Root Motionist works directly on that animation, so if you want to be extra
safe, you have to create a safety copy by yourself.

Additional parameters exist to fine-tune the way that root motion is extacted.
These are:

1. **Step Size** determines how many frames to advance when stepping through the
animation for root motion extraction. A step size of 1 means that we stop at
every frame and compute the root bone's motion. This yields the most precise
results, but can get jittery at times. A step size of 30 means we compute root
motion only every 30th frame, leading to less precision but more smoothness in
the root bone's path.
2. **Ignore Rotation**, if enabled, does not take bone rotation into account
when computing root motion. This is useful when the root bone should only drive
the character's location and ignore any rotational movement that might be going on
in the driver bone. An animation in which the character stumbles, tumbles and
falls forward should probably ignore rotation in order to produce cleaner root
motion, while a turn-in-place animation would almost always include rotation.
3. **Extract Vertical Motion**. For most types of character locomotion, vertical
motion is not necessary for root motion extraction and can lead to undesired
behavior. By default, any movement of the driver bone along the global Z-axis
is ignored when extracting root motion. If desired, for example for sloped
movement, this option can be enabled so that the root bone moves along all three
axes.

### Extract Root Motion

The character's skeleton is expected to already have a root bone, located at
(0,0,0) in the skeleton's local space, i.e. on the ground between its feet.
Inserting a root bone and parenting the original skeleton to that bone is
fairly easy and straightforward in Blender. Any keyframed movement that might
exist on the root bone prior to extraction will be overwritten.

It is planned to reduce the amount of manual work in future releases so that, for
example, a root bone is inserted automatically if it doesn't already exist.

A click on **Extract** starts the conversion. After it has finished, two things
will have happened. First, the animation is the same as it was originally, right
after being imported into Blender, only now with the root bone driving all
movement of the character in the world. Second, a copy of the armature will
have appeared in exactly the same place. This is the reference character, and
it can be used to check if the conversion result is satisfactory. This character
plays the original animation and if all went well, the bones of both armatures
are overlapping completely when playing back the animation.

### Integrate Root Motion

**Integrate** does the opposite of **Extract**. It simply removes all root motion
that might exist in an animation while keeping it otherwise intact. Apart from
the root bone's movement, the animation will look the same before and after.
This can be used for reverting the changes from the previous step as well as for
"cleaning out" root motion from third-party animations when the pipeline requires
root motion to not be present. Like **Extract**, **Integrate** creates a reference
character.

### Animate In-Place

Visually, the animation is the same before and after extracting or integrating
root motion; the character performs the exact same movement, only the motion
through the world is driven by another bone than before. **Animate In-Place**
differs in that it not only removes any motion from the root bone, it also clears
any animation data that would move the character through the world.

This is useful when the animation itself would normally move the character, but
movement is intended to be driven by simulation instead of animation, for example
by player input or AI controllers. **Animate In-Place** provides a one-click
solution for extracting the animation without the need to manually reset movement.
For it to work, an animation should first be driven by root motion.

Note that, while **Extract** and **Integrate** can each be used to reverse the
other, **Animate In-Place** is irreversible in that there is no way to
automatically convert an in-place animation back to one that has motion applied.

### Delete Reference Character

The button **Delete Ref Character** deletes all intermediate data that was
created while converting between animations. This includes the reference
skeleton and all animations bound to it.

Although the reference character can be reused between operations, it is
advisable to delete it before performing an operation of a different kind than
the one that was just performed. This guarantees that no data is lost after
certain combinations of extracting, clearing and integrating root motion.
