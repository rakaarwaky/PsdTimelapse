from domain.value_objects import EasingType

# --- 4 Scenes x 3 = 12 (10 unique BEST easings) ---
SCENES = [
    # Scene 1: Velocity Ramps
    {
        "name": "Scene 1: Velocity Ramps",
        "items": [
            {"color": (255, 100, 150, 255), "easing": EasingType.WHIP_PAN, "label": "WHIP_PAN"},
            {"color": (
                100,
                255,
                200,
                255), "easing": EasingType.REVERSE_RAMP, "label": "REVERSE_RAMP"},
            {"color": (
                200,
                150,
                255,
                255), "easing": EasingType.CINEMATIC_RAMP, "label": "CINEMATIC_RAMP"},
        ]
    },
    # Scene 2: Bouncy Effects
    {
"name": "Scene 2: Bouncy Effects",
"items": [
    {"color": (255, 200, 100, 255), "easing": EasingType.BOUNCE, "label": "BOUNCE"},
    {"color": (
        100,
        200,
        255,
        255), "easing": EasingType.ELASTIC_SNAP, "label": "ELASTIC_SNAP"},
    {"color": (
        200,
        255,
        100,
        255), "easing": EasingType.SMOOTH_OVERSHOOT, "label": "SMOOTH_OVERSHOOT"},
]
},
# Scene 3: Cinematic
{
    "name": "Scene 3: Cinematic",
    "items": [
        {"color": (150, 100, 255, 255), "easing": EasingType.EXPO_BURST, "label": "EXPO_BURST"},
        {"color": (
            255,
            150,
            100,
            255), "easing": EasingType.ANTICIPATION, "label": "ANTICIPATION"},
        {"color": (
            100,
            255,
            150,
            255), "easing": EasingType.EASE_OUT_BACK, "label": "EASE_OUT_BACK", "overshoot": 0.5},  # noqa: PLR0913, PLR0912
    ]
},
# Scene 4: Physics
{
    "name": "Scene 4: Physics",
    "items": [
        {"color": (
            255,
            100,
            255,
            255), "easing": EasingType.GRAVITY_FALL, "label": "GRAVITY_FALL"},
        {"color": (
            100,
            255,
            255,
            255), "easing": EasingType.EASE_OUT_ELASTIC, "label": "EASE_OUT_ELASTIC"},
        {"color": (
            255,
            255,
            100,
            255), "easing": EasingType.EASE_IN_OUT, "label": "EASE_IN_OUT"},
    ]
},
]

# Layout: 3 horizontal bars stacked vertically (WIDE for comparing speed)
POSITIONS = [
    (50, 80, 700, 100),    # Top bar (wide!)
    (50, 220, 700, 100),   # Middle bar
    (50, 360, 700, 100),   # Bottom bar
]
]

SCENE_DURATION = 5.0  # seconds per scene
TRANSITION_GAP = 0.5  # gap between scenes
