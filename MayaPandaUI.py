from enum import IntEnum
from math import ceil

import pymel.core as pm
import os
import time

from natsort import natsorted
from typing import List, Set
from dataclasses import dataclass, field

# region GLOBALS
EGG_OBJECT_TYPE_ARRAY = "gMP_PY_EggObjectTypeArray"
PANDA_FILE_VERSIONS = "gMP_PY_PandaFileVersions"
PANDA_SDK_NOTICE = "gMP_PY_ChoosePandaFileNotice"
ADDON_RELEASE_VERSION = "gMP_PY_ReleaseRevision"
MAYA_VER_SHORT = "gMP_PY_MayaVersionShort"

# endregion

"""
https://help.autodesk.com/cloudhelp/2023/CHS/Maya-Tech-Docs/PyMel/generated/functions/pymel.core.windows/pymel.core
.windows.button.html?highlight=button#pymel.core.windows.button
"""


def hex_to_rgb(hex_color):
    """Converts a hex color code to RGB values (0-255)."""

    # Remove the '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert hex values to integers
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return r, g, b


def hex_to_rgb_normalized(hex_color):
    """Converts a hex color code to normalized RGB values (0-1)."""

    r, g, b = hex_to_rgb(hex_color)
    return r / 255, g / 255, b / 255


class OTCategory(IntEnum):
    NoCategory = 0
    EmptyAttr = 100
    CollisionAttr = 200
    TriggerAttr = 250
    AlphaBlendAttr = 300
    AlphaOpAttr = 350
    DCSAttr = 400
    TagAttr = 500
    SeqAttr = 600
    BinAttr = 700
    BillboardAttr = 800
    ToontownAttr = 900  # specific to toontown


@dataclass
class ObjectTypeCategoryDefinition:
    name: str
    type_id: OTCategory
    friendly_name: str
    color: str
    color_alt: str = ""
    text_color: str = "white"
    children: List["ObjectTypeDefinition"] = field(default_factory = lambda: list())

    # Maya ui control holder
    FrameLayout = None

    def get_children(self):
        return natsorted(self.children, key = lambda x: x.name.lower())


NoCategory = ObjectTypeCategoryDefinition("none", OTCategory.NoCategory, "No Category", "#514e52")
CollideCategory = ObjectTypeCategoryDefinition("Collide", OTCategory.CollisionAttr, "Collision", "#ac4a78")
TriggerCategory = ObjectTypeCategoryDefinition("Trigger", OTCategory.TriggerAttr, "Trigger", "#ac2e37", "#482526")
AlphaBlendModeCategory = ObjectTypeCategoryDefinition("AlphaBlend", OTCategory.AlphaBlendAttr, "Alpha Blend", "#2f4e79")
AlphaOperationCategory = ObjectTypeCategoryDefinition("AlphaOp", OTCategory.AlphaOpAttr, "Alpha Op", "#433d79")
DCSCategory = ObjectTypeCategoryDefinition("DCS", OTCategory.DCSAttr, "DCS", "#244a14", "#354638")
SequenceCategory = ObjectTypeCategoryDefinition("Sequence", OTCategory.SeqAttr, "Sequence", "#7e4a1f")
BinCategory = ObjectTypeCategoryDefinition("Bin", OTCategory.BinAttr, "Bin", "#555eff", "#3d4351")
BillboardCategory = ObjectTypeCategoryDefinition(
    "Billboard", OTCategory.BillboardAttr, "Billboard", "#7a4a79", "#6e5a6a"
)
TagCategory = ObjectTypeCategoryDefinition("Tag", OTCategory.TagAttr, "Tag", "#a9ffb6")
ToontownCategory = ObjectTypeCategoryDefinition("Toontown", OTCategory.ToontownAttr, "Toontown", "#baa05e", "#ffb31f")

CategoryDefs = {
    OTCategory.NoCategory: NoCategory,
    OTCategory.CollisionAttr: CollideCategory,
    OTCategory.TriggerAttr: TriggerCategory,
    OTCategory.AlphaBlendAttr: AlphaBlendModeCategory,
    OTCategory.AlphaOpAttr: AlphaOperationCategory,
    OTCategory.DCSAttr: DCSCategory,
    # OTCategory.TagAttr: TagCategory,
    OTCategory.SeqAttr: SequenceCategory,
    OTCategory.BinAttr: BinCategory,
    OTCategory.BillboardAttr: BillboardCategory,
    OTCategory.ToontownAttr: ToontownCategory
}


@dataclass
class ObjectTypeDefinition:
    name: str
    description: List[str] = field(default_factory = lambda: list())
    flags: List[str] = field(default_factory = lambda: list())
    category: ObjectTypeCategoryDefinition = NoCategory
    friendly_name: str = ""
    text_color: str = ""

    @property
    def color(self):
        if not self.text_color:
            return self.category.color_alt if self.category.color_alt else self.category.color
        return self.text_color

    # Maya controllers
    mel_id = -1  # todo? meant to be stored as the internal enum value when defined into a mel global attr
    Button = None


###


OT_NEW = [
    ObjectTypeDefinition(
        name = "barrier",
        description = [
            'Creates a barrier that other objects cannot pass through.',
            'The collision is active on the "Normals" side of the object(s)'
        ],
        category = CollideCategory,
        flags = ['<Collide> { Polyset descend }']
    ),
    ObjectTypeDefinition(
        name = "barrier-no-mask",
        description = [],
        category = CollideCategory,
        flags = ['<Collide> { Polyset descend }']
    ),
    ObjectTypeDefinition(
        name = "floor",
        description = [
            'Creates a collision from the object(s) that "Avatars" can walk on.',
            'If the surface is angled, the Avatar will not slide down it.',
            'The collision is active on the "Normals" side of the object(s)'
        ],
        category = CollideCategory,
        flags = ['<Scalar> collide-mask { 0x02 }', '<Collide> { Polyset descend level }']
    ),
    ObjectTypeDefinition(
        name = "floor-collide",
        description = [],
        category = CollideCategory,
        flags = ['<Scalar> collide-mask { 0x06 }']
    ),
    ObjectTypeDefinition(
        name = "shadow",
        description = [
            'Define a "shadow" object type, so we can render all shadows in their own bin '
            'and have them not fight with other transparent geometry.'
        ],
        flags = ['<Scalar> bin { shadow }', '<Scalar> alpha { blend-no-occlude }'],
        category = BinCategory,
    ),
    ObjectTypeDefinition(
        name = "shadow-cast",
        description = [
            'Gives the selected object(s) the required attributes so that an "Avatar\'s" shadow can be cast over it.',
            'Commonly used for casting an "Avatar\'s" shadow onto floors.'
        ],
        flags = ['<Tag> cam { shground }', '<Scalar> draw-order { 0 }', '<Scalar> bin { ground }'],
        category = BinCategory,
    ),
    ObjectTypeDefinition(
        name = "bin-fixed",
        flags = ['<Scalar> bin { fixed }'],
        category = BinCategory,
        friendly_name = "Fixed"
    ),
    ObjectTypeDefinition(
        name = "bin-gui-popup",
        flags = ['<Scalar> bin { gui-popup }'],
        category = BinCategory,
        friendly_name = "GUI Popup"
    ),
    ObjectTypeDefinition(
        name = "bin-unsorted",
        flags = ['<Scalar> bin { unsorted }'],
        category = BinCategory,
        friendly_name = "Unsorted"
    ),
    ObjectTypeDefinition(
        name = "bin-opaque",
        flags = ['<Scalar> bin { opaque }'],
        category = BinCategory,
        friendly_name = "Opaque"
    ),
    ObjectTypeDefinition(
        name = "bin-background",
        flags = ['<Scalar> bin { background }'],
        category = BinCategory,
        friendly_name = "Background"
    ),
    ObjectTypeDefinition(
        name = "bin-transparent",
        flags = ['<Scalar> bin { transparent }'],
        category = BinCategory,
        friendly_name = "Transparent"
    ),
    ObjectTypeDefinition(
        name = "dupefloor",
        description = [
            'This type first creates a duplicate of the selected object(s).',
            'Then, creates a floor collision from the duplicate object(s) that "Avatars" can walk on.',
            'If the surface is angled, the Avatar will not slide down it.',
            'The collision is active on the "Normals" side of the object(s)'
        ],
        category = CollideCategory,
        flags = ['<Collide> { Polyset keep descend level }']
    ),
    ObjectTypeDefinition(
        name = "smooth-floors",
        description = ['Makes floors smooth for the "Avatars" to walk and stand on.'],
        flags = [
            '<Collide> { Polyset descend }',
            '<Scalar> from-collide-mask { 0x000fffff }',
            '<Scalar> into-collide-mask { 0x00000002 }'
        ],
        category = CollideCategory,

    ),
    ObjectTypeDefinition(
        name = "camera-collide",
        description = ['Allows only the camera to collide with the geometry.'],
        flags = [
            '<Scalar> collide-mask { 0x04 }',
            '<Collide> { Polyset descend }'
        ],
        category = CollideCategory,

    ),
    ObjectTypeDefinition(
        name = "sphere",
        description = [
            'Creates a "minimum-sized" sphere collision around the selected object(s), '
            'that other objects cannot enter into.'
        ],
        flags = ['<Collide> { Sphere descend }'],
        category = CollideCategory,

    ),
    ObjectTypeDefinition(
        name = "tube",
        description = [
            'Creates a "minimum-sized" tube collision around the selected object(s), '
            'that other objects cannot enter into.'
        ],
        flags = ['<Collide> { Tube descend }'],
        category = CollideCategory,

    ),
    ObjectTypeDefinition(
        name = "trigger",
        description = [
            'Creates a collision that can be used as a "Trigger", which can be used to activate, or deactivate, '
            'specific processes.',
            'The collision is active on the "Normals" side of the object(s)'
        ],
        flags = ['<Collide> { Polyset descend intangible }'],
        category = TriggerCategory,

    ),
    ObjectTypeDefinition(
        name = "trigger-sphere",
        description = [
            'Creates a "minimum-sized" sphere collision that can be used as a "Trigger", which can be used to activate,'
            ' or deactivate, specific processes.',
            'The collision is active on the "Normals" side of the object(s)'
        ],
        flags = ['<Collide> { Sphere descend intangible }'],
        category = TriggerCategory,

    ),
    ObjectTypeDefinition(
        name = "invsphere",
        description = [
            'Creates a "minimum-sized" inverse-sphere collision around the selected object(s). '
            'Any object inside the sphere will be prevented from exiting the sphere.'
        ],
        flags = ['<Collide> { InvSphere descend }'],
        category = CollideCategory,

    ),
    ObjectTypeDefinition(
        name = "bubble",
        description = [
            '"bubble" puts a Sphere collision around the geometry, but does not otherwise remove the geometry.'
        ],
        flags = ['<Collide> { Sphere keep descend }'],
        category = CollideCategory,

    ),
    ObjectTypeDefinition(
        name = "dual",
        description = [
            'Normally attached to polygons that have transparency, '
            'that are in the scene by themselves, such as a Tree or Flower.'
        ],
        flags = ['<Scalar> alpha { dual }'],
        category = AlphaBlendModeCategory,
    ),
    ObjectTypeDefinition(
        name = "multisample",
        flags = ['<Scalar> alpha { ms }'],
        category = AlphaBlendModeCategory,

    ),
    ObjectTypeDefinition(
        name = "blend",
        flags = ['<Scalar> alpha { blend }'],
        category = AlphaBlendModeCategory,

    ),
    ObjectTypeDefinition(
        name = "decal",
        flags = ['<Scalar> decal { 1 }']
    ),
    ObjectTypeDefinition(
        name = "ghost",
        description = [
            '"ghost" turns off the normal collide bit that is set on visible geometry by default, '
            'so that if you are using visible geometry for collisions, '
            'this particular geometry will not be part of those collisions--'
            'it is ghostlike. Characters will pass through it.'
        ],
        flags = ['<Scalar> collide-mask { 0 }']
    ),
    ObjectTypeDefinition(
        name = "glass",
        flags = ['<Scalar> alpha { blend_no_occlude }'],
        category = AlphaBlendModeCategory,
    ),
    ObjectTypeDefinition(
        name = "glow",
        description = [
            '"glow" is useful for halo effects and things of that ilk. It renders the object in add mode instead '
            'of the normal opaque mode.'
        ],
        flags = ['<Scalar> blend { add }'],
        friendly_name = "Add",
        category = AlphaOperationCategory
    ),
    ObjectTypeDefinition(
        name = "binary",
        description = [
            'This mode of alpha sets transparency pixels to either on or off. No blending is used.'
        ],
        flags = ['<Scalar> alpha { binary }'],
        category = AlphaBlendModeCategory,
    ),
    ObjectTypeDefinition(
        name = "indexed",
        flags = ['<Scalar> indexed { 1 }']
    ),
    ObjectTypeDefinition(
        name = "model",
        description = [
            'This creates a ModelNode at the corresponding level, which is guaranteed not to be removed by any '
            'flatten operation. However, its transform might still be changed.'
        ],
        flags = ['<Model> { 1 }']
    ),
    ObjectTypeDefinition(
        name = "dcs",
        description = [
            'Indicates the node should not be flattened out of the hierarchy during conversion. '
            'The node\'s transform is important and should be preserved.'
        ],
        flags = ['<DCS> { 1 }'],
        category = DCSCategory,
    ),
    ObjectTypeDefinition(
        name = "netdcs",
        flags = ['<DCS> { net }'],
        category = DCSCategory,
        friendly_name = "Net"

    ),
    ObjectTypeDefinition(
        name = "localdcs",
        flags = ['<DCS> { local }'],
        category = DCSCategory,
        friendly_name = "Local"

    ),
    ObjectTypeDefinition(
        name = "notouch",
        description = [
            'Indicates the node, and below, should not be flattened out of the hierarchy during the conversion process.'
        ],
        flags = ['<DCS> { no-touch }'],
        category = DCSCategory,

    ),
    ObjectTypeDefinition(
        name = "double-sided",
        description = [
            'Defines whether the polygon will be rendered double-sided (i.e., its back face will be visible).'
        ],
        flags = ['<BFace> { 1 }']
    ),
    ObjectTypeDefinition(
        name = "billboard",
        description = [
            'Rotates the geometry to always face the camera. Geometry will rotate on its local axis.'
        ],
        flags = ['<Billboard> { axis }'],
        friendly_name = "BB-Axis",
        category = BillboardCategory,
    ),
    ObjectTypeDefinition(
        name = "seq2",
        description = [
            'Indicates a series of animation frames that should be consecutively displayed at 2 fps.'
        ],
        flags = ['<Switch> { 1 }', '<Scalar> fps { 2 }'],
        category = SequenceCategory,
    ),
    ObjectTypeDefinition(
        name = "seq4",
        description = [
            'Indicates a series of animation frames that should be consecutively displayed at 4 fps.'
        ],
        flags = ['<Switch> { 1 }', '<Scalar> fps { 4 }'],
        category = SequenceCategory,
    ),
    ObjectTypeDefinition(
        name = "seq6",
        description = [
            'Indicates a series of animation frames that should be consecutively displayed at 6 fps.'
        ],
        flags = ['<Switch> { 1 }', '<Scalar> fps { 6 }'],
        category = SequenceCategory,
    ),
    ObjectTypeDefinition(
        name = "seq8",
        description = [
            'Indicates a series of animation frames that should be consecutively displayed at 8 fps.'
        ],
        flags = ['<Switch> { 1 }', '<Scalar> fps { 8 }'],
        category = SequenceCategory,
    ),
    ObjectTypeDefinition(
        name = "seq10",
        description = [
            'Indicates a series of animation frames that should be consecutively displayed at 10 fps.'
        ],
        flags = ['<Switch> { 1 }', '<Scalar> fps { 10 }'],
        category = SequenceCategory,
    ),
    ObjectTypeDefinition(
        name = "seq12",
        description = [
            'Indicates a series of animation frames that should be consecutively displayed at 12 fps.'
        ],
        flags = ['<Switch> { 1 }', '<Scalar> fps { 12 }'],
        category = SequenceCategory,
    ),
    ObjectTypeDefinition(
        name = "seq24",
        description = [
            'Indicates a series of animation frames that should be consecutively displayed at 24 fps.'
        ],
        flags = ['<Switch> { 1 }', '<Scalar> fps { 24 }'],
        category = SequenceCategory,
    ),
    ObjectTypeDefinition(
        name = "ground",
        flags = ['<Scalar> bin { ground }'],
        category = BinCategory,
    ),
    ObjectTypeDefinition(
        name = "invisible",
        flags = []
    ),
    ObjectTypeDefinition(
        name = "catch-grab",
        flags = ['<Scalar> collide-mask { 0x08 }'],
        description = ['Things the magnet can pick up in the Cashbot CFO battle (same as CatchGameBitmask)'],
        category = ToontownCategory,
    ),
    ObjectTypeDefinition(
        name = "pet",
        flags = ['<Scalar> collide-mask { 0x10 }'],
        description = ['Pets avoid this'],
        category = ToontownCategory,
    ),
    ObjectTypeDefinition(
        name = "furniture-side",
        flags = ['<Scalar> collide-mask { 0x20 }'],
        category = ToontownCategory,
    ),
    ObjectTypeDefinition(
        name = "furniture-top",
        flags = ['<Scalar> collide-mask { 0x40 }'],
        category = ToontownCategory,
    ),
    ObjectTypeDefinition(
        name = "furniture-drag",
        flags = ['<Scalar> collide-mask { 0x80 }'],
        category = ToontownCategory,
    ),
    ObjectTypeDefinition(
        name = "pie",
        flags = ['<Scalar> collide-mask { 0x100 }'],
        category = ToontownCategory,
        description = ['Things we can throw a pie at.'],
    ),
]


def getOTNames(sortby=None):
    names = [ot.name for ot in OT_NEW]
    if sortby == "alphabetical":
        names = natsorted(names)
    elif sortby == "category":
        def sorting_key(item):
            category_id = item.category.type_id if item.category is not None else NoCategory.type_id
            name_lower = item.name.lower()
            return category_id, name_lower

        names = [ot.name for ot in natsorted(OT_NEW, key = sorting_key)]
    return names


Names2Definition = {ot.name: ot for ot in OT_NEW}
FriendlyNames = {ot.name: ot.friendly_name for ot in OT_NEW}

# Populates categories with children
for OTEntry in OT_NEW:
    OTEntry.category.children.append(OTEntry)


# region Main Functions
def MP_PY_PandaVersion(option):
    """
    Scan each loop for the value of the selected bam file version

    bam2egg executable file name should be the next value (+1) after version in the array
    egg2bam executable should be the second value (+2) after version in the array
    pview executable should be the third value (+3) after version in the array

       EXAMPLE $gMP_PY_PandaFileVersions ARRAY ENTRY: "Default","bam2egg","egg2bam","pview"
    """
    pm.melGlobals.initVar("string[]", PANDA_FILE_VERSIONS)
    executableToUse = ""
    selectedBamVersion = str(pm.optionMenu("MP_PY_BamVersionOptionMenu", query = 1, value = 1))
    for i in range(0, len(pm.melGlobals[PANDA_FILE_VERSIONS])):
        if selectedBamVersion == pm.melGlobals[PANDA_FILE_VERSIONS][i]:
            if option == "getBam2Egg":
                executableToUse = pm.melGlobals[PANDA_FILE_VERSIONS][i + 1]
            elif option == "getEgg2Bam":
                executableToUse = pm.melGlobals[PANDA_FILE_VERSIONS][i + 2]
            elif option == "getPview":
                executableToUse = pm.melGlobals[PANDA_FILE_VERSIONS][i + 3]
            break
    return executableToUse


def MP_PY_ConfirmationDialog(title, message, dialog_type):
    """
    Shows a confirmation dialog with the given title, message, and button type.

    :param title: Title of the dialog.
    :param message: Message displayed in the dialog.
    :param dialog_type: Type of dialog (e.g., "ok", "okcancel", "yesno", etc.).
    :returns: The value of the button pressed by the user.
    """
    if isinstance(message, list):
        message = "\n".join(message)
    # would be nice sometime in the future to have message be a list of strings, combined with \n separator
    # Define button configurations based on the dialog type
    button_configs = {
        "ok": {"buttons": ["OK"], "default": "OK", "cancel": "CANCEL"},
        "okcancel": {"buttons": ["OK", "CANCEL"], "default": "OK", "cancel": "CANCEL"},
        "selectcancel": {"buttons": ["SELECT", "CANCEL"], "default": "SELECT", "cancel": "CANCEL"},
        "yesno": {"buttons": ["YES", "NO"], "default": "YES", "cancel": "NO"},
        "downloadcancel": {"buttons": ["DOWNLOAD", "CANCEL"], "default": "DOWNLOAD", "cancel": "CANCEL"},
    }

    # Get the configuration for the dialog type
    config = button_configs.get(dialog_type)
    if not config:
        raise ValueError(f"Unknown dialog type: {dialog_type}")

    # Show the confirmation dialog
    return str(
        pm.confirmDialog(
            title = title,
            message = message,
            button = config["buttons"],
            defaultButton = config["default"],
            cancelButton = config["cancel"],
            dismissString = config["cancel"],
        )
    )


def MP_PY_PlaceholderFunc(*args, **kwargs):
    return MP_PY_ConfirmationDialog(
        "Not implemented!",
        [
            "Sorry, this feature is not implemented yet.",
        ],
        "ok",
    )


def MP_PY_AddEggObjectFlags(eggObjectType):
    """
    Add an egg-object-type to poly
    """
    pm.melGlobals.initVar("string[]", EGG_OBJECT_TYPE_ARRAY)
    # global egg-object-type array
    # generate attribute enumeration list from the array
    enumerationList = ":".join(pm.melGlobals[EGG_OBJECT_TYPE_ARRAY])
    # Verify the eggObjectType that was passed to this process exists in the $gMP_PY_EggObjectTypeArray array
    # If it does not, we skip processing and warn user.
    eggTypeInArray = eggObjectType in pm.melGlobals[EGG_OBJECT_TYPE_ARRAY]
    if eggTypeInArray == 1:
        indexNumber = -1
        # String version of array index number.
        # This is necessary, so we can verify the index number is not null/empty
        # Get the array index number of the $eggObjectType passed to this process
        # by iterating through each array item and compare them to the $eggObjectType
        for n in range(0, len(pm.melGlobals[EGG_OBJECT_TYPE_ARRAY])):
            if pm.melGlobals[EGG_OBJECT_TYPE_ARRAY][n] == eggObjectType:
                indexNumber = int(n)

        selectedNodes = pm.ls(sl = 1)
        # Variable to hold all currently selected nodes
        # Iterate through each selected node one-by-one
        if len(selectedNodes) == 0:
            return MP_PY_ConfirmationDialog(
                "Selection Error!",
                [
                    "You must first make a selection!",
                    "Please select at least one node, then try again."
                ],
                "ok",
            )

        for node in selectedNodes:
            for i in range(1, 11):
                if pm.objExists(str(node) + ".eggObjectTypes" + str(i)) == 1:
                    # At the very moment, we set our egg tag limit to 10 per node.
                    # There's not really a reason right now for why a user will get to this limit, but
                    # due to some prior hard-coded values with egg object types, we are capping it at 10.
                    if i == 10:
                        MP_PY_ConfirmationDialog(
                            "Egg-Object-Type Error!",
                            [
                                "Limit of 10 egg-object-types has already been reached.",
                                "No More Egg Object Types Supported for this node."
                            ],
                            "ok",
                        )
                else:
                    MP_PY_SetEggObjectTypeAttribute(enumerationList, eggObjectType, indexNumber, i, node)
                    break
    else:
        MP_PY_ConfirmationDialog(
            "Egg-Object-Type Error!",
            [
                "The selected egg-object-type was not found in the $gMP_PY_EggObjectTypeArray",
                "Please verify the object-type being passed and update the $gMP_PY_EggObjectTypeArray",
                "to include the egg-object-type if the type is the correct one needed.",
                "If you modify the $gMP_PY_EggObjectTypeArray DO NOT forget to update your PRC files.",
                "to include a reference of the egg-object-type you are adding."
            ],
            "ok",
        )
    # Message to user that the passed egg-object-type is NOT in the $gMP_PY_EggObjectTypeArray array

    if pm.window("MP_PY_DeleteEggObjectTypesWindow", exists = 1):
        MP_PY_GetEggObjectTypes()
    # Method to update the DeleteEggObjectTypesWindow window if it is currently being shown


def MP_PY_TexPathOptionsUI():
    """
    Updates the UI based on the selected texture path option.
    """
    selected_option = pm.radioCollection("MP_PY_TexPathOptionsRC", query = True, select = True)
    output_file_type = pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = True, select = True)

    # Default settings for text fields and buttons
    def set_fields(egg_enable=False, bam_enable=False, egg_clear=False, bam_clear=False):
        pm.textField("MP_PY_CustomEggTexPathTF", edit = True, enable = egg_enable, text = "" if egg_clear else None)
        pm.textField("MP_PY_CustomBamTexPathTF", edit = True, enable = bam_enable, text = "" if bam_clear else None)
        pm.button("MP_PY_BrowseEggTexPathBTN", edit = True, enable = egg_enable)
        pm.button("MP_PY_BrowseBamTexPathBTN", edit = True, enable = bam_enable)

    if selected_option == "MP_PY_ChooseDefaultTexPathRB":
        print("Default Texture Path Chosen\n")
        set_fields(egg_enable = False, bam_enable = False, egg_clear = True, bam_clear = True)

    elif selected_option == "MP_PY_ChooseCustomRefPathRB":
        print("Custom Texture Reference Path Chosen\n")
        if output_file_type == "MP_PY_ChooseEggRB":
            set_fields(egg_enable = True, bam_enable = False, bam_clear = True)
        elif output_file_type == "MP_PY_ChooseEggBamRB":
            set_fields(egg_enable = False, bam_enable = True, egg_clear = True)

    elif selected_option == "MP_PY_ChooseCustomTexPathRB":
        print("Custom Texture Path Chosen\n")
        set_fields(
            egg_enable = output_file_type in {"MP_PY_ChooseEggRB", "MP_PY_ChooseEggBamRB"},
            bam_enable = output_file_type == "MP_PY_ChooseEggBamRB"
        )


def MP_PY_OutputPathOptionsUI():
    """
    Updates the UI when a radio button is chosen
    """
    selectedRB = str(pm.radioCollection("MP_PY_OutputPathOptionsRC", query = 1, select = 1))
    if selectedRB == "MP_PY_ChooseDefaultOutputPathRB":
        print("Default Export File Path Chosen\n")
        pm.textField("MP_PY_CustomOutputPathTF", edit = 1, text = "", enable = 0)
        pm.button("MP_PY_BrowseOutputPathBTN", edit = 1, enable = 0)

    elif selectedRB == "MP_PY_ChooseCustomOutputPathRB":
        print("Custom Export File Path Chosen\n")
        pm.textField("MP_PY_CustomOutputPathTF", edit = 1, enable = 1)
        pm.button("MP_PY_BrowseOutputPathBTN", edit = 1, enable = 1)


def MP_PY_OutputFilenameOptionsUI():
    """
    Updates the UI when a radio button is chosen
    """
    selectedRB = str(
        pm.radioCollection("MP_PY_OutputFilenameOptionsRC", query = 1, select = 1)
    )
    if selectedRB == "MP_PY_ChooseOriginalFilenameRB":
        print("Default Export Filename Chosen\n")
        pm.textField("MP_PY_CustomFilenameTF", edit = 1, text = "", enable = 0)
        pm.button("MP_PY_BrowseFilenameBTN", edit = 1, enable = 0)

    elif selectedRB == "MP_PY_ChooseCustomFilenameRB":
        print("Custom Export Filename Chosen\n")
        pm.textField("MP_PY_CustomFilenameTF", edit = 1, enable = 1)
        pm.button("MP_PY_BrowseFilenameBTN", edit = 1, enable = 1)


def MP_PY_TransformModeUI():
    """
    Updates the UI when a radio button is chosen

    Specifies which transforms in the Maya file should be converted to transforms in the egg file.

    The option may be one of all, model, dcs, or none.

    The Panda default is model, which means only transforms on nodes that have the model or dcs flag are preserved in
    the converted egg file.
    """
    selectedRB = str(pm.radioCollection("MP_PY_TransformModeRC", query = 1, select = 1))

    if selectedRB == "MP_PY_ChooseTransformNoneRB":
        print("Saves no transform information\n")

    elif selectedRB == "MP_PY_ChooseTransformAllRB":
        print(
            "Save transforms of all objects, PRESERVES local pivot, orientation, scale, and shear"
            + "\nAll transform will remain when loaded into Panda3D\n"
        )

    elif selectedRB == "MP_PY_ChooseTransformDCSRB":
        print(
            "Save transforms of objects which have dcs-flag only," +
            "\nCLEARS local pivot, orientation, scale, and shear of the other objects." +
            "\nAll transform will be frozen to the vertices and will be 0 when loaded into Panda3D\n"
        )

    elif selectedRB == "MP_PY_ChooseTransformModelRB":
        print(
            "Save transforms of objects which have model-flag or dcs-flag only,"
            + "\nCLEARS local pivot, "
              "orientation, "
              "scale, and shear of the other "
              "objects"
            + "\nAll transform will be frozen to the vertices and will be 0 when loaded into Panda3D\n"
        )


def MP_PY_SetEggObjectTypeAttribute(enumerationList, eggObjectType, indexNumber, attributeNumber, node):
    # Determining variable on whether we can add egg-object-type attribute to node
    # Check for any currently attached egg-object-type attribute values on the node.
    # If a current attribute matches passed egg-object-type,
    # we skip adding it again and notify user it already exists.
    for i in range(1, 11):
        if pm.objExists(node + ".eggObjectTypes" + str(i)):
            if pm.getAttr((node + ".eggObjectTypes" + str(i)), asString = 1) == eggObjectType:
                MP_PY_ConfirmationDialog(
                    "Egg-Object-Type Error!",
                    [
                        f'egg-object-type - "{eggObjectType}"',
                        f"Already attached on node attribute:",
                        f"{node}.eggObjectTypes{i}",
                    ],
                    "ok",
                )
                return
        # Attribute exists, check if attributes matches the passed egg-object-type
        # Message to user that the egg-object-type is already assigned to node
        # Since attribute already exists on node, set our determining variable to 0 to skip adding it again

    defObj = Names2Definition[eggObjectType]
    # pm.color(node, rgbColor=hex_to_rgb_normalized(defObj.category.color), ud=1)
    pm.addAttr(
        node,
        ln = ("eggObjectTypes" + str(attributeNumber)),
        enumName = enumerationList,
        attributeType = "enum",
        keyable = 1,
    )
    # Adds the egg-object-type attribute to node if it was not already attached
    pm.setAttr((node + ".eggObjectTypes" + str(attributeNumber)), indexNumber)


def generate_objtype_syntax(object_type):
    # egg-object-type XXXXX
    return f"egg-object-type-{object_type.name} " + " ".join(object_type.flags)


def MP_PY_InspectEggObjectType(object_type: ObjectTypeDefinition):
    # modify the inspect/creator section to show the object type information
    pm.textField("MP_PY_OTGEN_NAMEINPUT", edit = True, text = object_type.name)
    pm.scrollField("MP_PY_OTGEN_DEFINPUT", edit = True, text = '\n'.join(object_type.flags))
    pm.scrollField("MP_PY_OTGEN_DESCINPUT", edit = True, text = '\n'.join(object_type.description))
    pm.textField("MP_PY_OTGEN_ATTRDEFTXT", edit = True, text = generate_objtype_syntax(object_type))

    print(pm.optionMenu("MP_PY_OTGEN_CATMENU", q = True, ils = True))
    idlist = pm.optionMenu("MP_PY_OTGEN_CATMENU", query = True, ils = True)
    objIndex = idlist.index(f"MP_PY_OTGEN_CATMENU_ITEM_{object_type.category.name}")
    pm.optionMenu("MP_PY_OTGEN_CATMENU", edit = True, select = objIndex + 1)
    # print(idlist[pm.optionMenu("MP_PY_OTGEN_CATMENU", query=True, select=True, value=True) - 1])
    print(f"eggu -> {object_type}")


def MP_PY_AddEggObjectTypesGUI():
    """
    Constructs and displays a GUI for adding egg-object-type tags to nodes.
    It is designed to read the contents in the global $eggObjectTypeArray and
    automatically create rows of 5 buttons each row in a separate window.
    The array can be modified in the MP_PY_Globals process to the users liking.
    User must verify that any object types added to the array are also present
    in at least one of their PRC files, otherwise egg2bam will error complaining
    about an unknown object-type.
    """

    pm.melGlobals.initVar("string[]", EGG_OBJECT_TYPE_ARRAY)

    # Delete any current instances of the AddEggObjectTypesWindow window
    if pm.window("MP_PY_AddEggObjectTypesWindow", exists = 1):
        pm.deleteUI("MP_PY_AddEggObjectTypesWindow", window = 1)

    pm.window(
        "MP_PY_AddEggObjectTypesWindow",
        retain = 1,
        sizeable = 1,
        visible = 1,
        resizeToFitChildren = True,
        title = "Panda Exporter - Add Egg-Object-Types",
    )

    # region Add OT Tags
    def createOTTagsSection():
        pm.columnLayout(adjustableColumn = True, columnAttach = ("left", 0), rowSpacing = 0)
        with pm.frameLayout(
                font = "obliqueLabelFont",
                collapsable = True,
                backgroundColor = hex_to_rgb_normalized("#809933"),
                label = "Add Egg-Object-Type Tags to Selected Nodes",
        ):

            def callback_add_ot(obj_name):
                # hack: need this function otherwise it will pass True/False
                return lambda *args: MP_PY_AddEggObjectFlags(obj_name)

            def callback_inspect_ot(obj_name):
                # hack: need this function otherwise it will pass True/False
                return lambda *args: MP_PY_InspectEggObjectType(obj_name)

            def addEggTypeTags():
                # Add Egg-Type Tags
                with pm.columnLayout(adjustableColumn = True):
                    count = 0
                    entriesPerRow = 5
                    # To find how many rows we need to allocate, we
                    # divide the total number of entries by how many per row
                    totalEntries = len(pm.melGlobals[EGG_OBJECT_TYPE_ARRAY])
                    for n in range(max(1, ceil((totalEntries / entriesPerRow)))):
                        with pm.rowLayout(nc = entriesPerRow):
                            for _ in range(entriesPerRow):
                                if count >= totalEntries:
                                    break
                                eggObjectType = pm.melGlobals[EGG_OBJECT_TYPE_ARRAY][count]
                                ot = Names2Definition[eggObjectType]
                                annotation = str(MP_PY_GetObjectTypeAnnotationNEW(ot))
                                # This is what adds new egg object type entries into the add menu.
                                # Get the defined annotation for egg-object-type
                                labelName = FriendlyNames[eggObjectType] if FriendlyNames[
                                    eggObjectType] else eggObjectType
                                pm.button(
                                    f"MP_PY_AttEggATTR_{eggObjectType}",
                                    width = 100,
                                    height = 17,
                                    command = callback_add_ot(eggObjectType),  # Pass the current objName
                                    annotation = annotation,
                                    label = labelName,
                                    backgroundColor = hex_to_rgb_normalized(ot.color)
                                )
                                count += 1
                            pm.setParent(u = 1)
                    pm.setParent(u = 1)

            def addEggTypeTagsNew():
                for category_def in CategoryDefs.values():
                    numChildren = len(category_def.children)
                    with pm.frameLayout(
                            font = "boldLabelFont",
                            collapsable = True,
                            collapse = True,
                            label = category_def.friendly_name,
                            backgroundShade = True,
                            # backgroundColor = hex_to_rgb_normalized(category_def.color),
                    ) as frame:
                        category_def.FrameLayout = frame
                        with pm.columnLayout(adjustableColumn = True):
                            for ot in category_def.get_children():
                                annotation = str(MP_PY_GetObjectTypeAnnotationNEW(ot))
                                labelName = ot.friendly_name if ot.friendly_name else ot.name
                                ot.Button = pm.button(
                                    f"MP_PY_AttEggATTR_{ot.name}",
                                    width = 100,
                                    height = 17,
                                    command = callback_add_ot(ot.name),  # Pass the current objName
                                    annotation = annotation,
                                    label = labelName,
                                    backgroundColor = hex_to_rgb_normalized(ot.color)
                                )
                                pm.popupMenu()
                                pm.menuItem(
                                    label = f"Inspect {ot.name}",
                                    command = callback_inspect_ot(ot),
                                )
                        pm.setParent(u = 1)

            addEggTypeTagsNew()
            pm.setParent(u = 1)

    createOTTagsSection()

    # endregion

    # region OT Information Label
    def createOTInformationLabel():
        pm.separator(style = "none", height = 5)
        with pm.rowLayout(nc = 2, columnAttach = (1, "both", 100),  adjustableColumn = True):
            pm.text(
                bgc = hex_to_rgb_normalized("#59D1F2"),
                label = (
                        "Object types added to nodes can be edited by selecting the node"
                        + "\n and viewing the attributes in the "
                          "channels box of the node."
                ),
            )
            pm.setParent(u = 1)
        pm.setParent(u = 1)

    createOTInformationLabel()

    # endregion

    # region Create OT Tags
    def createOTTagGeneratorSection():
        with pm.frameLayout(
                font = "obliqueLabelFont",
                collapsable = True,
                label = "OT Tag Creator",
                backgroundColor = hex_to_rgb_normalized("#30991b"),
        ):
            with pm.columnLayout(columnAttach = ("both", 15), rowSpacing = 0, adjustableColumn = True):
                with pm.rowLayout(nc = 3,adjustableColumn = True):
                    pm.text(
                        font = "smallBoldLabelFont",
                        label = "Create and define custom ObjectTypes here. Press 'CREATE' to generate.",
                    )
                    pm.separator(width = 5, style = "none")
                    pm.button(label="Reset Values")
                    pm.setParent(u = 1)

                with pm.columnLayout(rowSpacing = 0, adjustableColumn = True):
                    with pm.rowLayout(nc = 2, adjustableColumn = True, columnAttach = (1, "left", 0)):
                        pm.text(font = "smallBoldLabelFont", label = "Object Type Name")
                        # pm.separator(width = 200, style = "none")
                        pm.text(font = "smallBoldLabelFont", label = "Category")
                        pm.setParent(u = 1)
                    with pm.rowLayout(nc = 2, adjustableColumn = True, columnAttach = (1, "both", 0)):
                        otName = pm.textField("MP_PY_OTGEN_NAMEINPUT", w=200)
                        # pm.separator(width = 1, style = "none")
                        pm.optionMenu("MP_PY_OTGEN_CATMENU", w=200)
                        # pm.separator(width = 200, style = "none")
                        for category_def in CategoryDefs.values():
                            pm.menuItem(
                                f"MP_PY_OTGEN_CATMENU_ITEM_{category_def.name}",
                                label = category_def.friendly_name
                            )
                        pm.setParent(u = 1)
                    pm.setParent(u = 1)

                # TODO: make this dynamic where the user can add as many key-value pairs as they want
                def addKVs():
                    with pm.rowLayout(nc = 3, adjustableColumn = True):
                        with pm.columnLayout(rowSpacing = 0):
                            pm.text(font = "smallBoldLabelFont", label = "<Type>")
                            otType = pm.textField("MP_PY_OTGEN_TYPEINPUT")
                            pm.setParent(u = 1)
                        with pm.columnLayout(rowSpacing = 0):
                            pm.text(font = "smallBoldLabelFont", label = "key")
                            otKey = pm.textField("MP_PY_OTGEN_KEYINPUT")
                            pm.setParent(u = 1)
                        with pm.columnLayout(rowSpacing = 0):
                            pm.text(font = "smallBoldLabelFont", label = "{ value }")
                            otValue = pm.textField("MP_PY_OTGEN_VALUEINPUT")
                            pm.setParent(u = 1)
                        pm.textField(otType, edit = True, enterCommand = ('pm.setFocus(\"' + otKey + '\")'))
                        pm.textField(otKey, edit = True, enterCommand = ('pm.setFocus(\"' + otValue + '\")'))
                        pm.setParent(u = 1)

                def addOTDefPanel():
                    with pm.rowLayout(nc = 1, adjustableColumn = True):
                        with pm.columnLayout(rowSpacing = 0, adjustableColumn = True):
                            pm.text(font = "smallBoldLabelFont", label = "Object Type Definition")
                            otDef = pm.scrollField(
                                "MP_PY_OTGEN_DEFINPUT",
                                editable = True,
                                wordWrap = False,
                                text = "<Type> foo { bar }",
                                annotation = 'Define the value of this object type. Separate entries with a newline.',
                                # height=50,
                            )
                            otDef.setHeight(50)
                            # otDef.setWidth(475)
                            pm.setParent(u = 1)
                        pm.setParent(u = 1)

                addOTDefPanel()

                # region Attr Description Input
                with pm.rowLayout(nc = 1, adjustableColumn = True):
                    with pm.columnLayout(rowSpacing = 0, adjustableColumn = True):
                        pm.text(font = "smallBoldLabelFont", label = "Description")
                        otDesc = pm.scrollField(
                            "MP_PY_OTGEN_DESCINPUT",
                            editable = True,
                            wordWrap = True,
                            annotation = 'Describe the context and usage of this object type.',
                        )
                        otDesc.setHeight(50)
                        otDesc.setWidth(475)
                        pm.setParent(u = 1)
                    pm.setParent(u = 1)
                # endregion

                # region OT Definition Previewer
                with pm.rowLayout(nc = 1, adjustableColumn = True):
                    pm.text(label = "Config Entry Preview", font = "smallBoldLabelFont")
                    pm.setParent(u = 1)
                with pm.rowLayout(nc = 1, adjustableColumn = True):
                    pm.textField(
                        "MP_PY_OTGEN_ATTRDEFTXT", text = "Preview", ed = False, width = 475
                    )
                    pm.setParent(u = 1)
                # endregion

                with pm.columnLayout(adjustableColumn = True):
                    pm.button(
                        label = "CREATE!",
                        width=100,
                    )
                    pm.setParent(u = 1)

                with pm.rowLayout(nc = 6):
                    pm.separator(width = 12, style = "none")
                    pm.setParent(u = 1)
                with pm.rowLayout(nc = 8):
                    pm.setParent(u = 1)
                pm.setParent(u = 1)
            pm.setParent(u = 1)

    createOTTagGeneratorSection()

    # endregion

    # region UV Scroll Section
    def createUVScrollSection():
        UVScrollFrameHeight = 125
        pm.frameLayout(
            font = "obliqueLabelFont",
            collapsable = False,
            label = "Set Texture UV Scrolling",
            backgroundColor = hex_to_rgb_normalized("#809933"),
            height = UVScrollFrameHeight,
        )
        pm.columnLayout(columnAttach = ("left", 15), rowSpacing = 0)
        # ----- UV Scrolling
        pm.rowLayout(nc = 1)
        # ----- UV Scrolling set speed Comment
        pm.text(
            font = "smallBoldLabelFont",
            label = "Can use [float] or -[float] to set speed and direction of scrolling",
        )
        pm.setParent(u = 1)
        pm.rowLayout(nc = 6)
        # ----- UV Scrolling Labels
        pm.text(font = "smallBoldLabelFont", label = "scroll 'U(X)'")
        pm.separator(width = 5, style = "none")
        pm.text(font = "smallBoldLabelFont", label = "scroll 'V(Y)'")
        pm.separator(width = 5, style = "none")
        pm.text(font = "smallBoldLabelFont", label = "scroll 'R(Z)'")
        pm.setParent(u = 1)
        pm.rowLayout(nc = 6)
        # ----- UV Scrolling TextFields
        pm.floatField("scrollUFF", width = 40, enable = 1, nbg = False, precision = 3, value = 0)
        pm.separator(width = 12, style = "none")
        pm.floatField("scrollVFF", width = 40, enable = 1, nbg = False, precision = 3, value = 0)
        pm.separator(width = 12, style = "none")
        pm.floatField("scrollRFF", width = 40, enable = 1, nbg = False, precision = 3, value = 0)
        pm.setParent(u = 1)
        pm.rowLayout(nc = 8)
        # ----- UV Scrolling Buttons
        pm.button(
            "SetCurrentUVScroll",
            width = 80,
            height = 17,
            command = lambda *args: MP_PY_UVScrolling("set"),
            annotation = "Set or Update the scroll values of selected node.",
            label = "Set/Update",
        )
        pm.button(
            "GetCurrentUVScroll",
            width = 80,
            height = 17,
            command = lambda *args: MP_PY_UVScrolling("get"),
            annotation = "Get the current UVScroll values of the selected node.",
            label = "Get Current",
        )
        pm.button(
            "deleteCurrentUVScroll",
            width = 80,
            height = 17,
            command = lambda *args: MP_PY_UVScrolling("delete"),
            annotation = "Remove the scroll values of selected node.",
            label = "Delete",
        )
        pm.setParent(u = 1)
        pm.setParent(u = 1)
        pm.setParent(u = 1)
        pm.setParent(u = 1)

    createUVScrollSection()
    # endregion

    pm.showWindow("MP_PY_AddEggObjectTypesWindow")
    n = 0
    UVScrollFrameHeight = 125
    # Set window height: base height 10 + 19 per button row
    buttonFrameHeight = int((((n + 1) * 19) + 10))
    pm.window(
        "MP_PY_AddEggObjectTypesWindow",
        edit = 1,
        width = 515,
        height = (buttonFrameHeight + UVScrollFrameHeight),
    )


def MP_PY_UVScrolling(option):
    """
    Handles setting, getting, or deleting UV scrolling attributes for selected nodes.
    """
    # Fetch the UV scrolling values from the UI
    scroll_u = pm.floatField("scrollUFF", query = True, value = True)
    scroll_v = pm.floatField("scrollVFF", query = True, value = True)
    scroll_r = pm.floatField("scrollRFF", query = True, value = True)

    # Get selected nodes
    selected_nodes = pm.ls(selection = True)
    if not selected_nodes:
        MP_PY_ConfirmationDialog(
            "Selection Error!",
            [
                "No nodes selected.",
                "Please select at least one node and try again.",
            ],
            "ok",
        )
        return

    # Process each selected node
    for node in selected_nodes:
        scroll_attrs = {
            "scrollU": scroll_u,
            "scrollV": scroll_v,
            "scrollR": scroll_r
        }

        if option == "set":
            # Ensure scrollUV attribute exists, then set values
            if not pm.attributeQuery("scrollUV", node = node, exists = True):
                pm.addAttr(node, longName = "scrollUV", attributeType = "double3", keyable = True)
                for attr in scroll_attrs:
                    pm.addAttr(node, longName = attr, attributeType = "double", parent = "scrollUV", keyable = True)

            for attr, value in scroll_attrs.items():
                pm.setAttr(f"{node}.{attr}", value)

        elif option == "get":
            # Query existing UV scroll values and update UI
            for attr in scroll_attrs:
                if pm.attributeQuery(attr, node = node, exists = True):
                    value = pm.getAttr(f"{node}.{attr}")
                    pm.floatField(f"{attr}FF", edit = True, value = value)

        elif option == "delete":
            # Remove scrollUV attribute if it exists
            if pm.attributeQuery("scrollUV", node = node, exists = True):
                pm.deleteAttr(node, attribute = "scrollUV")
                pm.floatField("scrollUFF", edit = True, value = 0)
                pm.floatField("scrollVFF", edit = True, value = 0)
                pm.floatField("scrollRFF", edit = True, value = 0)


def MP_PY_GetEggObjectTypes():
    """
    Retrieves egg-object-types from selected nodes and passes them to the GUI
    for deletion in a user-friendly manner.
    """
    win = MassDeleteAttrWindow()
    win.create()
    win.show()


def mp_py_delete_egg_object_type(node_hierarchy, index):
    """
    Deletes a specific egg-object-type attribute from a node.

    :param node_hierarchy: The full hierarchy of the node as a string.
    :param index: The index of the egg-object-type attribute to delete.
    """
    # Resolve the full node path
    node = node_hierarchy.split("|")[-1]
    attribute_name = f"{node}.eggObjectTypes{index}"

    # Check if the attribute exists
    if pm.objExists(attribute_name):
        # Confirm deletion with the user
        confirm = MP_PY_ConfirmationDialog(
            title = "Delete Egg-Object-Type",
            message = f"Are you sure you want to delete the egg-object-type at {attribute_name}?",
            dialog_type = "yesno"
        )

        if confirm == "YES":
            # Delete the attribute
            pm.deleteAttr(attribute_name)
            print(f"Deleted {attribute_name} from {node}.")
        else:
            print("Deletion canceled.")
    else:
        # Notify the user that the attribute does not exist
        MP_PY_ConfirmationDialog(
            title = "Error",
            message = f"Attribute {attribute_name} does not exist on node {node}.",
            dialog_type = "ok"
        )


def MP_PY_ArgsBuilder(FileName):
    """
    Constructs the arguments to pass to maya2egg.
    """
    # Base arguments
    pm.melGlobals.initVar("string", MAYA_VER_SHORT)
    ARGS = f"maya2egg{pm.melGlobals[MAYA_VER_SHORT]} -v -p "

    # Checkbox flags
    checkboxes = {
        "MP_PY_ExportBfaceCB": "-bface",
        "MP_PY_ExportLegacyShadersCB": "-legacy-shaders",
        "MP_PY_ExportKeepUvsCB": "-keep-uvs",
        "MP_PY_ExportRoundUvsCB": "-round-uvs",
        "MP_PY_ExportTbnallCB": "-tbnall",
        "MP_PY_ExportLightsCB": "-convert-lights",
        "MP_PY_ExportCamerasCB": "-convert-cameras",
    }
    ARGS += " ".join(
        flag for checkbox, flag in checkboxes.items() if pm.checkBox(checkbox, query = True, value = True)) + " "

    # Export options
    export_options = {
        "MP_PY_ChooseMeshRB": "-a none",
        "MP_PY_ChooseActorRB": "-a model",
        "MP_PY_ChooseAnimationRB": "-a chan",
        "MP_PY_ChooseBothRB": "-a both",
        "MP_PY_ChoosePoseRB": "-a pose",
    }
    selected_export = pm.radioCollection("MP_PY_ExportOptionsRC", query = True, select = True)
    ARGS += f"{export_options.get(selected_export, '')} "

    # Animation frame range
    if selected_export in {"MP_PY_ChooseAnimationRB", "MP_PY_ChooseBothRB", "MP_PY_ChoosePoseRB"}:
        if pm.radioCollection("MP_PY_AnimationOptionsRC", query = True,
                              select = True) == "MP_PY_chooseCustomAnimationRangeRB":
            start_frame = pm.intField("MP_PY_AnimationStartFrameIF", query = True, value = True)
            end_frame = pm.intField("MP_PY_AnimationEndFrameIF", query = True, value = True)
            if isinstance(start_frame, int) and isinstance(end_frame, int):
                ARGS += f"-sf {start_frame} -ef {end_frame} "
            else:
                pm.mel.error("Start or End Frame entered data is invalid. Must be integers.")
                return "failed"

    # Transform modes
    transform_modes = {
        "MP_PY_ChooseTransformModelRB": "-trans model",
        "MP_PY_ChooseTransformAllRB": "-trans all",
        "MP_PY_ChooseTransformDCSRB": "-trans dcs",
        "MP_PY_ChooseTransformNoneRB": "-trans none",
    }
    selected_transform = pm.radioCollection("MP_PY_TransformModeRC", query = True, select = True)
    ARGS += f"{transform_modes.get(selected_transform, '')} "

    # Remove groundPlane_transform
    if pm.checkBox("MP_PY_RemoveGroundPlaneCB", query = True, value = True):
        ARGS += "-exclude groundPlane_transform "

    # Scene up axis and units
    ARGS += f"-cs {pm.upAxis(query = True, axis = True)}-up "
    ARGS += f"-uo {pm.optionMenu('MP_PY_UnitMenu', query = True, value = True)} "

    # Character name
    if selected_export != "MP_PY_ChooseMeshRB":
        char_name = pm.textField("MP_PY_CharacterNameTF", query = True, text = True) or FileName
        ARGS += f"-cn {char_name.replace(' ', '_')} "

    # Handle force-joint flags
    joints = pm.textField("MP_PY_ForceJointTF", query = True, text = True).split()
    for joint in joints:
        if not pm.mel.attributeExists("eggObjectTypes1", joint):
            MP_PY_AddEggObjectFlags("dcs")
            confirm_restart = MP_PY_ConfirmationDialog(
                "File Error!",
                "Added missing DCS flag to nodes. Restart export?",
                "yesno",
            )
            if confirm_restart == "yes":
                MP_PY_StartSceneExport()
                return "failed"
        ARGS += f"-force-joint {joint} "

    # Texture paths
    if pm.radioCollection("MP_PY_TexPathOptionsRC", query = True, select = True) != "MP_PY_ChooseDefaultTexPathRB":
        ARGS += "-ps rel "
        custom_tex_path = pm.textField("MP_PY_CustomEggTexPathTF", query = True, text = True)
        if custom_tex_path:
            ARGS += f'-pd "{custom_tex_path}" -pp "{custom_tex_path}" '
        custom_output_path = pm.textField("MP_PY_CustomOutputPathTF", query = True, text = True)
        if custom_output_path:
            ARGS += f'-pc "{custom_output_path}" '

    print(f"Using these arguments: {ARGS.strip()}")
    return ARGS.strip()


def MP_PY_StartSceneExport():
    """
    Prepares the scene for export:
    - Exports a temporary Maya Binary file (MB).
    - Prepares the export path and file name.
    - Executes the export process with the necessary arguments.
    """
    # Determine whether to export selected objects or the entire scene
    selection_mode = "selected" if pm.checkBox("MP_PY_ExportSelectedCB", query = True, value = True) else "all"
    temp_mb_file = MP_PY_ExportScene(selection_mode)

    if temp_mb_file == "failed":
        return 0  # Export failed

    # Retrieve original file name without extension
    orig_file_name = str(pm.mel.basenameEx(pm.cmds.file(query = True, sceneName = True)))

    # Prepare and execute the export process
    egg_file = MP_PY_ExportPrep(temp_mb_file, orig_file_name)

    return egg_file != "failed"


def MP_PY_ExportScene(selection):
    """
    Exports the entire scene or selected objects.
    """
    # Get scene details
    scene_path = str(pm.mel.dirname(pm.cmds.file(query = True, sceneName = True)))
    file_name = str(pm.mel.basenameEx(pm.cmds.file(query = True, sceneName = True)))
    temp_scene_path = ""

    # Output options
    filename_option = pm.radioCollection("MP_PY_OutputFilenameOptionsRC", query = True, select = True)
    path_option = pm.radioCollection("MP_PY_OutputPathOptionsRC", query = True, select = True)

    # Validate input based on options
    if filename_option == "MP_PY_ChooseOriginalFilenameRB":
        if path_option == "MP_PY_ChooseDefaultOutputPathRB":
            if not scene_path or not file_name:
                return handle_error(
                    "It appears you have not yet saved this scene. Please save your scene first\n"
                    "OR specify a custom output directory AND custom filename."
                )
            temp_scene_path = f"{scene_path}/{file_name}_temp.mb"

        elif path_option == "MP_PY_ChooseCustomOutputPathRB":
            custom_path = validate_text_field(
                "MP_PY_CustomOutputPathTF",
                "You have not entered a custom path.\n"
                "Please enter a custom path and try exporting again."
            )
            if not custom_path:
                return "failed"
            temp_scene_path = f"{custom_path}/{file_name}_temp.mb"

    elif filename_option == "MP_PY_ChooseCustomFilenameRB":
        custom_file_name = validate_text_field(
            "MP_PY_CustomFilenameTF",
            "You have not entered a custom file name.\n"
            "Please enter a custom name and try exporting again."
        )
        if not custom_file_name:
            return "failed"

        if path_option == "MP_PY_ChooseDefaultOutputPathRB":
            if not scene_path:
                return handle_error(
                    "It appears you have not yet saved this scene. Please save your scene first\n"
                    "OR specify a custom output directory AND custom filename."
                )
            temp_scene_path = f"{scene_path}/{custom_file_name}_temp.mb"

        elif path_option == "MP_PY_ChooseCustomOutputPathRB":
            custom_path = validate_text_field(
                "MP_PY_CustomOutputPathTF",
                "You have not entered a custom path.\n"
                "Please enter a custom path and try exporting again."
            )
            if not custom_path:
                return "failed"
            temp_scene_path = f"{custom_path}/{custom_file_name}_temp.mb"

    # Export logic
    if selection == "all":
        print("Exporting entire scene...\n")
        pm.cmds.file(temp_scene_path, exportAll = True, type = "mayaBinary", options = "v=1")
        print(f"Saved entire scene as temporary file: {temp_scene_path}\n")
    else:
        print("Exporting selected objects...\n")
        pm.cmds.file(temp_scene_path, exportSelected = True, type = "mayaBinary", options = "v=1")
        print(f"Saved selected objects as temporary file: {temp_scene_path}\n")

    return temp_scene_path


def validate_text_field(field_name, error_message):
    """
    Validates the content of a text field. If empty, displays an error dialog.
    :param field_name: Name of the text field to validate.
    :param error_message: Error message to display if validation fails.
    :return: The text content of the field if valid, None otherwise.
    """
    text = str(pm.textField(field_name, query = True, text = True))
    if not text:
        MP_PY_ConfirmationDialog("File Error!", error_message, "ok")
        return None
    return text


def handle_error(message):
    """
    Displays an error message in a confirmation dialog.
    :param message: The error message to display.
    :return: "failed" to indicate an error state.
    """
    MP_PY_ConfirmationDialog("File Error!", message, "ok")
    return "failed"


def MP_PY_GetObjectTypeAnnotationNEW(object_type: ObjectTypeDefinition):
    """
    Returns the egg-object-type button annotation text of defined types as a string for GUI.
    """
    desc = "\n".join(object_type.description)
    flags = "\n".join(object_type.flags)
    return f"{desc}\n\nFlags:\n{flags}"


def MP_PY_Globals():
    """
    Contains MP_PY_PandaVersion and egg-object-type arrays
    """
    mayaVersionLong = str(pm.mel.getApplicationVersionAsFloat())
    # get the current Maya version
    pm.melGlobals.initVar("string", MAYA_VER_SHORT)
    pm.melGlobals[MAYA_VER_SHORT] = str(
        pm.mel.substituteAllString(mayaVersionLong, ".", "")
    )
    # Strips the version zeroes if the version number length is less than 4
    if len(pm.melGlobals[MAYA_VER_SHORT]) < 4:
        pm.melGlobals[MAYA_VER_SHORT] = str(
            pm.mel.substituteAllString(pm.melGlobals[MAYA_VER_SHORT], "0", "")
        )
    # silly little hack because sometimes maya wants to say 20220 instead of 2022 -o-
    elif len(pm.melGlobals[MAYA_VER_SHORT]) > 4:
        pm.melGlobals[MAYA_VER_SHORT] = str(
            pm.melGlobals[MAYA_VER_SHORT][0:4]
        )

    pm.melGlobals.initVar("string[]", PANDA_FILE_VERSIONS)
    # Global array containing all users versioned executable file names
    """
    NOTICE REGARDING THE PANDA3D/BIN FILES:
        This notice is only pertinent if you have more than one version of Panda3D installed.
        You MUST ensure that the files being used are named differently between the different Panda3D installations.
        EXAMPLE: You have three Panda3D's of different versions installed,
            You MUST give all the egg2bam.exe, bam2egg.exe, pview.exe all different names.
            Otherwise, your computer will default to calling the file from your last installation.
            The most efficient renaming concept is to append the file names with their version at the end.
            EXAMPLE: For Panda3D-1.8.1, you might append the file [egg2bam.exe] into [egg2bam_630.exe].
            the additional '630' or more technically '6.30', is the bam file version that is created using the
            egg2bam.exe file in version Panda3D-1.8.1.
            Add anything to them that will make them easily differentiated by yourself, and of course
            this script, even simply appending the panda version, i.e. 'egg2bam_181' is fine.


    INFORMATIONAL WARNING:
        One final issue that should be resolved if more than one Panda3D version is installed:
        The 'egg2maya[version].exe', 'maya2egg[version].exe', 'maya2egg[version]_bin',
        and the dll 'libp3mayaloader[version].dll' should only be present in the
        /panda3d[version]/bin/ folder for the installation that you have used the maya plugins for.
        Otherwise, your computer may throw a fit if there are more than one of these files visible
        to the computer when they are run. The best route to take is to put all those related files
        from the Panda3D installations you won't be using into a zip archive that is placed into
        the folder the files were originally located. Doing it this way, makes the files readily
        available if you need to restore them at some point in the future.


    To add an entry into the array:
    EACH ARRAY SET INCLUDES THE FOLLOWING FOUR ITEMS:
        First entry: The name you want displayed in the option menu.
        Second entry: bam2egg file name with no file extension.
        Third entry: egg2bam file name with no file extension.
        Fourth entry: pview file name with no file extension.


    Array Entry Example: To insert a bam version of 6.30(Panda3D-1.8.1),
        First, enter a comma at the end of the previous line of four items!
        Then, you would insert into the array the next line of four items:
            (notice file extensions are NOT used!)
            example: "6.30","egg2bam_630","bam2egg_630","pview_630"
    """
    # NOTE: WHEN ENTERING IN OTHER VERSIONS, DO NOT INCLUDE THE FILE EXTENSIONS!!
    # Array Format: {"MenuDisplayText","bam2egg[version]","egg2bam[version]","pview[version]"}
    # Please leave the initial set of four entries as they are the fallback defaults used.
    pm.melGlobals[PANDA_FILE_VERSIONS] = ["Default", "bam2egg", "egg2bam", "pview"]
    # User editable egg-object-type global array.
    # NOTICE: Each egg-object-type that is added into the array MUST ALSO be referenced in a user Panda3D PRC file!!!
    #        This is necessary otherwise egg2bam will error if it cannot relate an egg-object-type.
    pm.melGlobals.initVar("string[]", EGG_OBJECT_TYPE_ARRAY)

    pm.melGlobals[EGG_OBJECT_TYPE_ARRAY] = getOTNames("category")

    # todo: maybe add option to type own number for seqX
    # Global variable that keeps track of whether user has seen the import Panda file notification.
    # It is designed so that the user only sees the notification once during session.
    pm.melGlobals.initVar("int", PANDA_SDK_NOTICE)
    pm.melGlobals[PANDA_SDK_NOTICE] = 0


def MP_PY_CreatePandaExporterWindow():
    """
    Creates the GUI control
    """
    pm.melGlobals.initVar("string[]", PANDA_FILE_VERSIONS)
    # Process Variables
    pm.melGlobals.initVar("string", MAYA_VER_SHORT)
    pm.melGlobals.initVar("string", ADDON_RELEASE_VERSION)
    # Exporter GUI Creation
    pm.window(
        "MP_PY_PandaExporter",
        sizeable = 1,
        width = 400,
        title = ("Panda Exporter " + pm.melGlobals[ADDON_RELEASE_VERSION]),
        height = 400,
        visible = 0,
        retain = 1,
    )

    # This inits the left and right cols
    pm.rowLayout(
        numberOfColumns = 2, rowAttach = [(1, "top", 0), (2, "top", 0), (3, "top", 0)]
    )
    # region  Construct LEFT Column
    with pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0):
        with pm.frameLayout(width = 200, height = 65, label = "Export File Type"):
            with pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0):
                pm.radioCollection("MP_PY_ExportOptionsRC")
                with pm.rowLayout(numberOfColumns = 3):
                    pm.radioButton(
                        "MP_PY_ChooseActorRB",
                        onCommand = lambda *args: MP_PY_ExportOptionsUI(),
                        collection = "MP_PY_ExportOptionsRC",
                        label = "Actor",
                    )
                    pm.radioButton(
                        "MP_PY_ChooseAnimationRB",
                        onCommand = lambda *args: MP_PY_ExportOptionsUI(),
                        collection = "MP_PY_ExportOptionsRC",
                        label = "Animation",
                    )
                    pm.radioButton(
                        "MP_PY_ChooseBothRB",
                        onCommand = lambda *args: MP_PY_ExportOptionsUI(),
                        collection = "MP_PY_ExportOptionsRC",
                        label = "Both",
                    )
                    pm.setParent(upLevel = 1)
                with pm.rowLayout(numberOfColumns = 2):
                    pm.radioButton(
                        "MP_PY_ChooseMeshRB",
                        onCommand = lambda *args: MP_PY_ExportOptionsUI(),
                        select = 1,
                        collection = "MP_PY_ExportOptionsRC",
                        label = "Mesh",
                    )
                    pm.radioButton(
                        "MP_PY_ChoosePoseRB",
                        onCommand = lambda *args: MP_PY_ExportOptionsUI(),
                        collection = "MP_PY_ExportOptionsRC",
                        label = "Pose",
                    )
                    pm.setParent(upLevel = 1)
                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        with pm.frameLayout(width = 200, height = 65, label = "Transforms To Save:"):
            with pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0):
                pm.radioCollection("MP_PY_TransformModeRC")
                with pm.rowLayout(numberOfColumns = 3):
                    pm.radioButton(
                        "MP_PY_ChooseTransformNoneRB",
                        onCommand = lambda *args: MP_PY_TransformModeUI(),
                        collection = "MP_PY_TransformModeRC",
                        label = "None",
                    )
                    pm.separator(width = 28, style = "none")
                    pm.radioButton(
                        "MP_PY_ChooseTransformAllRB",
                        onCommand = lambda *args: MP_PY_TransformModeUI(),
                        collection = "MP_PY_TransformModeRC",
                        label = "All",
                    )
                    pm.setParent(upLevel = 1)
                with pm.rowLayout(numberOfColumns = 3):
                    pm.radioButton(
                        "MP_PY_ChooseTransformDCSRB",
                        onCommand = lambda *args: MP_PY_TransformModeUI(),
                        collection = "MP_PY_TransformModeRC",
                        label = "DCS Flag",
                    )
                    pm.separator(width = 10, style = "none")
                    pm.radioButton(
                        "MP_PY_ChooseTransformModelRB",
                        onCommand = lambda *args: MP_PY_TransformModeUI(),
                        select = 1,
                        collection = "MP_PY_TransformModeRC",
                        label = "Model/DCS flag",
                    )
                    pm.setParent(upLevel = 1)
                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        with pm.frameLayout(width = 200, height = 215, label = "Export Options"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                pm.checkBox(
                    "MP_PY_ExportSelectedCB",
                    annotation = "Will export only the selected scene nodes",
                    value = 0,
                    label = "Export only selected objects ",
                )
                pm.checkBox(
                    "MP_PY_ExportBfaceCB",
                    annotation = (
                            "If this flag is not specified,the default is to"
                            + "\ntreat all polygons as single-sided,unless an"
                            + '\negg object type of "double-sided" is set.'
                    ),
                    value = 0,
                    label = "Double sided faces",
                )
                pm.checkBox(
                    "MP_PY_ExportOverwriteCB",
                    annotation = "Will overwrite file if it already exists",
                    value = 1,
                    label = "Overwrite existing files",
                )
                pm.checkBox(
                    "MP_PY_ExportPviewCB",
                    annotation = (
                        "When exporting, it runs the final file, e.g. egg or bam, against pview command"
                    ),
                    value = 0,
                    label = "Run PView after export",
                )
                pm.checkBox(
                    "MP_PY_ExportLegacyShadersCB",
                    annotation = (
                        "Use this flag to turn off modern (Phong) shader generation \n"
                        "and treat shaders as if they were Lamberts (legacy)"
                    ),
                    value = 0,
                    label = "Only legacy shaders",
                )
                pm.checkBox(
                    "MP_PY_ExportKeepUvsCB",
                    annotation = (
                        "Convert all UV sets on all vertices, even those that do \n"
                        "not appear to be referenced by any textures."
                    ),
                    value = 1,
                    label = "Keep all UV's",
                )
                pm.checkBox(
                    "MP_PY_ExportRoundUvsCB",
                    annotation = (
                        "Round up uv coordinates to the nearest 1/100th. i.e.\n"
                        "-0.001 becomes0.0; 0.444 becomes 0.44; 0.778 becomes 0.78"
                    ),
                    value = 1,
                    label = "Round UV's",
                )
                pm.checkBox(
                    "MP_PY_ExportTbnallCB",
                    annotation = (
                            "Compute tangent and binormal for all texture coordinate sets"
                            + '\nThis is equivalent to -tbn "*"'
                    ),
                    value = 1,
                    label = "Tangents+Binormals for all UV sets",
                )
                pm.checkBox(
                    "MP_PY_ExportLightsCB",
                    annotation = (
                        "Convert all light nodes to locators. Will preserve position and rotation"
                    ),
                    enable = 1,
                    changeCommand = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_LightsSelectedUI
                    value = 0,
                    label = "Convert Lights",
                )
                pm.checkBox(
                    "MP_PY_ExportCamerasCB",
                    annotation = (
                        "Convert all camera nodes to locators. Will preserve position and rotation"
                    ),
                    enable = 1,
                    changeCommand = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_CamerasSelectedUI
                    value = 0,
                    label = "Convert Cameras",
                )
                pm.checkBox(
                    "MP_PY_RemoveGroundPlaneCB",
                    annotation = (
                        'Removes the "groundPlane_transform" node from the exported EGG file(s).\n'
                        "Currently, this is only supported for Mesh exporting.\n\n"
                        "NOTE: Ensure the node is EMPTY before enabling this option.\n"
                        "This feature allows for the removal of an empty node from the EGG file during the maya2egg "
                        "export process."
                    ),
                    enable = 1,
                    changeCommand = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_RemoveGroundPlaneUI
                    value = 1,
                    label = "Remove groundPlane_transform",
                )
                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        with pm.frameLayout(width = 200, height = 85, label = "Bam Specific Options"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                with pm.rowLayout(numberOfColumns = 3):
                    pm.optionMenu(
                        "MP_PY_BamVersionOptionMenu",
                        width = 100,
                        annotation = (
                            "Bam file version to use for creating the bam file. "
                            "These can be added to the $gMP_PY_PandaFileVersions Array as needed"
                        ),
                    )

                    # Construct the Bam Version Option Menu
                    for i in range(0, len(pm.melGlobals[PANDA_FILE_VERSIONS])):
                        pm.menuItem(label = pm.melGlobals[PANDA_FILE_VERSIONS][i])
                        # Generate menu item
                        # Increase counter by number of units between each version entry
                        i = i + 3

                    pm.separator(width = 5, style = "none")
                    pm.text("Bam Version")
                    pm.setParent(upLevel = 1)
                # region rawtex
                with pm.rowLayout(numberOfColumns = 2):
                    pm.checkBox("MP_PY_RawtexCB", value = 0, label = "Pack Textures into Bam (-rawtex)")
                    pm.setParent(upLevel = 1)
                # endregion
                # region flatten
                with pm.rowLayout(numberOfColumns = 2):
                    pm.checkBox("MP_PY_FlattenCB", value = 0, label = "Flatten (-flatten 1)")
                    pm.setParent(upLevel = 1)
                # endregion
                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        # region convert units from
        with pm.frameLayout(width = 200, height = 50, label = "Convert Units From"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                pm.optionMenu("MP_PY_UnitMenu")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "mm")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "cm")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "m")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "km")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "in")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "ft")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "yd")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "nmi")
                pm.menuItem(collection = "MP_PY_UnitMenu", label = "mi")
                pm.optionMenu("MP_PY_UnitMenu", edit = 1, value = "cm")
                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        # endregion
        # region output filetype
        pm.frameLayout(width = 200, height = 70, label = "Output File Type:")
        pm.columnLayout(columnAttach = ("left", 0))
        pm.radioCollection("MP_PY_OutputPandaFileTypeRC")
        pm.radioButton(
            "MP_PY_ChooseEggRB",
            onCommand = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_OutputPandaFileTypeUI
            select = 1,
            collection = "MP_PY_OutputPandaFileTypeRC",
            label = "EGG (ASCII) Only",
        )
        pm.radioButton(
            "MP_PY_ChooseEggBamRB",
            onCommand = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_OutputPandaFileTypeUI
            collection = "MP_PY_OutputPandaFileTypeRC",
            label = "EGG(ASCII)   and   BAM(Binary)",
        )
        pm.setParent(upLevel = 1)
        pm.setParent(upLevel = 1)
        # endregion
        with pm.frameLayout(width = 200, height = 50, label = "Egg-Object-Types:"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                with pm.rowLayout(numberOfColumns = 2):
                    pm.button(
                        "MP_PY_AddEggTypeBTN",
                        width = 90,
                        height = 20,
                        command = lambda *args: MP_PY_AddEggObjectTypesGUI(),
                        annotation = (
                                "Displays the Egg-Object-Type window in which"
                                + "\nthe user selects tags to add to selected "
                                  "nodes."
                        ),
                        label = "Add Egg Tags",
                    )
                    pm.button(
                        "MP_PY_DeleteEggTypeBTN",
                        width = 90,
                        height = 20,
                        command = lambda *args: MP_PY_GetEggObjectTypes(),
                        annotation = (
                                "Displays an Egg-Object-Type window in which"
                                + "\nthe user can select tags to delete from "
                                  "selected nodes."
                        ),
                        label = "Delete Egg Tags",
                    )
                    pm.setParent(upLevel = 1)
                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        pm.setParent(upLevel = 1)
    # endregion

    # region Construct RIGHT Column
    with pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0):
        with pm.frameLayout(width = 270, height = 320, label = "Output Path & Name Options:"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                # region Texture path options
                pm.text(fn = "boldLabelFont", label = "Texture Path Options:")
                pm.radioCollection("MP_PY_TexPathOptionsRC")
                pm.radioButton(
                    "MP_PY_ChooseDefaultTexPathRB",
                    annotation = "Reference textures relative to maya file (default)",
                    onCommand = lambda *args: MP_PY_TexPathOptionsUI(),
                    collection = "MP_PY_TexPathOptionsRC",
                    select = 1,
                    label = "Reference textures relative to maya file (default)",
                )
                pm.radioButton(
                    "MP_PY_ChooseCustomRefPathRB",
                    onCommand = lambda *args: MP_PY_TexPathOptionsUI(),
                    annotation = (
                        "References textures relative to the specified path.\n"
                        "NOTE: If exporting both BAM and EGG files:\n"
                        "- EGG file textures are referenced relative to the Maya file.\n"
                        "- BAM file textures are referenced to the specified directory."
                    ),
                    collection = "MP_PY_TexPathOptionsRC",
                    label = "Reference textures relative to specified path",
                )
                pm.radioButton(
                    "MP_PY_ChooseCustomTexPathRB",
                    onCommand = lambda *args: MP_PY_TexPathOptionsUI(),
                    annotation = (
                        "Copies textures and makes them relative to the selected specified path.\n"
                        "NOTE: If exporting both BAM and EGG files:\n"
                        "- Textures are copied to the 'Egg File Texture Ref Directory'.\n"
                        "- The BAM file reference directory defaults to this path but can be modified.\n"
                        "- If modified, the new path MUST start with the copied-to directory path."
                    ),
                    collection = "MP_PY_TexPathOptionsRC",
                    label = "Copy textures and make relative to specified path",
                )
                pm.text(label = "Egg File Texture Ref Path:")
                with pm.rowLayout(numberOfColumns = 3, rowAttach = (1, "top", 0)):
                    pm.textField(
                        "MP_PY_CustomEggTexPathTF",
                        width = 215,
                        enable = 0,
                        annotation = (
                            "Egg File custom texture reference path.\n\n"
                            "NOTE: If using the copy-to option for textures, this will be the copied-to directory.\n"
                            "If exporting both an EGG and BAM file, the BAM file texture referencing can be further "
                            "modified below."
                        ),
                    )
                    pm.button(
                        "MP_PY_BrowseEggTexPathBTN",
                        enable = 0,
                        command = lambda *args: MP_PY_BrowseForFolderPreProcess(
                            "customRelativeEggTexturePath"
                        ),
                        annotation = (
                            "Browse for the Egg File custom texture reference path.\n\n"
                            "NOTE: If using the copy-to option for textures, this will be the copied-to directory.\n"
                            "If exporting both an EGG and BAM file, the BAM file texture referencing can be further "
                            "modified below."
                        ),
                        label = "Browse",
                    )
                    pm.setParent(u = 1)

                pm.text(label = "Bam File Texture Ref Path:")
                with pm.rowLayout(numberOfColumns = 3, rowAttach = (1, "top", 0)):
                    pm.textField(
                        "MP_PY_CustomBamTexPathTF",
                        width = 215,
                        enable = 0,
                        annotation = (
                                "Bam File custom texture reference path"
                                + "\n"
                                + "\nNOTE:"
                                + "\nIf just referencing textures and exporting both an Egg and Bam file,"
                                + "\nThe Egg file is referenced to Maya file."
                                + "\nThe Bam file will be referenced to specified path."
                                + "\nThe Bam file reference path MUST start with the path to where textures are "
                                  "located."
                                + "\n"
                                + "\nIf copying textures, this path MUST start with the copied-to directory path"
                                + '\ndefined in the "Egg file texture Ref Directory" above'
                        ),
                    )
                    pm.button(
                        "MP_PY_BrowseBamTexPathBTN",
                        enable = 0,
                        command = lambda *args: MP_PY_BrowseForFolderPreProcess(
                            "customRelativeBamTexturePath"
                        ),
                        annotation = (
                            "Browse for the BAM File custom texture reference path.\n\n"
                            "NOTE:\n"
                            "If referencing textures and exporting both an EGG and BAM file:\n"
                            "- The EGG file is referenced relative to the Maya file.\n"
                            "- The BAM file is referenced to the specified path.\n\n"
                            "If copying textures, this path MUST start with the copied-to directory path\n"
                            'defined in the "Egg file texture Ref Directory" above.'
                        ),
                        label = "Browse",
                    )
                    pm.setParent(u = 1)
                pm.separator(style = "none", height = 5)
                # endregion

                # region Output filepath options
                pm.text(fn = "boldLabelFont", label = "Output File Path:")
                pm.radioCollection("MP_PY_OutputPathOptionsRC")
                pm.radioButton(
                    "MP_PY_ChooseDefaultOutputPathRB",
                    onCommand = lambda *args: MP_PY_OutputPathOptionsUI(),
                    collection = "MP_PY_OutputPathOptionsRC",
                    select = 1,
                    label = "Export to root directory of source file (default)",
                )
                pm.radioButton(
                    "MP_PY_ChooseCustomOutputPathRB",
                    onCommand = lambda *args: MP_PY_OutputPathOptionsUI(),
                    collection = "MP_PY_OutputPathOptionsRC",
                    label = "Export to other directory:",
                )

                with pm.rowLayout(numberOfColumns = 2, rowAttach = (1, "top", 0)):
                    pm.textField("MP_PY_CustomOutputPathTF", width = 215, enable = 0)
                    pm.button(
                        "MP_PY_BrowseOutputPathBTN",
                        enable = 0,
                        command = lambda *args: MP_PY_BrowseForFolderPreProcess("customOutputPath"),
                        label = "Browse",
                    )
                    pm.setParent(u = 1)

                pm.separator(style = "none", height = 5)
                pm.text(fn = "boldLabelFont", label = "Output File Name:")
                pm.radioCollection("MP_PY_OutputFilenameOptionsRC")

                with pm.rowLayout(numberOfColumns = 2):
                    pm.radioButton(
                        "MP_PY_ChooseOriginalFilenameRB",
                        onCommand = lambda *args: MP_PY_OutputFilenameOptionsUI(),
                        collection = "MP_PY_OutputFilenameOptionsRC",
                        select = 1,
                        label = "Original filename",
                    )
                    pm.radioButton(
                        "MP_PY_ChooseCustomFilenameRB",
                        onCommand = lambda *args: MP_PY_OutputFilenameOptionsUI(),
                        collection = "MP_PY_OutputFilenameOptionsRC",
                        label = "Alternate filename",
                    )
                    pm.setParent(upLevel = 1)

                with pm.rowLayout(rowAttach = (1, "top", 0), nc = 3):
                    pm.textField(
                        "MP_PY_CustomFilenameTF",
                        text = "",
                        enable = 0,
                        annotation = "Browse to select or enter custom output file name.",
                        width = 215,
                    )
                    pm.button(
                        "MP_PY_BrowseFilenameBTN",
                        enable = 0,
                        command = lambda *args: MP_PY_BrowseForFilePreProcess("customFilename"),
                        annotation = "Browse to select or enter custom output file name.",
                        label = "Browse",
                    )
                    pm.setParent(u = 1)

                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)

        # region Animation options
        with pm.frameLayout(width = 270, height = 120, label = "Animation Options"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                with pm.rowLayout(numberOfColumns = 2):
                    pm.text(
                        "MP_PY_CharacterNameLabel",
                        enable = 0,
                        annotation = (
                                "Character name associated with Model/Animation set"
                                + "\nAny spaces will be replaced with an underscore!"
                        ),
                        label = "Character Name",
                    )
                    pm.textField(
                        "MP_PY_CharacterNameTF",
                        text = "",
                        enable = 0,
                        annotation = (
                                "Character name associated with Model/Animation set"
                                + "\nAny spaces will be replaced with an underscore!"
                        ),
                        width = 170,
                    )
                    pm.setParent(upLevel = 1)

                with pm.rowLayout(numberOfColumns = 2):
                    pm.text(
                        "MP_PY_ForceJointLabel",
                        enable = 0,
                        annotation = "Separate multiple node names with a space",
                        label = "Force Joint",
                    )
                    pm.textField(
                        "MP_PY_ForceJointTF",
                        text = "",
                        enable = 0,
                        annotation = "Separate multiple node names with a space",
                        width = 170,
                    )
                    pm.setParent(upLevel = 1)

                pm.radioCollection("MP_PY_AnimationOptionsRC")

                with pm.rowLayout(numberOfColumns = 2):
                    pm.radioButton(
                        "MP_PY_chooseFullAnimationRangeRB",
                        onCommand = lambda *args: MP_PY_AnimationOptionsUI("animationMode", ""),
                        enable = 0,
                        collection = "MP_PY_AnimationOptionsRC",
                        select = 1,
                        label = "Full Frames    ",
                    )
                    pm.radioButton(
                        "MP_PY_chooseCustomAnimationRangeRB",
                        onCommand = lambda *args: MP_PY_AnimationOptionsUI("animationMode", ""),
                        enable = 0,
                        collection = "MP_PY_AnimationOptionsRC",
                        label = "Custom Frames",
                    )
                    pm.setParent(upLevel = 1)

                with pm.rowLayout(numberOfColumns = 6):
                    pm.text(
                        "MP_PY_AnimationStartFrameLabel",
                        enable = 0,
                        annotation = ("Set the animation start frame: Default is 0" + "\nRange is 0 to 10,000"),
                        label = "Start Frame",
                    )
                    pm.intField(
                        "MP_PY_AnimationStartFrameIF",
                        enable = 0,
                        min = 0,
                        max = 10000,
                        value = 0,
                        height = 20,
                        width = 40,
                        step = 1,
                        changeCommand = lambda *args: MP_PY_AnimationOptionsUI("updateFrameValues",
                                                                               "startFrameIFChanged"),
                        annotation = "Set the animation start frame: Default is 0\nRange is 0 to 10,000",
                        noBackground = False,
                    )
                    pm.intScrollBar(
                        "MP_PY_AnimationStartFrameSlider",
                        enable = 0,
                        min = 0,
                        max = 10000,
                        value = 0,
                        height = 18,
                        width = 33,
                        step = 1,
                        dragCommand = lambda *args: MP_PY_AnimationOptionsUI(
                            "updateFrameValues", "startFrameSliderMoved"
                        ),
                        changeCommand = lambda *args: MP_PY_AnimationOptionsUI(
                            "updateFrameValues", "startFrameSliderMoved"
                        ),
                        horizontal = True,
                        annotation = "Set the animation start frame: Default is 0\nRange is 0 to 10,000",
                    )
                    pm.text(
                        "MP_PY_AnimationEndFrameLabel",
                        enable = 0,
                        annotation = "Set the animation end frame: Default is 48\nRange is 0 to 10,000",
                        label = "End Frame",
                    )
                    pm.intField(
                        "MP_PY_AnimationEndFrameIF",
                        enable = 0,
                        min = 0,
                        max = 10000,
                        value = 48,
                        height = 20,
                        width = 40,
                        step = 1,
                        changeCommand = lambda *args: MP_PY_AnimationOptionsUI("updateFrameValues",
                                                                               "endFrameIFChanged"),
                        annotation = "Set the animation end frame: Default is 48\nRange is 0 to 10,000",
                        noBackground = False,
                    )
                    pm.intScrollBar(
                        "MP_PY_AnimationEndFrameSlider",
                        enable = 0,
                        min = 0,
                        max = 10000,
                        value = 48,
                        height = 18,
                        width = 33,
                        step = 1,
                        dragCommand = lambda *args: MP_PY_AnimationOptionsUI(
                            "updateFrameValues", "endFrameSliderMoved"
                        ),
                        changeCommand = lambda *args: MP_PY_AnimationOptionsUI(
                            "updateFrameValues", "endFrameSliderMoved"
                        ),
                        horizontal = True,
                        annotation = "Set the animation end frame: Default is 48\nRange is 0 to 10,000",
                    )

                    pm.setParent(upLevel = 1)

                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        # endregion
        # region Export scene/nodes options
        with pm.frameLayout(width = 270, height = 80, label = "Export Scene or Export Nodes:"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                with pm.rowLayout(numberOfColumns = 2):
                    pm.button(
                        "MP_PY_ExportSceneBTN",
                        width = 110,
                        height = 20,
                        command = lambda *args: MP_PY_StartSceneExport(),
                        annotation = (
                            "Creates a Panda Egg file (and a BAM file if both are chosen) "
                            "by first exporting the scene as a Maya file.\n"
                            "It then runs maya2egg[version] on the Maya file using the selected export options.\n\n"
                            "If both EGG and BAM files are chosen, it will run the selected version of egg2bam on the "
                            "EGG "
                            "file, "
                            "applying the selected BAM-specific options."
                        ),
                        label = "Export Current Scene",
                    )
                    # region send to pview
                    pm.button(
                        "MP_PY_Send2PviewBTN",
                        width = 80,
                        height = 20,
                        command = lambda *args: MP_PY_Send2Pview(""),
                        annotation = (
                            "Sends either the selected nodes or the entire scene (if nothing is selected) to the "
                            "libmayapview plugin, "
                            "if it is installed and loaded.\n"
                            "If the plugin is not installed or loaded, it prompts for a file to view instead."
                        ),
                        label = "Sent To Pview",
                    )
                    pm.setParent(upLevel = 1)

                with pm.rowLayout(numberOfColumns = 3):
                    # endregion
                    # region convert nodes to panda
                    pm.button(
                        "MP_PY_ConvertNodesToPandaBTN",
                        width = 135,
                        height = 20,
                        command = lambda *args: MP_PY_ExportNodesToPandaFiles(),
                        annotation = (
                            "Converts the selected node(s) to Panda files, supporting multiple selections.\n"
                            "Each node is exported as its own set of files. "
                            "By default, this includes a Maya binary file (.mb) and an EGG file.\n"
                            "If the '[EGG(ASCII) and BAM(Binary)]' option is selected, it will generate:\n"
                            "- A Maya binary file (.mb)\n"
                            "- A BAM file (.bam)\n"
                            "- An EGG file (.egg)\n"
                            "All files are saved in the chosen output directory. "
                            "File names default to node names unless a custom name is provided."
                        ),
                        label = "Convert Nodes To Panda",
                    )
                    pm.setParent(upLevel = 1)

                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        # endregion
        # region convert files
        with pm.frameLayout(width = 270, height = 80, label = "Convert Files:"):
            with pm.columnLayout(columnAttach = ("left", 0)):
                with pm.rowLayout(numberOfColumns = 3):
                    pm.button(
                        "MP_PY_GetMayaFile2EggBTN",
                        width = 85,
                        height = 20,
                        command = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_GetMayaFile2Egg
                        annotation = (
                                "Creates a Panda Egg file by running"
                                + "\nmaya2egg[version] on the selected Maya file(s)"
                        ),
                        label = "Maya File 2 Egg",
                    )
                    pm.button(
                        "MP_PY_GetEggFile2BamBTN",
                        width = 80,
                        height = 20,
                        command = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_GetEggFile2Bam
                        annotation = (
                            "Creates a Panda Bam file by running the selected version"
                            "\nof egg2bam and the currently chosen export options"
                            "\non the selected egg file(s)."
                        ),
                        label = "Egg File 2 Bam",
                    )
                    pm.button(
                        "MP_PY_GetBamFile2EggBTN",
                        width = 80,
                        height = 20,
                        command = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_GetBamFile2Egg
                        annotation = "Runs bam2egg on the selected bam file(s)",
                        label = "Bam File 2 Egg",
                    )
                    pm.setParent(upLevel = 1)
                # endregion
                with pm.rowLayout(numberOfColumns = 3):
                    pm.button(
                        "MP_PY_ImportPandaFileBTN",
                        width = 100,
                        height = 20,
                        command = lambda *args: MP_PY_PlaceholderFunc(),  # MP_PY_ImportPandaFile
                        annotation = "Imports selected Panda Bam or Egg file(s).",
                        label = "Import Panda File",
                    )
                    pm.setParent(upLevel = 1)
                pm.setParent(upLevel = 1)
            pm.setParent(upLevel = 1)
        # endregion
        # endregion
        pm.setParent(upLevel = 1)
    # endregion

    # Go back to the top
    pm.setParent(top = 1)


pm.melGlobals.initVar("string", "gMainWindow")
pm.setParent(pm.melGlobals["gMainWindow"])

# region Delete UI elements
# Define UI elements to delete
ui_elements = {
    "MP_PY_PandaMenu": "menu",
    "MP_PY_NodesExportedToPandaFilesGUI": "window",
    "MP_PY_PandaExporter": "window",
    "MP_PY_AddEggObjectTypesWindow": "window",
    "MP_PY_DeleteEggObjectTypesWindow": "window",
}

# Delete any current instances of the UI elements
for element, ui_type in ui_elements.items():
    if ui_type == "menu" and pm.menu(element, exists = True):
        pm.deleteUI(element, menu = True)
    elif ui_type == "window" and pm.window(element, exists = True):
        pm.deleteUI(element, window = True)
# endregion


# region Init menu
# Define main menu and menu items
pm.menu("MP_PY_PandaMenu", label = "Panda3D_Python")
# Set the MP_PY_PandaMenu as the parent for the following menuItems
pm.setParent("MP_PY_PandaMenu", menu = 1)
pm.menuItem(command = lambda *args: MP_PY_PandaExporterUI(), label = "Panda Export GUI...")
pm.menuItem(command = lambda *args: MP_PY_GetFile2Pview(), label = "View file in PView...")
pm.menuItem(command = lambda *args: MP_PY_AddEggObjectTypesGUI(), label = "Add Egg-Type Attribute")
pm.menuItem(command = lambda *args: MP_PY_GotoPanda3D(), label = "Panda3D Home")
pm.menuItem(command = lambda *args: MP_PY_GotoPanda3DManual(), label = "Panda3D Manual")
pm.menuItem(command = lambda *args: MP_PY_GotoPanda3DForum(), label = "Panda3D Help Forums")
pm.menuItem(command = lambda *args: MP_PY_GotoPanda3DSDKDownload(), label = "Download Panda3D-SDK")


# endregion

def MP_PY_AnimationOptionsUI(option, to_update=""):
    """
    Updates the UI based on animation options selected.

    :param option: The action to perform (e.g., "animationMode", "updateFrameValues").
    :param to_update: Specific element to update (e.g., "startFrameIFChanged").
    """

    def enable_animation_range(enable):
        """Enable or disable animation range fields and labels."""
        pm.intField("MP_PY_AnimationStartFrameIF", edit = True, enable = enable)
        pm.intScrollBar("MP_PY_AnimationStartFrameSlider", edit = True, enable = enable)
        pm.intField("MP_PY_AnimationEndFrameIF", edit = True, enable = enable)
        pm.intScrollBar("MP_PY_AnimationEndFrameSlider", edit = True, enable = enable)
        pm.text("MP_PY_AnimationStartFrameLabel", edit = True, enable = enable)
        pm.text("MP_PY_AnimationEndFrameLabel", edit = True, enable = enable)

    if option == "animationMode":
        selected_rb = pm.radioCollection("MP_PY_AnimationOptionsRC", query = True, select = True)
        if selected_rb == "MP_PY_chooseFullAnimationRangeRB":
            print("Exporting Full Animation Range")
            enable_animation_range(False)
        elif selected_rb == "MP_PY_chooseCustomAnimationRangeRB":
            print("Exporting Custom Animation Range")
            enable_animation_range(True)
        MP_PY_GetSelectedAnimationLayerLengthUI()

    elif option == "updateFrameValues":
        element_map = {
            "startFrameIFChanged": ("MP_PY_AnimationStartFrameIF", "MP_PY_AnimationStartFrameSlider"),
            "startFrameSliderMoved": ("MP_PY_AnimationStartFrameSlider", "MP_PY_AnimationStartFrameIF"),
            "endFrameIFChanged": ("MP_PY_AnimationEndFrameIF", "MP_PY_AnimationEndFrameSlider"),
            "endFrameSliderMoved": ("MP_PY_AnimationEndFrameSlider", "MP_PY_AnimationEndFrameIF"),
        }

        if to_update in element_map:
            source, target = element_map[to_update]
            value = pm.intField(source, query = True, value = True) \
                if "IF" in source \
                else pm.intScrollBar(source, query = True, value = True)

            if "IF" in target:
                pm.intField(target, edit = True, value = value)
            else:
                pm.intScrollBar(target, edit = True, value = value)

        elif to_update == "updateAllValues":
            for source, target in element_map.values():
                value = pm.intField(source, query = True, value = True) \
                    if "IF" in source \
                    else pm.intScrollBar(source, query = True, value = True)

                if "IF" in target:
                    pm.intField(target, edit = True, value = value)
                else:
                    pm.intScrollBar(target, edit = True, value = value)


def MP_PY_GetSelectedAnimationLayerLengthUI():
    """
    Updates the 'Start Frame' and 'End Frame' UI fields based on the selected animation layer.
    Defaults to start frame 0 and end frame 48 if no keyframes are found.
    """
    # Save current selection and playback options
    current_selection = pm.ls(selection = True)
    playback_options = {
        "min": pm.playbackOptions(query = True, min = True),
        "max": pm.playbackOptions(query = True, max = True),
        "start": pm.playbackOptions(query = True, animationStartTime = True),
        "end": pm.playbackOptions(query = True, animationEndTime = True),
    }

    # Default animation layer handling
    if pm.objExists("BaseAnimation"):
        child_layers = pm.animLayer("BaseAnimation", query = True, children = True) or []
        if child_layers:
            # Find and select objects in the first selected child layer
            for layer in child_layers:
                if pm.animLayer(layer, query = True, selected = True):
                    pm.animLayer(layer, edit = True, select = True)
                    break
        else:
            pm.select(all = True, hierarchy = True)

    # Temporarily set playback range to evaluate the entire timeline
    pm.playbackOptions(edit = True, min = 0, max = 10000, animationStartTime = 0, animationEndTime = 10000)

    # Determine the last keyframe
    last_keyframe = pm.findKeyframe(which = "last")

    # Update UI fields based on keyframes
    if last_keyframe > 1:
        end_frame = last_keyframe
    else:
        end_frame = 48  # Default to 48 if no keyframes are found

    pm.intField("MP_PY_AnimationStartFrameIF", edit = True, value = 0)
    pm.intField("MP_PY_AnimationEndFrameIF", edit = True, value = end_frame)
    pm.playbackOptions(edit = True, min = 0, max = end_frame, animationStartTime = 0, animationEndTime = end_frame)

    # Restore previous selection
    pm.select(clear = True)
    if current_selection:
        pm.select(current_selection)

    # Restore playback options
    pm.playbackOptions(
        edit = True,
        min = playback_options["min"],
        max = playback_options["max"],
        animationStartTime = playback_options["start"],
        animationEndTime = playback_options["end"],
    )


def MP_PY_ExportOptionsUI():
    """
    Updates the UI based on the selected export option.
    """

    def toggle_animation_fields(enable):
        """Enable or disable animation-related fields."""
        pm.intField("MP_PY_AnimationStartFrameIF", edit = True, enable = enable)
        pm.intScrollBar("MP_PY_AnimationStartFrameSlider", edit = True, enable = enable)
        pm.intField("MP_PY_AnimationEndFrameIF", edit = True, enable = enable)
        pm.intScrollBar("MP_PY_AnimationEndFrameSlider", edit = True, enable = enable)
        pm.radioButton("MP_PY_chooseFullAnimationRangeRB", edit = True, enable = enable)
        pm.radioButton("MP_PY_chooseCustomAnimationRangeRB", edit = True, enable = enable)
        pm.text("MP_PY_CharacterNameLabel", edit = True, enable = enable)
        pm.textField("MP_PY_CharacterNameTF", edit = True, enable = enable)
        pm.text("MP_PY_ForceJointLabel", edit = True, enable = enable)
        pm.textField("MP_PY_ForceJointTF", edit = True, enable = enable)

    def toggle_general_fields(enable_lights, enable_cameras, enable_ground_plane):
        """Toggle general export options."""
        pm.checkBox("MP_PY_ExportLightsCB", edit = True, enable = enable_lights)
        pm.checkBox("MP_PY_ExportCamerasCB", edit = True, enable = enable_cameras)
        pm.checkBox("MP_PY_RemoveGroundPlaneCB", edit = True, enable = enable_ground_plane)

    # Get the selected export option
    selected_rb = pm.radioCollection("MP_PY_ExportOptionsRC", query = True, select = True)

    if selected_rb == "MP_PY_ChooseActorRB":
        print("Export as animated Actor")
        toggle_animation_fields(True)
        toggle_general_fields(False, False, False)
        pm.radioButton("MP_PY_ChooseTransformModelRB", edit = True, select = True)

    elif selected_rb == "MP_PY_ChooseAnimationRB":
        print("Export Current Actor Animation")
        toggle_animation_fields(True)
        toggle_general_fields(False, False, False)
        pm.radioButton("MP_PY_ChooseTransformModelRB", edit = True, select = True)

    elif selected_rb == "MP_PY_ChooseBothRB":
        print("Export Meshes and Animation")
        toggle_animation_fields(True)
        toggle_general_fields(False, False, False)
        pm.radioButton("MP_PY_ChooseTransformModelRB", edit = True, select = True)

    elif selected_rb == "MP_PY_ChooseMeshRB":
        print("Export as Mesh")
        toggle_animation_fields(False)
        toggle_general_fields(True, True, True)
        pm.radioButton("MP_PY_ChooseTransformModelRB", edit = True, select = True)

    elif selected_rb == "MP_PY_ChoosePoseRB":
        print("Export Selected Actor Animation Pose")
        toggle_animation_fields(True)
        toggle_general_fields(False, False, False)
        pm.radioButton("MP_PY_ChooseTransformModelRB", edit = True, select = True)

    # Update animation options and frame values
    MP_PY_AnimationOptionsUI("animationMode", "")
    MP_PY_AnimationOptionsUI("updateFrameValues", "updateAllValues")


def MP_PY_BrowseForFolderPreProcess(option):
    """
    Prepares and invokes a folder browsing dialog for various scenarios.

    :param option: Specifies the type of folder browsing operation.
    """
    # Define output file type based on the radio button selection
    output_panda_file_type = pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = True, select = True)

    if option == "customRelativeEggTexturePath":
        file_mode = 3
        caption = "Choose Texture Relative Directory For Egg File"
        folder_path = MP_PY_BrowseForFolder(file_mode, caption)
        if folder_path:
            pm.textField("MP_PY_CustomEggTexPathTF", edit = True, enable = True, text = folder_path)
            # If exporting both file types, use the same folder for Bam file texture referencing
            if output_panda_file_type == "MP_PY_ChooseEggBamRB":
                pm.textField("MP_PY_CustomBamTexPathTF", edit = True, enable = True, text = folder_path)

    elif option == "customRelativeBamTexturePath":
        file_mode = 3
        caption = "Choose Texture Relative Directory For Bam File"
        folder_path = MP_PY_BrowseForFolder(file_mode, caption)
        if folder_path:
            pm.textField("MP_PY_CustomBamTexPathTF", edit = True, enable = True, text = folder_path)

    elif option == "customOutputPath":
        file_mode = 3
        caption = "Choose Custom Output Folder"
        folder_path = MP_PY_BrowseForFolder(file_mode, caption)
        if folder_path:
            pm.radioButton("MP_PY_ChooseCustomOutputPathRB", edit = True, select = True)
            pm.button("MP_PY_BrowseOutputPathBTN", edit = True, enable = True)
            pm.textField("MP_PY_CustomOutputPathTF", edit = True, enable = True, text = folder_path)


def MP_PY_ExportPrep(work_file, file_name):
    """
    Prepares the export process, generates arguments, exports the egg file,
    and optionally converts it to a bam file or views it in Pview.

    :param work_file: Full file path and name.
    :param file_name: Base file name.
    :return: The path to the exported egg file or "failed" on error.
    """
    # Get the destination path
    dest_path = os.path.dirname(work_file) + "/"

    # Check for custom file name option
    custom_filename = pm.textField("MP_PY_CustomFilenameTF", query = True, text = True)
    if custom_filename:
        file_name = custom_filename

    # Get the custom arguments
    args = MP_PY_ArgsBuilder(file_name)
    if args == "failed":
        return "failed"

    # Export the egg file
    egg_file = MP_PY_Export2Egg(work_file, dest_path, file_name + ".egg", args)
    if egg_file == "failed":
        return "failed"

    # If output option is both Egg and Bam, run egg2bam
    selected_output_option = pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = True, select = True)
    if selected_output_option == "MP_PY_ChooseEggBamRB":
        MP_PY_Export2Bam(egg_file, 0)
    else:
        # If Pview option is selected, view the egg file
        if pm.checkBox("MP_PY_ExportPviewCB", query = True, value = True):
            MP_PY_Send2Pview(egg_file)

    return egg_file


def MP_PY_BrowseForFolder(file_mode, caption):
    """
    Displays a folder browsing dialog and returns the selected folder path.

    :param file_mode: The mode of the file dialog (e.g., directory only).
    :param caption: The title of the dialog box.
    :return: The selected folder path as a string.
    """
    folder_path = pm.fileDialog2(dialogStyle = 2, fileMode = file_mode, caption = caption)
    if folder_path:
        return folder_path[0]  # Return the first selected path
    return ""


def MP_PY_Export2Bam(egg_file, export_mode):
    """
    Converts an .egg file to a .bam file using specified options.

    :param egg_file: Path to the .egg file to be converted.
    :param export_mode: Determines the export mode:
                        0 = Normal scene exporting.
                        1 = User has chosen a specific egg file to convert.
    """
    if not egg_file:
        pm.error("Invalid egg file")

    # Extract file details
    file_name, file_extension = os.path.splitext(os.path.basename(egg_file))
    file_path = os.path.dirname(egg_file)

    # Additional options
    raw_tex = "-rawtex " if pm.checkBox("MP_PY_RawtexCB", query = True, value = True) else ""
    flatten = "-flatten 1 " if pm.checkBox("MP_PY_FlattenCB", query = True, value = True) else ""

    # Handle custom output and filename for export_mode 1
    if export_mode == 1:
        custom_filename = pm.textField("MP_PY_CustomFilenameTF", query = True, text = True)
        custom_output_path = pm.textField("MP_PY_CustomOutputPathTF", query = True, text = True)
        file_name = custom_filename or file_name
        file_path = custom_output_path or file_path

    # Texture path options
    tex_path_option = pm.radioCollection("MP_PY_TexPathOptionsRC", query = True, select = True)
    custom_bam_tex_path = pm.textField("MP_PY_CustomBamTexPathTF", query = True, text = True)
    custom_egg_tex_path = pm.textField("MP_PY_CustomEggTexPathTF", query = True, text = True)

    path_store = "-ps rel " \
        if tex_path_option in {"MP_PY_ChooseCustomRefPathRB", "MP_PY_ChooseCustomTexPathRB"} \
        else ""

    path_directory = f"-pd \"{custom_bam_tex_path or custom_egg_tex_path or file_path}\" " \
        if tex_path_option != "MP_PY_ChooseDefaultTexPathRB" \
        else ""

    target_directory = f"-pc \"{custom_bam_tex_path or custom_egg_tex_path or file_path}\" " \
        if tex_path_option == "MP_PY_ChooseCustomTexPathRB" \
        else ""

    dirname = f"-pp \"{file_path}\" " \
        if tex_path_option != "MP_PY_ChooseDefaultTexPathRB" \
        else ""

    # Define the .bam file path
    bam_file = os.path.join(file_path, f"{file_name}.bam")
    print(f"Converting: {egg_file}")
    print(f"Output BAM file: {bam_file}")

    # Get the appropriate egg2bam version
    egg2bam = MP_PY_PandaVersion("getEgg2Bam")

    # Overwrite mode
    overwrite = pm.checkBox("MP_PY_ExportOverwriteCB", query = True, value = True)
    overwrite_flag = "-o " if overwrite else ""

    # Construct the command
    cmd = (
        f"{egg2bam} {raw_tex}{flatten}{path_store}{path_directory}"
        f"{target_directory}{dirname}"
        f"{overwrite_flag}\"{bam_file}\" \"{egg_file}\""
    )
    # Execute the command
    result = os.system(cmd)
    print(f"Command executed:\n{cmd}")

    # Run Pview if selected
    if pm.checkBox("MP_PY_ExportPviewCB", query = True, value = True):
        MP_PY_Send2Pview(bam_file)

    print(f"Conversion complete: .egg -> .bam\nUnit: {pm.optionMenu('MP_PY_UnitMenu', query = True, value = True)}")


def MP_PY_Send2Pview(file_path=""):
    """
    Sends the specified file to Pview or uses the Pview plugin for Maya to preview the scene.

    :param file_path: The file to preview. If empty, uses Maya's Pview plugin to preview the scene.
    """
    # Process Variables
    maya_version_short = pm.melGlobals[MAYA_VER_SHORT]

    if not file_path:
        # No file provided, use Pview plugin for the scene
        plugin_name = f"libmayapview{maya_version_short}"

        if pm.pluginInfo(plugin_name, query = True, loaded = True):
            # Check if viewing the whole scene or selected nodes
            if pm.checkBox("MP_PY_ExportSelectedCB", query = True, value = True):
                print("\nStarting Pview for selected nodes...\n")
                pm.mel.pview()
                print("End Pview\n")
            else:
                pm.select(clear = True)
                print("\nStarting Pview for the entire scene...\n")
                pm.mel.pview()
                print("End Pview\n")

        # Check for an alternate Pview plugin and prompt user for a file
        plugin_name_save = f"libmayasavepview{maya_version_short}"
        if pm.pluginInfo(plugin_name_save, query = True, loaded = True):
            print("Pview plugin requires a saved scene. Prompting user to choose a file...")
            MP_PY_GetFile2Pview()

    else:
        # A file is provided; use the external Pview executable
        pview_executable = MP_PY_PandaVersion("getPview")
        print("\nStarting Pview for file...\n")
        print(f"File: {file_path}\n")

        # Execute the Pview command
        cmd = f"{pview_executable} -l -c \"{file_path}\""
        result = os.system(cmd)

        print(f"{result}\n")
        print("End Pview\n")


def MP_PY_Export2Egg(mb_file, dest_path, dest_filename, args):
    """
    Exports a Maya binary file to an egg file using the specified arguments.

    :param mb_file: The path to the Maya binary (.mb) file.
    :param dest_path: The destination directory for the .egg file.
    :param dest_filename: The name of the destination .egg file.
    :param args: The arguments to be passed to the maya2egg export command.
    :return: The path to the exported .egg file, or "failed" if the export fails.
    """
    # Validate Maya binary file
    if not mb_file:
        pm.error("Not a valid Maya Binary file.")
        return "failed"

    # Define the full path for the .egg file
    egg_file = os.path.join(dest_path, dest_filename)

    print(f"Your scene will be saved as this egg file: {dest_filename}")
    print(f"In this directory: {dest_path}")

    # Check if overwriting is enabled
    overwrite = pm.checkBox("MP_PY_ExportOverwriteCB", query = True, value = True)

    # Construct the system command
    if overwrite:
        print("!!Overwrite enabled!!")
        cmd = f"{args} -o \"{egg_file}\" \"{mb_file}\""
    else:
        cmd = f"{args} \"{mb_file}\" \"{egg_file}\""

    # Execute the command
    # Notice: cmd is a string, be careful with any spaces in the path.
    start_time = time.time()
    result = os.system(cmd)
    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time} seconds")

    print(f"Finished exporting (.mb -> .egg), unit: {pm.optionMenu('MP_PY_UnitMenu', query = True, value = True)}")
    return egg_file


def MP_PY_GetFile2Pview():
    """
    Allows the user to choose a .egg or .bam file and sends it to Pview.
    """
    # Get the Pview executable version
    pview_executable = MP_PY_PandaVersion("getPview")

    # Get the starting directory (directory of the current Maya scene)
    starting_directory = os.path.dirname(pm.sceneName()) if pm.sceneName() else os.getcwd()

    # Set up file browsing options
    file_mode = 1  # A single existing file
    caption = "Select Panda file to Pview..."
    file_filter = "Panda Egg (*.egg);;Panda Bam (*.bam)"

    # Prompt the user to select a file
    pview_file = pm.fileDialog2(
        dialogStyle = 2,
        fileMode = file_mode,
        startingDirectory = starting_directory,
        caption = caption,
        fileFilter = file_filter,
    )

    # If a file is selected, send it to Pview
    if pview_file and len(pview_file) == 1:
        MP_PY_Send2Pview(pview_file[0])
    else:
        pm.error("No file selected!\n")


def MP_PY_ExportNodesToPandaFiles():
    """
    Converts the selected nodes in a Maya scene to Panda3D-compatible files.
    Supports exporting multiple nodes to individual files with user-defined options.
    """
    # Get the export directory path
    dest_path = pm.textField("MP_PY_CustomOutputPathTF", query = True, text = True)
    selected_nodes = pm.ls(selection = True, long = True)
    selected_nodes.sort()

    if not selected_nodes:
        MP_PY_ConfirmationDialog("Selection Error!", "You must select at least one(1) node to export.", "ok")
        return

    if not dest_path:
        output_directory_error = MP_PY_ConfirmationDialog(
            "Output Directory ERROR!",
            [
                "You must select a directory where the exported files will go.",
                "Click \"Choose Directory\" to select the directory and continue",
                "or click \"Cancel\" to exit process."
            ],
            "selectcancel"
        )
        if output_directory_error == "SELECT":
            pm.radioButton("MP_PY_ChooseCustomOutputPathRB", edit = True, select = True)
            MP_PY_BrowseForFolderPreProcess("customOutputPath")
            MP_PY_ExportNodesToPandaFiles()
        return

    # Ensure the destination path ends with a slash
    dest_path = os.path.join(dest_path, "")

    # Variables for tracking progress and results
    nodes_to_panda_files = []
    files_exported = 0
    number_of_selected_nodes = len(selected_nodes)

    # Initialize Maya progress bar
    g_main_progress_bar = pm.melGlobals["gMainProgressBar"]
    pm.progressBar(
        g_main_progress_bar,
        edit = True,
        beginProgress = True,
        isInterruptable = True,
        minValue = 0,
        maxValue = number_of_selected_nodes,
    )

    # Loop through selected nodes and export each
    for this_file_number, node in enumerate(selected_nodes, start = 1):
        if pm.progressBar(g_main_progress_bar, query = True, isCancelled = True):
            break

        # Update progress bar
        pm.progressBar(
            g_main_progress_bar,
            edit = True,
            step = 1,
            status = f"Exporting selected node... {this_file_number} of Nodes: {number_of_selected_nodes}",
        )

        # Extract the node's name and construct file names
        node_name = node.split("|")[-1]
        maya_file_name = f"{node_name}.mb"
        temp_mb_file = os.path.join(dest_path, maya_file_name)

        # Export the node as a Maya binary file
        pm.select(node, replace = True)
        pm.cmds.file(temp_mb_file, op = "v=1", typ = "mayaBinary", exportSelected = True, force = True)
        # Add Maya file info to results
        nodes_to_panda_files.append((maya_file_name, dest_path))

        # Define egg file name
        file_name = os.path.splitext(maya_file_name)[0]
        dest_filename = f"{file_name}.egg"

        # Build arguments for exporting
        args = MP_PY_ArgsBuilder(file_name)

        # Export the egg file
        if pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = True, select = True) == "MP_PY_ChooseEggRB":
            egg_file = MP_PY_Export2Egg(temp_mb_file, dest_path, dest_filename, args)
            nodes_to_panda_files.append((dest_filename, dest_path))
            files_exported += 1
        elif pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = True, select = True) == "MP_PY_ChooseEggBamRB":
            # Export egg and bam files
            egg_file = MP_PY_Export2Egg(temp_mb_file, dest_path, dest_filename, args)
            nodes_to_panda_files.append((dest_filename, dest_path))

            # Convert the egg file to a bam file
            MP_PY_Export2Bam(egg_file, 0)
            bam_file_name = f"{file_name}.bam"
            nodes_to_panda_files.append((bam_file_name, dest_path))
            files_exported += 1

    # End progress bar
    pm.progressBar(g_main_progress_bar, edit = True, endProgress = True)

    # Show results if files were exported
    if files_exported > 0 and nodes_to_panda_files:
        MP_PY_NodesExportedAsPandaFilesGUI(nodes_to_panda_files)


def MP_PY_NodesExportedAsPandaFilesGUI(nodes_to_panda_files):
    """
    Displays a window listing all nodes that were exported as Panda files.
    Shows the file names and their export locations as a reference for the user.

    :param nodes_to_panda_files: List of tuples with (file_name, file_path).
    """
    # Delete the window if it already exists
    if pm.window("MP_PY_NodesExportedToPandaFilesGUI", exists = True):
        pm.deleteUI("MP_PY_NodesExportedToPandaFilesGUI", window = True)

    if not nodes_to_panda_files:
        MP_PY_ConfirmationDialog("Data Error!", "There is currently no exported files in the array.", "ok")
        return

    # Create the window
    window = pm.window(
        "MP_PY_NodesExportedToPandaFilesGUI",
        sizeable = False,
        width = 600,
        height = 200,
        title = "...Listing of Exported nodes to Panda Files...",
        toolbox = True,
        titleBarMenu = True,
    )
    with pm.columnLayout(columnAttach = ("left", 0), adjustableColumn = True, rowSpacing = 0):
        scroll_field = pm.scrollField(
            wordWrap = False,
            editable = False,
            width = 600,
            height = 200,
        )

    # Show the window
    pm.showWindow(window)
    pm.window("MP_PY_NodesExportedToPandaFilesGUI", edit = True, width = 600, height = 200)

    # Populate the scroll field with exported files and paths
    for i in range(0, len(nodes_to_panda_files), 2):
        file_name = nodes_to_panda_files[i]
        file_path = nodes_to_panda_files[i + 1]
        pm.scrollField(scroll_field, edit = True, insertText = f"{file_name} : {file_path}\n")


def MP_PY_BrowseForFilePreProcess(option):
    """
    Prepares and invokes a file browsing dialog for various scenarios and updates UI elements.

    :param option: Specifies the type of file browsing operation.
    """
    # currently only supports customFilename
    if option != "customFilename":
        return
    # File dialog configuration
    file_mode = 0  # Any file, whether it exists or not
    caption = "Select file name to save as"
    file_filter = "Panda Egg (*.egg);;All Files (*.*)"
    starting_directory = os.path.dirname(pm.sceneName()) if pm.sceneName() else os.getcwd()

    # Open file dialog
    custom_file = pm.fileDialog2(
        dialogStyle = 2,
        fileMode = file_mode,
        caption = caption,
        fileFilter = file_filter,
        startingDirectory = starting_directory,
    )

    if custom_file and len(custom_file) > 0:
        # Extract file name and directory
        file_name = os.path.splitext(os.path.basename(custom_file[0]))[0]
        directory_name = os.path.dirname(custom_file[0])

        # Update UI elements
        pm.textField("MP_PY_CustomFilenameTF", edit = True, enable = True, text = file_name)
        pm.radioButton("MP_PY_ChooseCustomOutputPathRB", edit = True, select = True)
        pm.textField("MP_PY_CustomOutputPathTF", edit = True, enable = True, text = directory_name)


class MassDeleteAttrWindow(object):
    # Borrowed from https://forums.cgsociety.org/t/delete-multiple-attributes/1848055/2
    def __init__(self):
        self.window = 'massDeleteAttrWin'
        self.title = 'Mass Delete Attributes'
        self.size = (600, 800)

    def create(self):
        if pm.window(self.window, exists = True):
            pm.deleteUI(self.window, window = True)

        self.window = pm.window(
            self.window,
            title = self.title,
            widthHeight = self.size
        )

        self.mainForm = pm.paneLayout(configuration = 'horizontal3', ps = ((1, 100, 80), (2, 100, 10)))
        self.uiList = pm.textScrollList(allowMultiSelection = True)
        self.btnDelete = pm.button(label = 'Delete!', command = partial(self.doDelete))
        self.btnRefresh = pm.button(label = 'Refresh Selection', command = partial(self.doRefresh))

    def getSelection(self):
        self.selection = pm.ls(selection = True)
        if not self.selection:
            self.selection = pm.ls(transforms = True, shapes = True)

    def listCustomAttrs(self):
        # todo: Also list the value of the attr (instead of just eggObjectType1 or whatever)
        attrs = []
        for node in self.selection:
            customAttrs = node.listAttr(userDefined = True)
            if customAttrs:
                attrs.extend([attr.attrName() for attr in customAttrs])
        return sorted(list(set(attrs)))

    def doDelete(self, *args):
        attrs = self.uiList.getSelectItem()
        if not attrs:
            return

        for node in self.selection:
            for attr in attrs:
                if node.hasAttr(attr):
                    node.deleteAttr(attr)

        for attr in attrs:
            self.uiList.removeItem(attr)

    def doRefresh(self, *args):
        self.getSelection()
        self.uiList.removeAll()
        self.uiList.append(self.listCustomAttrs())

    def show(self):
        pm.showWindow(self.window)
        self.doRefresh()


# The following processes define the functions called by using the menu items


def MP_PY_GotoPanda3D():
    pm.showHelp("http://www.panda3d.org", absolute = 1)


def MP_PY_GotoPanda3DManual():
    pm.showHelp("http://www.panda3d.org/manual/index.php/Main_Page", absolute = 1)


def MP_PY_GotoPanda3DForum():
    pm.showHelp("https://www.panda3d.org/forums/index.php", absolute = 1)


def MP_PY_GotoPanda3DSDKDownload():
    pm.showHelp("http://www.panda3d.org/download.php?sdk", absolute = 1)


def MP_PY_PandaExporterUI():
    """Displays the exporter GUI if it has already been created
    Otherwise, it creates the GUI window, then displays it"""

    if pm.window("MP_PY_PandaExporter", exists = 1) == 0:
        MP_PY_CreatePandaExporterWindow()
        pm.showWindow("MP_PY_PandaExporter")
    else:
        pm.showWindow("MP_PY_PandaExporter")


# End of main
# endregion


MP_PY_Globals()
# Variable to hold our release revision
pm.melGlobals.initVar("string", ADDON_RELEASE_VERSION)
pm.melGlobals[ADDON_RELEASE_VERSION] = "v1.9"
# Call the GUI creation process
MP_PY_CreatePandaExporterWindow()
