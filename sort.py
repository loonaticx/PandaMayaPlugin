attribs = [
    "barrier", "barrier-no-mask",
    "ground", "floor", "dupefloor", "smooth-floors", "floor-collide",
    "camera-collide", "camera-collide-sphere", "camera-barrier", "cambarrier-sphere", "camtransparent",
    "camtransbarrier",
    "sphere", "invsphere", "tube", "trigger", "trigger-sphere", "bubble",
    "decal", "dual", "blend", "ghost", "binary", "multisample",
    "shadow", "shadow-cast", "fixed", "opaque", "background", "transparent", "gui-popup",
    "glass", "glow",
    "indexed", "model",
    "dcs", "localdcs", "netdcs", "notouch",
    "shground",
    "draw0", "draw1", "occlude",
    "billboard", "double-sided",
    "safety-net", "safety-gate", "pie", "catch-grab", "invisible",
    "dart", "structured",
    "surface-grass", "surface-snow", "surface-metal", "surface-water",  # you can add more later
    "seq2", "seq4", "seq6", "seq8", "seq10", "seq12", "seq24"
]

"""
egg-object-type-surface-dirt    <Tag> surface { dirt }
egg-object-type-surface-gravel  <Tag> surface { gravel }
egg-object-type-surface-grass   <Tag> surface { grass }
egg-object-type-surface-asphalt <Tag> surface { asphalt }
egg-object-type-surface-wood    <Tag> surface { wood }
egg-object-type-surface-water   <Tag> surface { water }
egg-object-type-surface-snow    <Tag> surface { snow }
egg-object-type-surface-ice   <Tag> surface { ice }
egg-object-type-surface-sticky  <Tag> surface { sticky }
egg-object-type-surface-metal  <Tag> surface { metal }
"""

print(sorted(attribs))