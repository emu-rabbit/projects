"""Build the Boundary Notes macaron from the accepted shared shell geometry.

Run with:
  blender --background --python scripts/blender/create_boundary_notes_macaron.py

The accepted Window Notes .blend is opened only to copy its two shell meshes.
Every material, filling, pied, and decoration created here is independent.
"""

from __future__ import annotations

import importlib.util
import math
import random
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[2]
BASE_BLEND = ROOT / "assets" / "models" / "window-notes-macaron.blend"
WORK_DIR = ROOT / ".tmp" / "blender" / "boundary-notes"
TEXTURE_DIR = WORK_DIR / "textures"
OUTPUT_DIR = ROOT / "assets" / "models"
BLEND_PATH = OUTPUT_DIR / "boundary-notes-macaron.blend"
GLB_PATH = OUTPUT_DIR / "boundary-notes-macaron.glb"
GLB_TEMP_PATH = WORK_DIR / "boundary-notes-macaron.export.glb"
PIPING_MASK = ROOT / "assets" / "textures" / "boundary-notes" / "piping-mask.png"


def load_shared_builder():
    source = ROOT / "scripts" / "blender" / "create_window_notes_macaron.py"
    spec = importlib.util.spec_from_file_location("window_notes_builder", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load shared macaron helpers from {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.WORK_DIR = WORK_DIR
    module.TEXTURE_DIR = TEXTURE_DIR
    return module


base = load_shared_builder()


def keep_accepted_shells() -> tuple[bpy.types.Object, bpy.types.Object]:
    """Open the accepted .blend and retain only its exact upper/lower shell meshes."""
    bpy.ops.wm.open_mainfile(filepath=str(BASE_BLEND))
    shells = {
        "upper": bpy.data.objects.get("Upper night-violet shell"),
        "lower": bpy.data.objects.get("Lower night-violet shell"),
    }
    if not shells["upper"] or not shells["lower"]:
        raise RuntimeError("The accepted shell objects were not found in the base .blend")

    keep = {shells["upper"], shells["lower"]}
    for object_ in list(bpy.data.objects):
        if object_ not in keep:
            bpy.data.objects.remove(object_, do_unlink=True)

    for shell in keep:
        shell.parent = None
        shell.location = (0, 0, 0)
        shell.rotation_euler = (0, 0, 0)
        shell.scale = (1, 1, 1)
        shell.data = shell.data.copy()
        shell.data.materials.clear()

    return shells["upper"], shells["lower"]


def create_materials() -> dict[str, bpy.types.Material]:
    return {
        "shell": base.create_material(
            "Soft burgundy blackcurrant shell",
            "#7D2438",
            roughness=0.86,
            texture_seed=2309,
            texture_profile="shell",
            roughness_variation=0.045,
            normal_seed=2309,
            normal_strength=0.16,
        ),
        "foot": base.create_material(
            "Crisp rose burgundy foot",
            "#842A40",
            roughness=0.96,
            texture_seed=2357,
            texture_profile="foot",
            roughness_variation=0.07,
            normal_seed=2357,
            normal_strength=0.38,
        ),
        "foot_crumb": base.create_material("Toasted rose foot crumbs", "#C45E70", roughness=0.95),
        "foot_pore": base.create_material(
            "Deep baked burgundy foot pores",
            "#5E152B",
            roughness=1.0,
            texture_seed=2381,
            texture_profile="foot",
            texture_size=256,
            roughness_variation=0.025,
        ),
        "core": base.create_material(
            "Rose Earl Grey cream core",
            "#F0B8B3",
            roughness=0.69,
            texture_seed=2411,
            texture_profile="cream",
            texture_size=256,
            roughness_variation=0.065,
            coat_weight=0.08,
            coat_roughness=0.3,
        ),
        "rose_cream": base.create_material(
            "Upper pale rose cream",
            "#EEABA8",
            roughness=0.70,
            texture_seed=2423,
            texture_profile="cream_filling",
            texture_size=256,
            roughness_variation=0.09,
            normal_seed=2423,
            normal_strength=0.15,
            coat_weight=0.08,
            coat_roughness=0.31,
        ),
        "ivory_cream": base.create_material(
            "Lower warm ivory Earl Grey cream",
            "#F2D7AC",
            roughness=0.67,
            texture_seed=2441,
            texture_profile="cream_filling",
            texture_size=256,
            roughness_variation=0.08,
            normal_seed=2441,
            normal_strength=0.13,
            coat_weight=0.10,
            coat_roughness=0.28,
        ),
        "blackcurrant": base.create_material(
            "Straight blackcurrant jelly boundary",
            "#4A0922",
            roughness=0.16,
            texture_seed=2473,
            texture_profile="jam",
            texture_size=256,
            roughness_variation=0.07,
            normal_seed=2473,
            normal_strength=0.06,
            transmission=0.14,
            coat_weight=0.62,
            coat_roughness=0.06,
            specular_level=0.44,
        ),
        "letter": base.create_material(
            "Folded warm ivory letter sugar",
            "#F7E4BF",
            roughness=0.78,
            texture_seed=2503,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.045,
            normal_seed=2503,
            normal_strength=0.11,
        ),
        "letter_shadow": base.create_material("Letter fold warm shadow", "#D5A46B", roughness=0.88),
        "letter_edge": base.create_material("Letter toasted pencil edge", "#A56A3D", roughness=0.92),
        "wax": base.create_material(
            "Honey amber rabbit wax seal",
            "#D88A25",
            roughness=0.60,
            texture_seed=2531,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.04,
            coat_weight=0.10,
            coat_roughness=0.24,
            specular_level=0.24,
        ),
        "wax_dark": base.create_material("Rabbit seal embossed line", "#693209", roughness=0.78),
        "wax_highlight": base.create_material(
            "Raised rabbit wax emboss",
            "#E3A03E",
            roughness=0.64,
            texture_seed=2543,
            texture_profile="painted_sugar",
            texture_size=128,
            roughness_variation=0.025,
        ),
        "piping_edge": base.create_material("Caramel pencil piping edge", "#9D5B41", roughness=0.94),
        "piping": base.create_material(
            "Short vanilla cream piping",
            "#F4D395",
            roughness=0.72,
            texture_seed=2557,
            texture_profile="cream",
            texture_size=256,
            roughness_variation=0.045,
            normal_seed=2557,
            normal_strength=0.08,
        ),
        "rose": base.create_material(
            "Rose sugar pearl",
            "#D9576B",
            roughness=0.70,
            texture_seed=2579,
            texture_profile="painted_sugar",
            texture_size=256,
            roughness_variation=0.04,
            normal_seed=2579,
            normal_strength=0.10,
            coat_weight=0.08,
            coat_roughness=0.28,
            specular_level=0.24,
        ),
        "rose_highlight": base.create_material("Rose pearl and jewel highlight", "#FFD4CA", roughness=0.5),
        "rose_shadow": base.create_material("Rose candy toasted edge", "#9D344D", roughness=0.72),
    }


def create_blackcurrant_ribbon(name: str, material: bpy.types.Material) -> bpy.types.Object:
    """Create the straight, narrow dark boundary between the two cream layers."""
    segments = 256
    levels = 11
    height = 0.16
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for level in range(levels):
        t = level / (levels - 1)
        profile = math.sin(t * math.pi) ** 0.72
        for index in range(segments):
            angle = index / segments * math.tau
            frontness = max(0.0, -math.sin(angle))
            radius = 1.76 + 0.10 * profile
            radius += profile * (0.012 * math.sin(angle * 4 + 0.8) + 0.006 * math.sin(angle * 13))
            center_z = -0.015 - 0.008 * frontness**2
            z = center_z + (t - 0.5) * height * (1 + 0.025 * math.sin(angle * 3))
            vertices.append((math.cos(angle) * radius, math.sin(angle) * radius, z))
    for level in range(levels - 1):
        for index in range(segments):
            following = (index + 1) % segments
            lower = level * segments + index
            upper = (level + 1) * segments + index
            faces.append((lower, level * segments + following, (level + 1) * segments + following, upper))
    bottom_center = len(vertices)
    vertices.append((0, 0, -0.015 - height / 2))
    top_center = len(vertices)
    vertices.append((0, 0, -0.015 + height / 2))
    top_start = (levels - 1) * segments
    for index in range(segments):
        following = (index + 1) % segments
        faces.append((bottom_center, following, index))
        faces.append((top_center, top_start + index, top_start + following))
    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    ribbon = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ribbon)
    base.cube_project_uv(ribbon, 3.4)
    base.smooth(ribbon)
    return ribbon


def create_solid_cream_layer(
    name: str,
    z: float,
    height: float,
    material: bpy.types.Material,
    seed: int,
    *,
    upper: bool,
) -> bpy.types.Object:
    """Create a closed, full-disc cream volume with a handmade outer bulge."""
    segments = 256
    levels = 21
    local_rng = random.Random(seed)
    phase_a = local_rng.random() * math.tau
    phase_b = local_rng.random() * math.tau
    phase_c = local_rng.random() * math.tau
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []

    for level in range(levels):
        t = level / (levels - 1)
        profile_power = 0.6 if upper else 0.82
        profile = math.sin(t * math.pi) ** profile_power
        soft_center = math.sin(t * math.pi) ** 1.5
        for index in range(segments):
            angle = index / segments * math.tau
            frontness = max(0.0, -math.sin(angle))
            broad_swell = 0.062 * math.sin(angle * 4 + phase_a)
            secondary_swell = 0.028 * math.sin(angle * 9 + phase_b + t * 0.9)
            handmade = 0.012 * math.sin(angle * 17 + phase_c - t * 1.7)
            bulge = 0.15 if upper else 0.13
            radius = 1.7 + bulge * profile
            radius += profile * (broad_swell + secondary_swell + handmade)
            radius += (0.052 if upper else 0.036) * frontness**2 * profile

            local_height = height * (
                1 + 0.035 * math.sin(angle * 3 + phase_b) + 0.016 * math.sin(angle * 7 + phase_c)
            )
            center_wobble = 0.012 * math.sin(angle * 3 + phase_a)
            center_wobble += 0.006 * math.sin(angle * 8 + phase_b)
            center_wobble += (-0.024 if upper else 0.008) * frontness**2
            surface_wobble = 0.006 * math.sin(angle * 11 + phase_c + t * 2.1) * soft_center
            z_position = z + center_wobble + (t - 0.5) * local_height + surface_wobble
            vertices.append((math.cos(angle) * radius, math.sin(angle) * radius, z_position))

    for level in range(levels - 1):
        for index in range(segments):
            following = (index + 1) % segments
            lower = level * segments + index
            upper_index = (level + 1) * segments + index
            faces.append((lower, level * segments + following, (level + 1) * segments + following, upper_index))

    bottom_center = len(vertices)
    vertices.append((0, 0, z - height / 2))
    top_center = len(vertices)
    vertices.append((0, 0, z + height / 2))
    top_start = (levels - 1) * segments
    for index in range(segments):
        following = (index + 1) % segments
        faces.append((bottom_center, following, index))
        faces.append((top_center, top_start + index, top_start + following))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    cream = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(cream)
    base.add_displacement(cream, 0.003, 0.11, seed)
    base.cube_project_uv(cream, 3.6)
    base.smooth(cream)
    return cream


def rounded_rectangle(width: float, height: float, radius: float, segments: int = 8) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for cx, cy, start in (
        (width / 2 - radius, height / 2 - radius, 0),
        (-width / 2 + radius, height / 2 - radius, math.pi / 2),
        (-width / 2 + radius, -height / 2 + radius, math.pi),
        (width / 2 - radius, -height / 2 + radius, math.pi * 1.5),
    ):
        for index in range(segments + 1):
            angle = start + index / segments * math.pi / 2
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    return points


def create_irregular_wax_seal(
    name: str,
    radius: float,
    depth: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Model a poured, slightly uneven wax disc instead of mapping a seal image."""
    segments = 72
    points: list[tuple[float, float]] = []
    for index in range(segments):
        angle = index / segments * math.tau
        edge = radius * (
            1.0
            + 0.027 * math.sin(angle * 5 + 0.4)
            + 0.018 * math.sin(angle * 9 - 0.7)
            + 0.010 * math.sin(angle * 17 + 1.1)
        )
        points.append((math.cos(angle) * edge, math.sin(angle) * edge))
    seal = base.create_extruded_polygon(name, points, depth, material, 0.010, uv_cube_size=0.5)
    base.smooth(seal)
    return seal


def create_local_curve(
    name: str,
    group: bpy.types.Object,
    points: list[tuple[float, float, float]],
    bevel: float,
    material: bpy.types.Material,
    *,
    cyclic: bool = False,
) -> bpy.types.Object:
    curve = base.create_curve(name, points, bevel, material, cyclic=cyclic, bezier=False)
    base.parent_local(curve, group)
    return curve


def create_rabbit_emboss(group: bpy.types.Object, materials: dict[str, bpy.types.Material]) -> None:
    """Build the rabbit mark as attached sugar relief with an outlined head and tapered ears."""
    seal_y = -0.040
    head_fill = base.create_extruded_polygon(
        "Rabbit seal raised head relief",
        base.ellipse_points(0.150, 0.132, 40),
        0.012,
        materials["wax_highlight"],
        0.005,
    )
    base.parent_local(head_fill, group, (0, seal_y - 0.016, 0.163))

    for side, angle in ((-1, math.radians(-12)), (1, math.radians(12))):
        ear_fill = base.create_extruded_polygon(
            f"Rabbit seal raised {'left' if side < 0 else 'right'} ear relief",
            base.ellipse_points(0.048, 0.142, 32),
            0.012,
            materials["wax_highlight"],
            0.004,
        )
        base.parent_local(ear_fill, group, (side * 0.034, seal_y + 0.092, 0.163))
        ear_fill.rotation_euler.z = angle

    head = [
        (math.cos(i / 40 * math.tau) * 0.075, seal_y - 0.015 + math.sin(i / 40 * math.tau) * 0.070, 0.173)
        for i in range(40)
    ]
    create_local_curve(
        "Rabbit seal embossed head outline",
        group,
        head,
        0.008,
        materials["wax_dark"],
        cyclic=True,
    )

    for side, angle in ((-1, math.radians(-12)), (1, math.radians(12))):
        cx = side * 0.034
        cy = seal_y + 0.092
        ear_points: list[tuple[float, float, float]] = []
        for i in range(32):
            theta = i / 32 * math.tau
            ex = math.cos(theta) * 0.025
            ey = math.sin(theta) * 0.073
            rotated_x = ex * math.cos(angle) - ey * math.sin(angle)
            rotated_y = ex * math.sin(angle) + ey * math.cos(angle)
            ear_points.append((cx + rotated_x, cy + rotated_y, 0.173))
        create_local_curve(
            f"Rabbit seal embossed {'left' if side < 0 else 'right'} ear outline",
            group,
            ear_points,
            0.007,
            materials["wax_dark"],
            cyclic=True,
        )

    nose = base.create_extruded_polygon(
        "Rabbit seal tiny nose relief",
        [(0, -0.016), (-0.013, 0.004), (0.013, 0.004)],
        0.008,
        materials["wax_dark"],
        0.003,
    )
    base.parent_local(nose, group, (0, seal_y - 0.025, 0.173))


SCREEN_RIGHT = Vector((0.5, 0.866)).normalized()
SCREEN_UP = Vector((-0.866, 0.5)).normalized()


def design_to_world(local_x: float, local_y: float) -> tuple[float, float]:
    point = SCREEN_RIGHT * local_x + SCREEN_UP * local_y
    return point.x, point.y


def create_letter_group(materials: dict[str, bpy.types.Material]) -> None:
    group = bpy.data.objects.new("Folded ivory letter with rabbit wax seal", None)
    bpy.context.collection.objects.link(group)
    # Landmark fit against the canonical 2D composition. The old candidate was
    # about one envelope-height too low and right, which made the pearl arc read
    # as a separate necklace instead of wrapping the letter.
    group_x, group_y = design_to_world(0.12, 0.30)
    group.location = (group_x, group_y, base.top_shell_surface_z(group_x, group_y) + 0.045)
    # The canonical envelope rises toward screen-right by roughly ten degrees.
    # Sixty degrees is screen-horizontal for the presentation camera.
    group.rotation_euler.z = math.radians(70)
    group.scale = (1.16, 1.16, 1.0)

    outline = base.create_extruded_polygon(
        "Folded letter toasted edge",
        rounded_rectangle(1.13, 0.80, 0.07),
        0.052,
        materials["letter_edge"],
        0.018,
        uv_cube_size=1.2,
    )
    base.parent_local(outline, group, (0, 0, 0.018))
    letter = base.create_extruded_polygon(
        "Warm ivory letter backing sugar sheet",
        rounded_rectangle(1.07, 0.74, 0.055),
        0.040,
        materials["letter"],
        0.015,
        uv_cube_size=1.1,
    )
    base.parent_local(letter, group, (0, 0, 0.052))

    # Four individually modeled sugar-paper folds. Their overlaps and height
    # changes generate the canonical envelope seams under grazing light.
    fold_specs = (
        (
            "Letter left folded sugar flap",
            [(-0.525, -0.345), (-0.525, 0.345), (0.005, -0.015)],
            0.016,
            0.079,
        ),
        (
            "Letter right folded sugar flap",
            [(0.525, -0.345), (0.525, 0.345), (-0.005, -0.015)],
            0.016,
            0.081,
        ),
        (
            "Letter lower folded sugar flap",
            [(-0.515, -0.335), (0.515, -0.335), (0.0, 0.035)],
            0.018,
            0.090,
        ),
        (
            "Letter raised upper sugar flap",
            [(-0.515, 0.335), (0.515, 0.335), (0.0, -0.055)],
            0.022,
            0.102,
        ),
    )
    for name, points, depth, z in fold_specs:
        flap = base.create_extruded_polygon(name, points, depth, materials["letter"], 0.008, uv_cube_size=1.0)
        base.parent_local(flap, group, (0, 0, z))

    seam_lines = (
        ("Letter left physical fold seam", [(-0.505, 0.315, 0.112), (0.0, -0.048, 0.112)]),
        ("Letter right physical fold seam", [(0.505, 0.315, 0.112), (0.0, -0.048, 0.112)]),
        ("Letter lower left physical fold seam", [(-0.500, -0.315, 0.105), (0.0, 0.028, 0.105)]),
        ("Letter lower right physical fold seam", [(0.500, -0.315, 0.105), (0.0, 0.028, 0.105)]),
    )
    for name, points in seam_lines:
        create_local_curve(name, group, points, 0.006, materials["letter_shadow"])

    seal = create_irregular_wax_seal(
        "Hand-poured honey rabbit wax seal",
        0.215,
        0.048,
        materials["wax"],
    )
    base.parent_local(seal, group, (0, -0.04, 0.132))
    rim_points = []
    for index in range(64):
        angle = index / 64 * math.tau
        rim_radius = 0.174 * (1.0 + 0.015 * math.sin(angle * 5 + 0.8))
        rim_points.append((math.cos(angle) * rim_radius, -0.04 + math.sin(angle) * rim_radius, 0.158))
    create_local_curve(
        "Rabbit wax seal irregular raised rim",
        group,
        rim_points,
        0.006,
        materials["wax_dark"],
        cyclic=True,
    )
    create_rabbit_emboss(group, materials)


def surface_path(points: list[tuple[float, float]], lift: float) -> list[tuple[float, float, float]]:
    result = []
    for local_x, local_y in points:
        x, y = design_to_world(local_x, local_y)
        result.append((x, y, base.top_shell_surface_z(x, y) + lift))
    return result


def reference_pixel_to_design(pixel_x: float, pixel_y: float) -> tuple[float, float]:
    """Map canonical 2D shell landmarks into the presentation-plane coordinates."""
    return (pixel_x - 625.0) / 274.0, (430.0 - pixel_y) / 207.0


def erode_binary(mask: np.ndarray) -> np.ndarray:
    padded = np.pad(mask, 1, mode="constant", constant_values=False)
    eroded = np.ones_like(mask, dtype=bool)
    for dy in range(3):
        for dx in range(3):
            eroded &= padded[dy : dy + mask.shape[0], dx : dx + mask.shape[1]]
    return eroded


def mask_radius_map(mask: np.ndarray) -> np.ndarray:
    """Approximate each pixel's distance from the traced piping boundary."""
    distance = np.zeros(mask.shape, dtype=np.float32)
    remaining = mask.copy()
    while remaining.any():
        distance[remaining] += 1.0
        remaining = erode_binary(remaining)
    return distance


def thin_mask(mask: np.ndarray) -> np.ndarray:
    """Zhang-Suen thinning: turn the authored silhouette into a one-pixel centerline."""
    image = mask.astype(np.uint8).copy()
    image[[0, -1], :] = 0
    image[:, [0, -1]] = 0
    while True:
        removed = 0
        for first_pass in (True, False):
            p2 = np.roll(image, -1, axis=0)
            p3 = np.roll(np.roll(image, -1, axis=0), -1, axis=1)
            p4 = np.roll(image, -1, axis=1)
            p5 = np.roll(np.roll(image, 1, axis=0), -1, axis=1)
            p6 = np.roll(image, 1, axis=0)
            p7 = np.roll(np.roll(image, 1, axis=0), 1, axis=1)
            p8 = np.roll(image, 1, axis=1)
            p9 = np.roll(np.roll(image, -1, axis=0), 1, axis=1)
            neighbors = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            transitions = (
                ((p2 == 0) & (p3 == 1)).astype(np.uint8)
                + ((p3 == 0) & (p4 == 1)).astype(np.uint8)
                + ((p4 == 0) & (p5 == 1)).astype(np.uint8)
                + ((p5 == 0) & (p6 == 1)).astype(np.uint8)
                + ((p6 == 0) & (p7 == 1)).astype(np.uint8)
                + ((p7 == 0) & (p8 == 1)).astype(np.uint8)
                + ((p8 == 0) & (p9 == 1)).astype(np.uint8)
                + ((p9 == 0) & (p2 == 1)).astype(np.uint8)
            )
            removable = (image == 1) & (neighbors >= 2) & (neighbors <= 6) & (transitions == 1)
            if first_pass:
                removable &= (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else:
                removable &= (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            removable[[0, -1], :] = False
            removable[:, [0, -1]] = False
            count = int(removable.sum())
            image[removable] = 0
            removed += count
        if removed == 0:
            break
    return image.astype(bool)


def skeleton_paths(skeleton: np.ndarray) -> tuple[list[list[tuple[int, int]]], list[tuple[int, int]]]:
    pixels = {tuple(point) for point in np.argwhere(skeleton)}

    def neighbors(point: tuple[int, int]) -> list[tuple[int, int]]:
        y, x = point
        linked: list[tuple[int, int]] = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                candidate = (y + dy, x + dx)
                if not (dy or dx) or candidate not in pixels:
                    continue
                # Do not add a diagonal shortcut when an orthogonal skeleton
                # pixel already joins the same corner. Otherwise every bend
                # becomes a false graph junction and produces chopped tubes.
                if dy and dx and ((y + dy, x) in pixels or (y, x + dx) in pixels):
                    continue
                linked.append(candidate)
        return linked

    adjacency = {point: neighbors(point) for point in pixels}
    nodes = {point for point, linked in adjacency.items() if len(linked) != 2}
    visited_edges: set[frozenset[tuple[int, int]]] = set()
    paths: list[list[tuple[int, int]]] = []

    def walk(start: tuple[int, int], following: tuple[int, int]) -> list[tuple[int, int]]:
        path = [start, following]
        previous, current = start, following
        visited_edges.add(frozenset((start, following)))
        while current not in nodes:
            candidates = [point for point in adjacency[current] if point != previous]
            if not candidates:
                break
            next_point = candidates[0]
            edge = frozenset((current, next_point))
            if edge in visited_edges:
                break
            visited_edges.add(edge)
            path.append(next_point)
            previous, current = current, next_point
        return path

    for node in sorted(nodes):
        for linked in adjacency[node]:
            edge = frozenset((node, linked))
            if edge not in visited_edges:
                paths.append(walk(node, linked))

    # A closed curl can have no graph nodes; seed any remaining loop edge.
    for point in sorted(pixels):
        for linked in adjacency[point]:
            edge = frozenset((point, linked))
            if edge not in visited_edges:
                paths.append(walk(point, linked))
    return paths, sorted(nodes)


def simplify_pixel_path(path: list[tuple[int, int]], spacing: float = 3.5) -> list[tuple[int, int]]:
    if len(path) <= 2:
        return path
    simplified = [path[0]]
    anchor_y, anchor_x = path[0]
    for point in path[1:-1]:
        y, x = point
        if math.hypot(x - anchor_x, y - anchor_y) >= spacing:
            simplified.append(point)
            anchor_y, anchor_x = point
    simplified.append(path[-1])
    return simplified


def create_traced_piping(materials: dict[str, bpy.types.Material]) -> None:
    """Sweep round, variable-radius cream tubes over the exact canonical trace."""
    mask_image = bpy.data.images.load(str(PIPING_MASK), check_existing=False)
    width, height = mask_image.size
    pixels = np.empty(width * height * 4, dtype=np.float32)
    mask_image.pixels.foreach_get(pixels)
    mask = pixels.reshape((height, width, 4))[::-1, :, 0] > 0.5
    mask[:100, :] = False
    mask[625:, :] = False
    mask[:, :165] = False
    mask[:, 620:] = False
    radius_map = mask_radius_map(mask)
    paths, nodes = skeleton_paths(thin_mask(mask))

    modeled_paths = 0
    for index, raw_path in enumerate(paths):
        if len(raw_path) < 7:
            continue
        path = simplify_pixel_path(raw_path)
        traced_length = sum(
            math.hypot(current[1] - previous[1], current[0] - previous[0])
            for previous, current in zip(path, path[1:])
        )
        if len(path) < 2 or traced_length < 4.0:
            continue
        world_points: list[tuple[float, float, float]] = []
        path_radii: list[float] = []
        for pixel_y, pixel_x in path:
            local_x, local_y = reference_pixel_to_design(float(pixel_x), float(pixel_y))
            world_x, world_y = design_to_world(local_x, local_y)
            world_points.append((world_x, world_y, base.top_shell_surface_z(world_x, world_y) + 0.060))
            path_radii.append(float(radius_map[pixel_y, pixel_x]))

        edge = create_variable_curve(
            f"Canonical traced piping toasted underside {modeled_paths + 1}",
            [(x, y, z - 0.012) for x, y, z in world_points],
            0.022,
            materials["piping_edge"],
            phase=index * 0.37,
            radii=path_radii,
        )
        edge.data.bevel_resolution = 3
        create_variable_curve(
            f"Canonical hand-piped vanilla sugar tube {modeled_paths + 1}",
            world_points,
            0.017,
            materials["piping"],
            phase=index * 0.37,
            radii=path_radii,
        )
        modeled_paths += 1

    print(f"PIPING_PATHS={modeled_paths}; PIPING_JUNCTIONS={len(nodes)}")


def sample_catmull_rom(control_points: list[tuple[float, float]], samples_per_segment: int = 14) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    for segment in range(len(control_points) - 1):
        p0 = Vector(control_points[max(0, segment - 1)])
        p1 = Vector(control_points[segment])
        p2 = Vector(control_points[segment + 1])
        p3 = Vector(control_points[min(len(control_points) - 1, segment + 2)])
        for sample in range(samples_per_segment):
            t = sample / samples_per_segment
            point = 0.5 * (
                2 * p1
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
            )
            result.append((point.x, point.y))
    result.append(control_points[-1])
    return result


def create_variable_curve(
    name: str,
    points: list[tuple[float, float, float]],
    bevel: float,
    material: bpy.types.Material,
    *,
    phase: float,
    radii: list[float] | None = None,
) -> bpy.types.Object:
    """Create a dense food-safe tube whose radius swells like hand piping."""
    curve_data = bpy.data.curves.new(name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 12
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for index, (point, coordinate) in enumerate(zip(spline.points, points)):
        point.co = (*coordinate, 1.0)
        normalized = index / max(1, len(points) - 1)
        authored_radius = 1.0
        if radii:
            authored_radius = max(0.62, min(1.70, radii[index] / 4.2))
        handmade = 1.0 + 0.045 * math.sin(normalized * math.tau * 3 + phase)
        handmade += 0.020 * math.sin(normalized * math.tau * 7 - phase)
        point.radius = authored_radius * handmade
    object_ = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(object_)
    curve_data.materials.append(material)
    return object_


def add_surface_sphere(
    name: str,
    local_x: float,
    local_y: float,
    radius: float,
    material: bpy.types.Material,
    *,
    faceted: bool = False,
) -> bpy.types.Object:
    x, y = design_to_world(local_x, local_y)
    seed = sum((index + 1) * ord(character) for index, character in enumerate(name))
    scale_x = 0.96 + 0.05 * math.sin(seed * 0.31)
    scale_y = 0.94 + 0.06 * math.sin(seed * 0.47 + 0.9)
    scale_z = 0.66 + 0.035 * math.sin(seed * 0.23 - 0.4)
    z = base.top_shell_surface_z(x, y) + radius * scale_z * 0.91
    if faceted:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=(x, y, z))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=radius, location=(x, y, z))
    sphere = bpy.context.object
    sphere.name = name
    sphere.data.materials.append(material)
    if not faceted:
        sphere.scale = (scale_x, scale_y, scale_z)
        sphere.rotation_euler.z = math.radians((seed % 17) - 8)
        base.smooth(sphere)
    return sphere


def create_rose_jewel(
    name: str,
    local_x: float,
    local_y: float,
    radius: float,
    materials: dict[str, bpy.types.Material],
) -> None:
    """Create one low, rose-cut candy with the five-point highlight in the 2D art."""
    x, y = design_to_world(local_x, local_y)
    surface_z = base.top_shell_surface_z(x, y)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=radius + 0.012,
        depth=0.032,
        location=(x, y, surface_z + 0.030),
    )
    backing = bpy.context.object
    backing.name = f"{name} toasted rose edge"
    backing.data.materials.append(materials["rose_shadow"])

    segments = 8
    jewel_vertices: list[tuple[float, float, float]] = []
    for level_radius, level_z, rotation in (
        (radius, 0.0, math.radians(18)),
        (radius, 0.030, math.radians(18)),
        (radius * 0.48, 0.076, math.radians(40.5)),
    ):
        for index in range(segments):
            angle = index / segments * math.tau + rotation
            jewel_vertices.append((math.cos(angle) * level_radius, math.sin(angle) * level_radius, level_z))
    jewel_vertices.append((0, 0, 0.094))
    jewel_faces: list[tuple[int, ...]] = []
    for index in range(segments):
        following = (index + 1) % segments
        jewel_faces.append((index, following, segments + following, segments + index))
        jewel_faces.append((segments + index, segments + following, segments * 2 + following, segments * 2 + index))
        jewel_faces.append((segments * 2 + index, segments * 2 + following, segments * 3))
    jewel_mesh = bpy.data.meshes.new(f"{name} rose-cut mesh")
    jewel_mesh.from_pydata(jewel_vertices, [], jewel_faces)
    jewel_mesh.materials.append(materials["rose"])
    jewel_mesh.update()
    jewel = bpy.data.objects.new(f"{name} faceted jewel sugar", jewel_mesh)
    bpy.context.collection.objects.link(jewel)
    jewel.location = (x, y, surface_z + 0.047)
    jewel.name = f"{name} faceted jewel sugar"

    star_points: list[tuple[float, float, float]] = []
    for index in range(10):
        angle = math.pi / 2 + index / 10 * math.tau
        point_radius = radius * (0.52 if index % 2 else 0.24)
        point_x, point_y = design_to_world(
            local_x + math.cos(angle) * point_radius,
            local_y + math.sin(angle) * point_radius,
        )
        star_points.append((point_x, point_y, surface_z + 0.148))
    base.create_curve(
        f"{name} five-point sugar highlight",
        star_points,
        0.009,
        materials["rose_highlight"],
        cyclic=True,
        bezier=False,
    )


def create_piping_and_rose_arc(materials: dict[str, bpy.types.Material]) -> None:
    create_traced_piping(materials)
    for index, (pixel_x, pixel_y, radius) in enumerate(((565, 140, 0.044), (434, 571, 0.046))):
        local_x, local_y = reference_pixel_to_design(pixel_x, pixel_y)
        add_surface_sphere(
            f"Detached canonical vanilla piping pearl {index + 1}",
            local_x,
            local_y,
            radius,
            materials["piping"],
        )

    rose_positions = [
        (1.16, 0.54, 0.082, False),
        (1.18, 0.39, 0.036, False),
        (1.18, 0.24, 0.040, False),
        (1.15, 0.07, 0.074, False),
        (1.06, -0.12, 0.112, True),
        (0.92, -0.28, 0.036, False),
        (0.74, -0.43, 0.071, False),
        (0.55, -0.56, 0.036, False),
        (0.35, -0.68, 0.106, True),
        (0.13, -0.76, 0.036, False),
        (-0.10, -0.81, 0.072, False),
        (-0.33, -0.82, 0.037, False),
        (-0.55, -0.77, 0.106, True),
        (-0.72, -0.67, 0.036, False),
        (-0.84, -0.54, 0.071, False),
        (-0.90, -0.39, 0.035, False),
        (-0.91, -0.23, 0.067, False),
    ]
    for index, (x, y, radius, faceted) in enumerate(rose_positions):
        if faceted:
            create_rose_jewel(f"Rose arc candy {index + 1}", x, y, radius, materials)
            continue
        world_x, world_y = design_to_world(x, y)
        surface_z = base.top_shell_surface_z(world_x, world_y)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=radius + 0.012,
            depth=0.018,
            location=(world_x, world_y, surface_z + 0.020),
        )
        rose_base = bpy.context.object
        rose_base.name = f"Rose arc candy {index + 1} grounded toasted edge"
        rose_base.data.materials.append(materials["rose_shadow"])
        base.smooth(rose_base)
        rose = add_surface_sphere(
            f"Rose arc candy {index + 1} round pearl",
            x,
            y,
            radius,
            materials["rose"],
        )
        if radius >= 0.07:
            highlight = add_surface_sphere(
                f"Rose arc candy {index + 1} soft highlight",
                x - 0.014,
                y + 0.012,
                radius * 0.24,
                materials["rose_highlight"],
            )
            highlight.location.z += radius * 0.44


def build_model() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0

    upper_shell, lower_shell = keep_accepted_shells()
    materials = create_materials()
    for shell in (upper_shell, lower_shell):
        shell.data.materials.append(materials["shell"])
    upper_shell.name = "Upper soft-burgundy Boundary Notes shell"
    lower_shell.name = "Lower soft-burgundy Boundary Notes shell"

    base.create_ruffled_foot(
        "Upper crisp rose macaron foot",
        0.49,
        materials["foot"],
        materials["foot_crumb"],
        materials["foot_pore"],
        2357,
    )
    base.create_ruffled_foot(
        "Lower crisp rose macaron foot",
        -0.50,
        materials["foot"],
        materials["foot_crumb"],
        materials["foot_pore"],
        2399,
    )
    base.create_cylinder("Rose Earl Grey cream core", 1.30, 0.92, 0, materials["core"], 0.13)
    create_solid_cream_layer(
        "Upper thick pale rose cream layer", 0.29, 0.50, materials["rose_cream"], 2423, upper=True
    )
    create_solid_cream_layer(
        "Lower thick warm ivory cream layer", -0.28, 0.46, materials["ivory_cream"], 2441, upper=False
    )
    create_blackcurrant_ribbon("Straight narrow blackcurrant jelly boundary", materials["blackcurrant"])
    create_letter_group(materials)
    create_piping_and_rose_arc(materials)

    root = bpy.data.objects.new("Boundary Notes Macaron", None)
    bpy.context.collection.objects.link(root)
    for object_ in list(bpy.context.scene.objects):
        if object_ is not root and object_.parent is None:
            object_.parent = root

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), compress=True)
    GLB_TEMP_PATH.unlink(missing_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_TEMP_PATH),
        export_format="GLB",
        export_apply=True,
        export_yup=True,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    GLB_TEMP_PATH.replace(GLB_PATH)
    print(f"BLEND={BLEND_PATH} ({BLEND_PATH.stat().st_size} bytes)")
    print(f"GLB={GLB_PATH} ({GLB_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    build_model()
