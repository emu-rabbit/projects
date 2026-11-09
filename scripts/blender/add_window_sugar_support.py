"""Add a small edible back brace to the authored Window Notes checkpoint.

Run: blender --background --python scripts/blender/add_window_sugar_support.py
Preserves the checkpoint's hand-adjusted decoration transforms.
"""

from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
BLEND = ROOT / "assets/models/window-notes-macaron.blend"
GLB = BLEND.with_suffix(".glb")
NAME = "Dusky violet sugar plaque back brace"


def main():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    existing = bpy.data.objects.get(NAME)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)

    pane = bpy.data.objects["Inset warm apricot sugar-glass pane"]
    shell = bpy.data.objects["Upper night-violet shell"]
    group = bpy.data.objects["Arched window sugar plaque"]
    bpy.context.view_layer.update()
    shell_inverse = shell.matrix_world.inverted()
    back = (pane.matrix_world.to_3x3() @ Vector((0, 0, -1)))
    back.z = 0
    back.normalize()

    def shell_contact(point):
        origin = Vector((point.x, point.y, 5))
        hit, location, _, _ = shell.ray_cast(
            shell_inverse @ origin,
            shell_inverse.to_3x3() @ Vector((0, 0, -1)),
        )
        if not hit:
            raise RuntimeError("Sugar support must land on the upper shell")
        contact = shell.matrix_world @ location
        contact.z -= 0.025  # Embed the rounded foot rather than leave a gap.
        return contact

    vertices = []
    for x in (-0.065, 0.065):
        # A low sugar wedge braces the pane without dominating its silhouette.
        upper = pane.matrix_world @ Vector((x, 0.34, -0.002))
        lower = pane.matrix_world @ Vector((x, 0.02, -0.009))
        vertices.extend((upper, shell_contact(lower), shell_contact(upper + back * 0.23)))
    inverse = group.matrix_world.inverted()
    mesh = bpy.data.meshes.new(NAME)
    mesh.from_pydata([inverse @ v for v in vertices], [], [
        (0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5),
    ])
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    brace = bpy.data.objects.new(NAME, mesh)
    bpy.context.collection.objects.link(brace)
    brace.parent = group
    # Use the actual rear-frame material, including its baked sugar texture.
    brace.data.materials.append(bpy.data.materials["Deep violet sugar frame edge and back"])
    bpy.ops.object.select_all(action="DESELECT")
    brace.select_set(True)
    bpy.context.view_layer.objects.active = brace
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=0.65)
    bpy.ops.object.mode_set(mode="OBJECT")
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    bevel = brace.modifiers.new("Soft moulded sugar edges", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 5
    bevel.harden_normals = True
    normals = brace.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    normals.keep_sharp = True

    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), compress=True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB), export_format="GLB", export_apply=True,
        export_yup=True, export_animations=False, export_cameras=False,
        export_lights=False, export_materials="EXPORT",
    )
    print("Added sugar back brace with four embedded shell contacts:", list(vertices))


if __name__ == "__main__":
    main()
