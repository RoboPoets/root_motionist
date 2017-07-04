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
at ground level at the skeleton's origin, for root motion to work.
