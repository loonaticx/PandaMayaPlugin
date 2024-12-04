import pymel.core as pm
import os

# region GLOBALS
EGG_OBJECT_TYPE_ARRAY = "gMP_PY_EggObjectTypeArray"
PANDA_FILE_VERSIONS = "gMP_PY_PandaFileVersions"
ADDON_RELEASE_VERSION = "gMP_PY_ReleaseRevision"
# endregion

OT_ENTRIES = {
    "barrier": (
        "<Collide> { Polyset descend }"
        "\n\nCreates a barrier that other objects cannot pass through."
        '\nThe collision is active on the "Normals" side of the object(s)'
    ),
    "barrier-no-mask": "<Collide> { Polyset descend }",
    "floor": (
        "<Scalar> collide-mask { 0x02 }"
        "\n<Collide> { Polyset descend level }"
        "\n\nCreates a collision from the object(s) that 'Avatars' can walk on."
        "\nIf the surface is angled, the Avatar will not slide down it."
        '\nThe collision is active on the "Normals" side of the object(s)'
    ),
    "floor-collide": "<Scalar> collide-mask { 0x06 }",
    "shadow": (
        "<Scalar> bin { shadow } <Scalar> alpha { blend-no-occlude }"
        '\n\nDefine a "shadow" object type, so we can render all shadows in '
        "their own bin and have them not fight with each other (or with other "
        "transparent geometry)."
    ),
    "shadow-cast": (
        "<Tag> cam { shground }"
        "\n<Scalar> draw-order { 0 }"
        "\n<Scalar> bin { ground }"
        "\n\nGives the selected object(s) the required attributes so that an "
        '"Avatar\'s" shadow can be cast over it. Commonly used for casting an '
        '"Avatar\'s" shadow onto floors.'
    ),
    "dupefloor": (
        "<Collide> { Polyset keep descend level }"
        "\n\nThis type first creates a duplicate of the selected object(s)."
        "\nThen, creates a floor collision from the duplicate object(s) that "
        '"Avatars" can walk on.'
        "\nIf the surface is angled, the Avatar will not slide down it."
        '\nThe collision is active on the "Normals" side of the object(s)'
    ),
    "smooth-floors": (
        "<Collide> { Polyset descend }"
        "\n<Scalar> from-collide-mask { 0x000fffff }"
        "\n<Scalar> into-collide-mask { 0x00000002 }"
        '\n\nMakes floors smooth for the "Avatars" to walk and stand on.'
    ),
    "camera-collide": (
        "<Scalar> collide-mask { 0x04 }"
        "\n<Collide> { Polyset descend }"
        "\n\nAllows only the camera to collide with the geometry."
    ),
    "sphere": (
        "<Collide> { Sphere descend }"
        '\n\nCreates a "minimum-sized" sphere collision around the selected '
        "object(s), that other objects cannot enter into."
    ),
    "tube": (
        "<Collide> { Tube descend }"
        '\n\nCreates a "minimum-sized" tube collision around the selected '
        "object(s), that other objects cannot enter into."
    ),
    "trigger": (
        "<Collide> { Polyset descend intangible }"
        "\n\nCreates a collision that can be used as a 'Trigger', which can be "
        "used to activate, or deactivate, specific processes."
        '\nThe collision is active on the "Normals" side of the object(s)'
    ),
    "trigger-sphere": (
        "<Collide> { Sphere descend intangible }"
        '\n\nCreates a "minimum-sized" sphere collision that can be used as a '
        '"Trigger", which can be used to activate, or deactivate, specific processes.'
        '\nThe collision is active on the "Normals" side of the object(s)'
    ),
    "invsphere": (
        "<Collide> { InvSphere descend }"
        '\n\nCreates a "minimum-sized" inverse-sphere collision around the '
        "selected object(s). Any object inside the sphere will be prevented from "
        "exiting the sphere."
    ),
    "bubble": (
        "<Collide> { Sphere keep descend }"
        '\n\n"bubble" puts a Sphere collision around the geometry, but does not '
        "otherwise remove the geometry."
    ),
    "dual": (
        "<Scalar> alpha { dual }"
        "\n\nNormally attached to polygons that have transparency, that are in "
        "the scene by themselves, such as a Tree or Flower."
    ),
    "multisample": "<Scalar> alpha { ms }",
    "blend": "<Scalar> alpha { blend }",
    "decal": "<Scalar> decal { 1 }",
    "ghost": (
        "<Scalar> collide-mask { 0 }"
        '\n\n"ghost" turns off the normal collide bit that is set on visible '
        "geometry by default, so that if you are using visible geometry for "
        "collisions, this particular geometry will not be part of those collisions--"
        "it is ghostlike. Characters will pass through it."
    ),
    "glass": "<Scalar> alpha { blend_no_occlude }",
    "glow": (
        "<Scalar> blend { add }"
        '\n\n"glow" is useful for halo effects and things of that ilk. It renders '
        "the object in add mode instead of the normal opaque mode."
    ),
    "binary": (
        "<Scalar> alpha { binary }"
        "\n\nThis mode of alpha sets transparency pixels to either on or off. No "
        "blending is used."
    ),
    "indexed": "<Scalar> indexed { 1 }",
    "model": (
        "<Model> { 1 }"
        "\n\nThis creates a ModelNode at the corresponding level, which is "
        "guaranteed not to be removed by any flatten operation. However, its "
        "transform might still be changed."
    ),
    "dcs": (
        "<DCS> { 1 }"
        "\n\nIndicates the node should not be flattened out of the hierarchy during "
        "conversion. The node's transform is important and should be preserved."
    ),
    "netdcs": "<DCS> { Net }",
    "localdcs": "<DCS> { Local }",
    "notouch": (
        "<DCS> { no-touch }"
        "\n\nIndicates the node, and below, should not be flattened out of the "
        "hierarchy during the conversion process."
    ),
    "double-sided": (
        "<BFace> { 1 }"
        "\n\nDefines whether the polygon will be rendered double-sided (i.e., its "
        "back face will be visible)."
    ),
    "billboard": (
        "<Billboard> { axis }"
        "\n\nRotates the geometry to always face the camera. Geometry will rotate "
        "on its local axis."
    ),
    "seq2": (
        "<Switch> { 1 }"
        "\n<Scalar> fps { 2 }"
        "\n\nIndicates a series of animation frames that should be consecutively "
        "displayed at 2 fps."
    ),
    "seq4": (
        "<Switch> { 1 }"
        "\n<Scalar> fps { 4 }"
        "\n\nIndicates a series of animation frames that should be consecutively "
        "displayed at 4 fps."
    ),
    "seq6": (
        "<Switch> { 1 }"
        "\n<Scalar> fps { 6 }"
        "\n\nIndicates a series of animation frames that should be consecutively "
        "displayed at 6 fps."
    ),
    "seq8": (
        "<Switch> { 1 }"
        "\n<Scalar> fps { 8 }"
        "\n\nIndicates a series of animation frames that should be consecutively "
        "displayed at 8 fps."
    ),
    "seq10": (
        "<Switch> { 1 }"
        "\n<Scalar> fps { 10 }"
        "\n\nIndicates a series of animation frames that should be consecutively "
        "displayed at 10 fps."
    ),
    "seq12": (
        "<Switch> { 1 }"
        "\n<Scalar> fps { 12 }"
        "\n\nIndicates a series of animation frames that should be consecutively "
        "displayed at 12 fps."
    ),
    "seq24": (
        "<Switch> { 1 }"
        "\n<Scalar> fps { 24 }"
        "\n\nIndicates a series of animation frames that should be consecutively "
        "displayed at 24 fps."
    ),
    "ground": (
        ""
    ),
    "invisible": "",
    "catch-grab": "",
    "pie": "",
    "safety-gate": "",
    "safety-net": "",
    "draw1": "",
    "draw0": "",
    "shground": "",
    "camtransbarrier": "",
    "camtransparent": "",
    "cambarrier-sphere": "",
    "camera-barrier": "",
    "camera-collide-sphere": "",
    "backstage": "",
}


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
    selectedBamVersion = str(
        pm.optionMenu("MP_PY_BamVersionOptionMenu", query = 1, value = 1)
    )
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


def MP_PY_ConfirmationDialog(title, message, type):
    """
    Shows a confirmation dialog with the passed title and message to the user.

    :returns: the value of the button that was pressed by user.
    """
    confirmValue = ""

    # Displays only an 'OK' button to user
    if type == "ok":
        confirmValue = str(
            pm.confirmDialog(
                title = title,
                cancelButton = "CANCEL",
                defaultButton = "OK",
                button = "OK",
                message = message,
                dismissString = "CANCEL",
            )
        )

    # Displays an 'OK' and 'CANCEL' button to user
    elif type == "okcancel":
        confirmValue = str(
            pm.confirmDialog(
                title = title,
                cancelButton = "CANCEL",
                defaultButton = "OK",
                button = ["OK", "CANCEL"],
                message = message,
                dismissString = "CANCEL",
            )
        )

    # Displays an 'SELECT' and 'CANCEL' button to user
    elif type == "selectcancel":
        confirmValue = str(
            pm.confirmDialog(
                title = title,
                cancelButton = "CANCEL",
                defaultButton = "SELECT",
                button = ["SELECT", "CANCEL"],
                message = message,
                dismissString = "CANCEL",
            )
        )

    elif type == "yesno":
        confirmValue = str(
            pm.confirmDialog(
                title = title,
                cancelButton = "NO",
                defaultButton = "YES",
                button = ["YES", "NO"],
                message = message,
                dismissString = "NO",
            )
        )
    # Displays a 'YES' and 'NO' button to user

    elif type == "downloadcancel":
        confirmValue = str(
            pm.confirmDialog(
                title = title,
                cancelButton = "CANCEL",
                defaultButton = "DOWNLOAD",
                button = ["DOWNLOAD", "CANCEL"],
                message = message,
                dismissString = "CANCEL",
            )
        )
    # Displays a 'Download' and 'Cancel' button to user

    return confirmValue


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
        # This is necessary so we can verify the index number is not null/empty
        # Get the array index number of the $eggObjectType passed to this process
        # by iterating through each array item and compare them to the $eggObjectType
        for n in range(0, len(pm.melGlobals[EGG_OBJECT_TYPE_ARRAY])):
            if pm.melGlobals[EGG_OBJECT_TYPE_ARRAY][n] == eggObjectType:
                indexNumber = int(n)

        selectedNodes = pm.ls(sl = 1)
        # Variable to hold all currently selected nodes
        # Iterate through each selected node one-by-one
        if len(selectedNodes) == 0:
            MP_PY_ConfirmationDialog(
                "Selection Error!",
                "You must first make a selection!"
                + "\nPlease select at least one node, "
                  "then try again.",
                "ok",
            )
            return

        for node in selectedNodes:
            for i in range(1, 11):
                if pm.objExists(str(node) + ".eggObjectTypes" + str(i)) == 1:
                    if i == 10:
                        MP_PY_ConfirmationDialog(
                            "Egg-Object-Type Error!",
                            "Limit of 10 egg-object-types has already been reached."
                            + "\nNo More Egg Object Types Supported for this node.",
                            "ok",
                        )
                    # Notify user if the lmit of 3 tags are already assigned to node
                    # Message to user that the egg-object-type limit has been reached
                else:
                    MP_PY_SetEggObjectTypeAttribute(
                        enumerationList, eggObjectType, indexNumber, i, node
                    )
                    # Call subprocess to check/set attribute
                    # Set variable to exit loop
                    break
    else:
        MP_PY_ConfirmationDialog(
            "Egg-Object-Type Error!",
            "The selected egg-object-type was not found in the $gMP_PY_EggObjectTypeArray"
            + "\n"
            + "\nPlease verify the object-type being passed and update the $gMP_PY_EggObjectTypeArray"
            + "\nto include the egg-object-type if the type is the correct one needed."
            + "\n\nIf you modify the $gMP_PY_EggObjectTypeArray DO NOT forget to update your PRC files."
            + "\nto include a reference of the egg-object-type you are adding.",
            "ok",
        )
    # Message to user that the passed egg-object-type is NOT in the $gMP_PY_EggObjectTypeArray array

    if pm.window("MP_PY_DeleteEggObjectTypesWindow", exists = 1):
        MP_PY_GetEggObjectTypes()
    # Method to update the DeleteEggObjectTypesWindow window if it is currently being shown


def MP_PY_TexPathOptionsUI():
    """
    Updates the UI when a radio button is chosen
    """
    selectedRB = str(pm.radioCollection("MP_PY_TexPathOptionsRC", query = 1, select = 1))
    outputPandaFileType = str(
        pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = 1, select = 1)
    )
    if selectedRB == "MP_PY_ChooseDefaultTexPathRB":
        print("Default Texture Path Chosen\n")

        pm.textField("MP_PY_CustomEggTexPathTF", edit = 1, text = "", enable = 0)

        pm.button("MP_PY_BrowseEggTexPathBTN", edit = 1, enable = 0)

        pm.textField("MP_PY_CustomBamTexPathTF", edit = 1, text = "", enable = 0)

        pm.button("MP_PY_BrowseBamTexPathBTN", edit = 1, enable = 0)

    elif selectedRB == "MP_PY_ChooseCustomRefPathRB":
        print("Custom Texture Reference Path Chosen\n")
        # Set options based on file type

        if outputPandaFileType == "MP_PY_ChooseEggRB":
            pm.textField("MP_PY_CustomBamTexPathTF", edit = 1, text = "", enable = 0)
            # Disable bam file options
            pm.button("MP_PY_BrowseBamTexPathBTN", edit = 1, enable = 0)
            # Enable egg file options
            pm.textField("MP_PY_CustomEggTexPathTF", edit = 1, enable = 1)
            pm.button("MP_PY_BrowseEggTexPathBTN", edit = 1, enable = 1)

        elif outputPandaFileType == "MP_PY_ChooseEggBamRB":
            pm.textField("MP_PY_CustomBamTexPathTF", edit = 1, enable = 1)
            # Enable bam file options
            pm.button("MP_PY_BrowseBamTexPathBTN", edit = 1, enable = 1)
            # Disable egg file options
            pm.textField("MP_PY_CustomEggTexPathTF", edit = 1, text = "", enable = 0)
            pm.button("MP_PY_BrowseEggTexPathBTN", edit = 1, enable = 0)

    elif selectedRB == "MP_PY_ChooseCustomTexPathRB":
        print("Custom Texture Path Chosen\n")
        # Set options based on file type

        if outputPandaFileType == "MP_PY_ChooseEggRB":
            pm.textField("MP_PY_CustomBamTexPathTF", edit = 1, text = "", enable = 0)
            # Disable bam file options

            pm.button("MP_PY_BrowseBamTexPathBTN", edit = 1, enable = 0)
            # Enable egg file options

            pm.textField("MP_PY_CustomEggTexPathTF", edit = 1, enable = 1)

            pm.button("MP_PY_BrowseEggTexPathBTN", edit = 1, enable = 1)

        elif outputPandaFileType == "MP_PY_ChooseEggBamRB":
            pm.textField("MP_PY_CustomBamTexPathTF", edit = 1, enable = 1)
            # Enable bam file options

            pm.button("MP_PY_BrowseBamTexPathBTN", edit = 1, enable = 1)
            # Enable egg file options

            pm.textField("MP_PY_CustomEggTexPathTF", edit = 1, enable = 1)

            pm.button("MP_PY_BrowseEggTexPathBTN", edit = 1, enable = 1)


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


def MP_PY_SetEggObjectTypeAttribute(
        enumerationList, eggObjectType, indexNumber, attributeNumber, node
):
    # Determining variable on whether we can add egg-object-type attribute to node
    # Check for any currently attached egg-object-type attribute values on the node.
    # If a current attribute matches passed egg-object-type,
    #  we skip adding it again and notify user it already exists.
    for i in range(1, 11):
        if pm.objExists(node + ".eggObjectTypes" + str(i)):
            if pm.getAttr((node + ".eggObjectTypes" + str(i)), asString = 1) == eggObjectType:
                MP_PY_ConfirmationDialog(
                    "Egg-Object-Type Error!",
                    'egg-object-type  -  "' + eggObjectType + '"' +
                    "\n\nAlready attached on node attribute:  \n" +
                    (node + ".eggObjectTypes" + str(i)),
                    "ok",
                )
                return
        # Attribute exists, check if attributes matches the passed egg-object-type
        # Message to user that the egg-object-type is already assigned to node
        # Since attribute already exists on node, set our determining variable to 0 to skip adding it again

    pm.addAttr(
        node,
        ln = ("eggObjectTypes" + str(attributeNumber)),
        enumName = enumerationList,
        attributeType = "enum",
        keyable = 1,
    )
    # Adds the egg-object-type attribute to node if it was not already attached
    pm.setAttr((node + ".eggObjectTypes" + str(attributeNumber)), indexNumber)


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
    pm.columnLayout(adjustableColumn = True, columnAttach = ("left", 0), rowSpacing = 0)
    pm.frameLayout(
        font = "obliqueLabelFont",
        collapsable = False,
        backgroundColor = (0.50, 0.60, 0.20),
        label = "Add Egg-Object-Type Tags to Selected Nodes",
    )

    def create_button_callback(obj_name):
        # hack: need this function otherwise it will pass True/False
        return lambda *args: MP_PY_AddEggObjectFlags(obj_name)

    dataStore = {}
    # Add Egg-Type Tags
    pm.columnLayout(adjustableColumn = True)
    count = 0
    for n in range(0, int((len(pm.melGlobals[EGG_OBJECT_TYPE_ARRAY]) + 1) / 4)):
        pm.rowLayout(nc = 6)
        for i in range(0, 5):
            eggObjectType = pm.melGlobals[EGG_OBJECT_TYPE_ARRAY][count]
            # 5 rows per col
            if eggObjectType != "":
                annotation = str(MP_PY_GetObjectTypeAnnotation(eggObjectType))
                objName = stupid(eggObjectType)
                dataStore[int(count)] = objName
                # Get the defined annotation for egg-object-type
                pm.button(
                    f"MP_PY_AttEggATTR_{objName}",
                    width = 100,
                    height = 17,
                    command = create_button_callback(objName),  # Pass the current objName
                    annotation = annotation,
                    label = f"{objName}",
                )
                count += 1
        pm.setParent(u = 1)

    pm.separator(style = "none", height = 5)
    pm.rowLayout(nc = 1, columnAttach = (1, "left", 100))
    pm.text(
        bgc = (0.350, 0.820, 0.950),
        label = (
                "Object types added to nodes can be edited by selecting the node"
                + "\n and viewing the attributes in the "
                  "channels box of the node."
        ),
    )
    pm.setParent(u = 1)
    pm.setParent(u = 1)
    pm.setParent(u = 1)
    UVScrollFrameHeight = 125
    pm.frameLayout(
        font = "obliqueLabelFont",
        collapsable = False,
        label = "Set Texture UV Scrolling",
        backgroundColor = (0.50, 0.60, 0.20),
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
    pm.showWindow("MP_PY_AddEggObjectTypesWindow")
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
            "No nodes selected.\nPlease select at least one node and try again.",
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
    Retreives egg-object-types from selected node
    """
    currentObjectTypesArray = []
    """
    Generate an array from any egg-object-types that are currently attached to the selected node.
    It then passes this array onto the MP_PY_DeleteEggObjectTypesGUI process,
    to which it then displays them in button style in a separate window
    making it easier for a user to delete them from the selected node.
    """
    currentObjectTypesArray = []
    # Record the currently selected nodes
    selected = pm.ls(l = 1, sl = 1)
    # Verify user has selected at least one node.
    if len(selected) < 1:
        MP_PY_ConfirmationDialog(
            "Selection Error!",
            "Nothing is currently selected"
            + "\nSelect at least one node and try again.",
            "ok",
        )
    # Throw a message if at least one node has not been selected.

    else:
        # Loop through each selected node to check for and gather any egg-object-type attributes
        for selection in selected:
            attributeName = "eggObjectTypes"
            # Attribute name we are checking for
            # Insert current selected node hierarchy into array
            currentObjectTypesArray.insert(len(currentObjectTypesArray), selection)
            for i in range(1, 4):
                if pm.mel.attributeExists((attributeName + str(i)), selection) == 1:
                    currentObjectTypesArray.insert(
                        len(currentObjectTypesArray) + 2,
                        pm.getAttr(
                            (str(selection) + "." + attributeName + str(i)), asString = 1
                        ),
                    )
                # Check for attributes. If present, insert contents into array
                # If not, insert dummy placeholder values
                # Insert attribute value into array.
                # Value is used for button label

                else:
                    currentObjectTypesArray.insert(
                        len(currentObjectTypesArray) + 2, "NONE"
                    )
        # Insert 'NONE' attribute value into array

        MP_PY_DeleteEggObjectTypesGUI(currentObjectTypesArray)


def MP_PY_DeleteEggObjectTypesGUI(currentObjectTypesArray):
    pm.window(
        "MP_PY_DeleteEggObjectTypesWindow",
        retain = 1,
        sizeable = 0,
        visible = 1,
        resizeToFitChildren = True,
        title = "Delete Current Egg-Object-Types",
    )
    # Create the window layout
    pm.frameLayout(
        font = "obliqueLabelFont",
        collapsable = False,
        backgroundColor = (0.50, 0.60, 0.20),
        label = "Egg-Object-Type Tags of selected nodes",
    )
    pm.columnLayout(adjustableColumn = False, rowSpacing = 0)
    pm.rowLayout(rowAttach = (1, "top", 0), nc = 1)
    pm.button(
        "MP_PY_RefreshEggTypesWindowButton",
        width = 110,
        height = 20,
        command = lambda *args: MP_PY_GetEggObjectTypes(),
        annotation = (
                "Refreshes the window with information on selected nodes"
                + "\nUsed if new nodes are selected "
                  "while window is visible"
        ),
        label = "Update Window",
    )
    pm.setParent(u = 1)
    pm.rowLayout(rowAttach = [(1, "top", 0), (2, "top", 0)], nc = 2)
    pm.columnLayout("nodeColumn", width = 150, adjustableColumn = False, rowSpacing = 0)
    pm.rowLayout(columnOffset1 = 15, rowAttach = (1, "top", 0), nc = 1, columnAttach1 = "left")
    pm.text(bgc = (0.350, 0.820, 0.950), label = "Node Name")
    pm.setParent(u = 1)
    pm.setParent(u = 1)
    pm.columnLayout("rowColumn", width = 350, adjustableColumn = False)
    pm.rowLayout(
        rowAttach = [(1, "top", 0), (2, "top", 0), (3, "top", 0)],
        nc = 3,
        columnAttach3 = ("left", "left", "left"),
        columnOffset3 = (30, 65, 65),
    )
    pm.text(bgc = (0.350, 0.820, 0.950), label = "Egg Tag 1")
    pm.text(bgc = (0.350, 0.820, 0.950), label = "Egg Tag 2")
    pm.text(bgc = (0.350, 0.820, 0.950), label = "Egg Tag 3")
    pm.setParent(u = 1)
    pm.setParent(u = 1)
    pm.setParent(u = 1)
    pm.setParent(u = 1)
    pm.setParent(u = 1)
    pm.showWindow("MP_PY_DeleteEggObjectTypesWindow")

    count = 0
    num_rows = len(currentObjectTypesArray) // 4

    for n in range(num_rows):
        # Parse out just the short node name for labeling
        node_hierarchy = currentObjectTypesArray[count]

        # Split node hierarchy into token segments
        hierarchy_tokens = node_hierarchy.split("|")
        node = hierarchy_tokens[-1]

        # Generate the node name label
        pm.text(
            parent = "nodeColumn",
            font = "boldLabelFont",
            height = 22,
            label = node
        )

        # Increment count
        count += 1

        # Create a new row of buttons per node
        # One row will consist of a node name label and up to three buttons
        row_layout = pm.rowLayout(
            parent = "rowColumn",
            nc = 3,
            rowAttach = [(n + 1, "top", 0)],
            name = f"rowLine{n}"
        )

        for i in range(3):
            egg_type = currentObjectTypesArray[count]

            if egg_type != "NONE":
                # Create the button for a valid egg-object-type
                pm.button(
                    parent = row_layout,
                    label = currentObjectTypesArray[count],
                    width = 110,
                    height = 20,
                    annotation = f"Deletes the {currentObjectTypesArray[count]} egg-object-type tag from the node",
                    command = lambda node_hierarchy=node_hierarchy, i=i: mp_py_delete_egg_object_type(node_hierarchy,
                                                                                                      i + 1)
                )
            else:
                # Create a dummy placeholder button
                pm.button(
                    parent = row_layout,
                    label = egg_type,
                    width = 110,
                    height = 20,
                    visible = True,
                    enable = False,
                    annotation = "",
                    command = ""
                )

            # Increment count
            count += 1

    # Set window height: base height 51 + 20 per button row
    height = 51 + ((n * 2) + ((n + 1) * 20))
    pm.window("MP_PY_DeleteEggObjectTypesWindow", edit = 1, width = 500, height = height)


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
            type = "yesno"
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
            type = "ok"
        )


# Send array of egg-object-types to MP_PY_DeleteEggObjectTypesGUI


def MP_PY_ArgsBuilder(FileName):
    """
    constructs the arguments to pass to maya2egg
    """
    ARGS = "maya2egg"
    pm.melGlobals.initVar("string", "gMP_PY_MayaVersionShort")
    ARGS += pm.melGlobals["gMP_PY_MayaVersionShort"]
    ARGS += " "
    # Increase output verbosity.  More v's means more verbose.
    ARGS += "-v "
    # We always want polygons, never nurbs.
    ARGS += "-p "
    # check back face culling i.e. 'double-sided faces'
    if pm.checkBox("MP_PY_ExportBfaceCB", query = 1, value = 1):
        ARGS += "-bface "

    if pm.checkBox("MP_PY_ExportLegacyShadersCB", query = 1, value = 1):
        ARGS += "-legacy-shaders "
    # check Shader option

    if pm.checkBox("MP_PY_ExportKeepUvsCB", query = 1, value = 1):
        ARGS += "-keep-uvs "
    # check Keep UV option

    if pm.checkBox("MP_PY_ExportRoundUvsCB", query = 1, value = 1):
        ARGS += "-round-uvs "
    # check Round UV option

    if pm.checkBox("MP_PY_ExportTbnallCB", query = 1, value = 1):
        ARGS += "-tbnall "
    # check tbnall option  'Compute tangent and binormal for all texture coordinate sets'

    if pm.checkBox("MP_PY_ExportLightsCB", query = 1, value = 1):
        ARGS += "-convert-lights "
    # check lights option  'Convert all light nodes to locators.'

    if pm.checkBox("MP_PY_ExportCamerasCB", query = 1, value = 1):
        ARGS += "-convert-cameras "
    # check cameras option  'Convert all camera nodes to locators.'

    exportOptionsARGS = str(
        pm.radioCollection("MP_PY_ExportOptionsRC", query = 1, select = 1)
    )
    # check Export File Type option 'none, pose, flip, strobe, model, chan, or both'
    if exportOptionsARGS == "MP_PY_ChooseMeshRB":
        ARGS += "-a none "

    elif exportOptionsARGS == "MP_PY_ChooseActorRB":
        ARGS += "-a model "

    elif exportOptionsARGS == "MP_PY_ChooseAnimationRB":
        ARGS += "-a chan "
        # set the start frames
        #  **Does not check if start frame < end frame
        #  **Does not support negative values
        #  **Does not check if start/end frame is within bounds of the scene

        if (
                pm.radioCollection("MP_PY_AnimationOptionsRC", query = 1, select = 1)
                == "MP_PY_chooseCustomAnimationRangeRB"
        ):
            startFrameARGS = str(
                pm.intField("MP_PY_AnimationStartFrameIF", query = 1, value = 1)
            )
            endFrameARGS = str(
                pm.intField("MP_PY_AnimationEndFrameIF", query = 1, value = 1)
            )
            # start frame
            if (
                    pm.mel.match("[0-9]+", startFrameARGS) == startFrameARGS
                    and startFrameARGS != ""
            ):
                ARGS += "-sf " + str(pm.mel.match("[0-9]+", startFrameARGS)) + " "

            else:
                pm.mel.error(
                    "Start Frame entered data is the wrong format.  Should be an integer.\n"
                )
                return "failed"

            if (
                    pm.mel.match("[0-9]+", endFrameARGS) == endFrameARGS
                    and endFrameARGS != ""
            ):
                ARGS += "-ef " + str(pm.mel.match("[0-9]+", endFrameARGS)) + " "
            # end frame

            else:
                pm.mel.error(
                    "End Frame entered data is the wrong format.      Should be an integer.\n"
                )
                return "failed"

    elif exportOptionsARGS == "MP_PY_ChooseBothRB":
        ARGS += "-a both "
        # set the start frames
        #  **Does not check if start frame < end frame
        #  **Does not support negative values
        #  **Does not check if start/end frame is within bounds of the scene

        if (
                pm.radioCollection("MP_PY_AnimationOptionsRC", query = 1, select = 1)
                == "MP_PY_chooseCustomAnimationRangeRB"
        ):
            startFrameARGS = str(
                pm.intField("MP_PY_AnimationStartFrameIF", query = 1, value = 1)
            )
            endFrameARGS = str(
                pm.intField("MP_PY_AnimationEndFrameIF", query = 1, value = 1)
            )
            # start frame
            if (
                    pm.mel.match("[0-9]+", startFrameARGS) == startFrameARGS
                    and startFrameARGS != ""
            ):
                ARGS += "-sf " + str(pm.mel.match("[0-9]+", startFrameARGS)) + " "

            else:
                pm.mel.error(
                    "Start Frame entered data is the wrong format.  Should be an integer.\n"
                )
                return "failed"

            if (
                    pm.mel.match("[0-9]+", endFrameARGS) == endFrameARGS
                    and endFrameARGS != ""
            ):
                ARGS += "-ef " + str(pm.mel.match("[0-9]+", endFrameARGS)) + " "
            # end frame

            else:
                pm.mel.error(
                    "End Frame entered data is the wrong format.      Should be an integer.\n"
                )
                return "failed"

    elif exportOptionsARGS == "MP_PY_ChoosePoseRB":
        ARGS += "-a pose "
        # set the pose frame for animation
        #  **Does not support negative values

        startFrameARGS = str(
            pm.intField("MP_PY_AnimationStartFrameIF", query = 1, value = 1)
        )

        if (
                pm.mel.match("[0-9]+", startFrameARGS) == startFrameARGS
                and startFrameARGS != ""
        ):
            ARGS += "-sf " + str(pm.mel.match("[0-9]+", startFrameARGS)) + " "

        else:
            pm.mel.error(
                "Start Frame entered data is the wrong format.  Should be an integer.\n"
            )
            return "failed"

    transformMode = str(pm.radioCollection("MP_PY_TransformModeRC", query = 1, select = 1))
    # Get the 'transform mode' option and append to $ARGS string
    if transformMode == "MP_PY_ChooseTransformModelRB":
        ARGS += "-trans model "

    elif transformMode == "MP_PY_ChooseTransformAllRB":
        ARGS += "-trans all "

    elif transformMode == "MP_PY_ChooseTransformDCSRB":
        ARGS += "-trans dcs "

    elif transformMode == "MP_PY_ChooseTransformNoneRB":
        ARGS += "-trans none "

    if pm.checkBox("MP_PY_RemoveGroundPlaneCB", query = 1, value = 1) == 1:
        ARGS += "-exclude groundPlane_transform "
    # Check status of remove groundPlane_transform checkBox

    up = str(pm.upAxis(q = 1, axis = 1))
    # get scene up axis and append to $ARGS string
    ARGS += "-cs " + up + "-up "
    # get units from option menu and append to $ARGS string
    unit = str(pm.optionMenu("MP_PY_UnitMenu", q = 1, value = 1))
    ARGS += "-uo " + unit + " "
    """-cn name
      Specifies the name of the animation character.  This
      should match between all of the model files and all of
      the channel files for a particular model and its
      associated channels.
      Only applied if the exported file is not a mesh type.
    """
    if exportOptionsARGS != "MP_PY_ChooseMeshRB":
        if pm.textField("MP_PY_CharacterNameTF", query = 1, text = 1) != "":
            ARGS += (
                    "-cn "
                    + str(
                pm.mel.substituteAllString(
                    pm.textField("MP_PY_CharacterNameTF", query = 1, text = 1), " ", "_"
                )
            )
                    + " "
            )
        # User has entered a character name, we use that
        # spaces not allowed, replace with underscores

        else:
            ARGS += "-cn " + str(pm.mel.substituteAllString(FileName, " ", "_")) + " "
    # User did not enter a character name, we use file name as character name
    # spaces not allowed, replace with underscores

    mustRestart = 0
    """-force-joint name
      Specifies the name(s) of a DAG node that maya2egg should
      treat as a joint, even if it does not appear to be a
      Maya joint and does not appear to be animated.
      The specified DAGs have to be tagged as a DCS egg-type.
      Routine checks for this and if it doesn't exist, it adds the DCS tag to it.
    """
    JointNames = str(pm.textField("MP_PY_ForceJointTF", query = 1, text = 1))
    joints = JointNames.split(" ")
    numberEntries = int(len(joints))
    if pm.textField("MP_PY_ForceJointTF", query = 1, text = 1) != "":
        # iterate through each named joint and verify they have the required 'DCS' object-type flag set
        # If not, we add the attribute and request restarting the export process
        # We MUST restart so the export process recognizes the added object-tags
        for i in range(0, numberEntries):
            eggObjectTypes1 = ""
            eggObjectTypes2 = ""
            eggObjectTypes3 = ""
            pm.select(joints[i], r = 1)
            if pm.mel.attributeExists("eggObjectTypes1", joints[i]) == 1:
                eggObjectTypes1 = str(
                    pm.getAttr((joints[i] + ".eggObjectTypes1"), asString = 1)
                )

            if pm.mel.attributeExists("eggObjectTypes2", joints[i]) == 1:
                eggObjectTypes2 = str(
                    pm.getAttr((joints[i] + ".eggObjectTypes2"), asString = 1)
                )

            if pm.mel.attributeExists("eggObjectTypes3", joints[i]) == 1:
                eggObjectTypes3 = str(
                    pm.getAttr((joints[i] + ".eggObjectTypes3"), asString = 1)
                )

            if "dcs" in [eggObjectTypes1, eggObjectTypes2, eggObjectTypes3]:
                ARGS += "-force-joint " + joints[i] + " "
            # If any of the current object-type attributes are DCS, append to $ARGS
            # If there is no DCS attribute, add it to the node

            else:
                MP_PY_AddEggObjectFlags("dcs")
                mustRestart += 1

        if mustRestart != 0:
            confirmRestart = str(
                MP_PY_ConfirmationDialog(
                    "File Error!",
                    "We had to add a missing DCS flag to one or more of the "
                    '"-force-joint" nodes.' + "\nWe must restart the "
                                              "exporting process now."
                    + "\nPress 'Yes' to restart, Press 'No' to exit exporting",
                    "yesno",
                )
            )
            # If $mustRestart variable is greater than 0, we had to add a DCS tag.
            # If we had to add a DCS tag to any nodes, we must restart exporting so it's recognized.
            # Otherwise, the force-joint for that node will not export properly.
            # Prompt user with confirm dialog if we had to add the DCS attribute to any of the nodes
            if confirmRestart == "YES":
                MP_PY_StartSceneExport()
                return "failed"
            # needed to exit the previous exporting loop

            else:
                pm.mel.error("User cancelled exporting")
                return "failed"

    if pm.radioCollection("MP_PY_TexPathOptionsRC", query = 1, select = 1) != "MP_PY_ChooseDefaultTexPathRB":
        ARGS += "-ps rel" + " "
    # Check custom reference path and output path; append to $ARGS string
    # -ps   The option may be one of: rel, abs, rel_abs, strip, or keep. If either rel or rel_abs is specified,
    #      the files are made relative to the directory specified by -pd.  The default is rel.
    # Check if we are referencing textures to a path OTHER than the Maya file

    customTexPath = str(pm.textField("MP_PY_CustomEggTexPathTF", query = 1, text = 1))
    # -pd   Specifies the name of a directory to make paths relative to, if '-ps rel' or '-ps rel_abs' is specified.
    #      If this is omitted, the directory name is taken from the name of the output file.
    # -pp   Adds the indicated directory name to the list of directories to search for filenames referenced by the
    # source file.
    #      We always want to add the file path to the search
    # -pc   Copies textures and other dependent files into the indicated directory.
    #      If a relative pathname is specified, it is relative to the directory specified with -pd, above.
    # Check if we are referencing textures to a Custom path
    if pm.radioCollection("MP_PY_TexPathOptionsRC", query = 1, select = 1) == "MP_PY_ChooseCustomRefPathRB":
        if pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = 1, select = 1) == "MP_PY_ChooseEggRB":
            if customTexPath != "":
                ARGS += "-pd " + '"' + customTexPath + '"' + " "
                # If we are exporting to an Egg File and Bam File, THE EGG MUST BE RELATIVE TO MAYA FILE!!
                # So we skip this.
                # Otherwise the bam file will be produced without textures since it can't find them during compiling
                #  NOTE: Bam file texture referencing is handled in the MP_Export2Bam process
                #  NOTE: Bam file texture referencing is handled in the Export2Bam process
                # If exporting only to an Egg File, relative referencing will function as expected
                #  and directory path MUST start with the path to where the textures are truly located
                # Verify user entered in a path
                ARGS += "-pp " + '"' + customTexPath + '"' + " "

    customOutputPath = str(pm.textField("MP_PY_CustomOutputPathTF", query = 1, text = 1))
    # Check if we are copying and referencing textures to a Custom path
    if pm.radioCollection("MP_PY_TexPathOptionsRC", query = 1, select = 1) == "MP_PY_ChooseCustomTexPathRB":
        if customTexPath != "":
            ARGS += "-pc " + '"' + customTexPath + '"' + " "
            ARGS += "-pp " + '"' + customTexPath + '"' + " "

        if customOutputPath != "":
            ARGS += "-pd " + '"' + customOutputPath + '"' + " "

    print("Using these arguments: " + ARGS + "[END]\n")
    return ARGS


def MP_PY_StartSceneExport():
    tempMBFile = ""
    """
    We need to do before calling Export2Egg/BAM/Pview:
    -Export a temporary MB
    -Get the destination path
    -Get the filename
    -Get the custom arguments
    """
    if pm.checkBox("MP_PY_ExportSelectedCB", query = 1, value = 1):
        tempMBFile = str(MP_PY_ExportScene("selected"))
        # returns $tempScenePath as $tempMBFile
        if tempMBFile == "failed":
            return 0

    else:
        tempMBFile = str(MP_PY_ExportScene("all"))
        # returns $tempScenePath as $tempMBFile
        if tempMBFile == "failed":
            return 0

    origFileName = str(pm.mel.basenameEx(pm.cmds.file(q = 1, sceneName = 1)))
    # Determine base file name from the scene name.
    """
    Get the destination path
    Get the filename
    Get the custom arguments
    """
    eggFile = str(MP_PY_ExportPrep(tempMBFile, origFileName))
    # Delete the temporary Maya binary file
    # sysFile -del $tempMBFile;
    # Check if the eggFile passed return, else return it failed as an integer
    if eggFile == "failed":
        return 0

    else:
        return 1


def MP_PY_ExportScene(selection):
    """
    exports the entire scene/selected objects
    """
    scenePath = str(pm.mel.dirname(pm.cmds.file(q = 1, sceneName = 1)))
    # gets the current scene filename and path if present.
    fileName = str(pm.mel.basenameEx(pm.cmds.file(q = 1, sceneName = 1)))
    # cut off the file extension
    fileExtension = str(pm.mel.fileExtension(pm.cmds.file(q = 1, sceneName = 1)))
    # Returns file extension
    tempScenePath = ""
    # Processes if exporting file with original file name and default output path
    if (
            pm.radioCollection("MP_PY_OutputFilenameOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseOriginalFilenameRB"
    ) and (
            pm.radioCollection("MP_PY_OutputPathOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseDefaultOutputPathRB"
    ):
        if (scenePath == "") or (fileName == ""):
            MP_PY_ConfirmationDialog(
                "File Error!",
                "It appears you have not yet saved this scene. Please save your scene first"
                + "\nOR, specify a Custom Output Directory AND Custom Filename.",
                "ok",
            )
            return "failed"

        else:
            tempScenePath = scenePath + "/" + fileName + "_temp.mb"

    if (
            pm.radioCollection("MP_PY_OutputFilenameOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseOriginalFilenameRB"
    ) and (
            pm.radioCollection("MP_PY_OutputPathOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseCustomOutputPathRB"
    ):
        if fileName == "":
            MP_PY_ConfirmationDialog(
                "File Error!",
                "It appears you have not yet saved this scene. Please save your scene first"
                + "\nOR, specify a Custom Output Directory AND Custom Filename.",
                "ok",
            )
            # Processes if exporting file with original file name and custom output path
            return "failed"

        else:
            TempPath = str(pm.textField("MP_PY_CustomOutputPathTF", query = 1, text = 1))
            if TempPath == "":
                MP_PY_ConfirmationDialog(
                    "File Error!",
                    "It appears you have not entered a Custom Path."
                    + "\nPlease Enter a "
                      "Custom Path and then"
                      " try Exporting again",
                    "ok",
                )
                return "failed"

            else:
                tempScenePath = TempPath + "/" + fileName + "_temp.mb"

    if (
            pm.radioCollection("MP_PY_OutputFilenameOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseCustomFilenameRB"
    ) and (
            pm.radioCollection("MP_PY_OutputPathOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseDefaultOutputPathRB"
    ):
        if scenePath == "":
            MP_PY_ConfirmationDialog(
                "File Error!",
                "It appears you have not yet saved this scene. Please save your scene first"
                + "\nOR, specify a Custom Output Directory AND Custom Filename.",
                "ok",
            )
            # Processes if exporting file with custom file name and default output path
            return "failed"

        else:
            tempFileName = str(pm.textField("MP_PY_CustomFilenameTF", query = 1, text = 1))
            if tempFileName == "":
                MP_PY_ConfirmationDialog(
                    "File Error!",
                    "It appears you have not entered a Custom File Name."
                    + "\nPlease Enter "
                      "a Custom Name "
                      "and then try "
                      "Exporting again",
                    "ok",
                )
                return "failed"

            else:
                tempScenePath = scenePath + "/" + tempFileName + "_temp.mb"

    if (
            pm.radioCollection("MP_PY_OutputFilenameOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseCustomFilenameRB"
    ) and (
            pm.radioCollection("MP_PY_OutputPathOptionsRC", query = 1, select = 1)
            == "MP_PY_ChooseCustomOutputPathRB"
    ):
        TempPath = str(pm.textField("MP_PY_CustomOutputPathTF", query = 1, text = 1))
        # Processes if exporting file with custom file name and custom output path
        if TempPath == "":
            MP_PY_ConfirmationDialog(
                "File Error!",
                "It appears you have not entered a Custom Path."
                + "\nPlease Enter a Custom "
                  "Path and then try "
                  "Exporting again",
                "ok",
            )
            return "failed"

        else:
            tempFileName = str(pm.textField("MP_PY_CustomFilenameTF", query = 1, text = 1))
            if tempFileName == "":
                MP_PY_ConfirmationDialog(
                    "File Error!",
                    "It appears you have not entered a Custom File Name."
                    + "\nPlease Enter "
                      "a Custom Name "
                      "and then try "
                      "Exporting again",
                    "ok",
                )
                return "failed"

            else:
                tempScenePath = TempPath + "/" + tempFileName + "_temp.mb"

    if selection == "all":
        print("Exporting scene...\n")
        # Export entire scene contents
        pm.cmds.file(tempScenePath, ea = 1, typ = "mayaBinary", op = "v=1")
        # export the whole scene
        print("Saved entire scene as temporary file: " + tempScenePath + "\n")

    else:
        print("Exporting scene...\n")
        # Export selected scene contents
        pm.cmds.file(tempScenePath, typ = "mayaBinary", es = 1, op = "v=1")
        # export only selected objects
        print("Saved selected objects as temporary file: " + tempScenePath + "\n")

    return tempScenePath


def MP_PY_GetObjectTypeAnnotation(objectType):
    """
    Returns the egg-object-type button annotation text of defined types as a string for GUI.
    """
    return OT_ENTRIES.get(
        objectType, f"Adds the {objectType} egg-object-type to selected geometry."
    )


# Return the string


def MP_PY_Globals():
    """
    Contains MP_PY_PandaVersion and egg-object-type arrays
    """
    mayaVersionLong = str(pm.mel.getApplicationVersionAsFloat())
    # get the current Maya version
    pm.melGlobals.initVar("string", "gMP_PY_MayaVersionShort")
    pm.melGlobals["gMP_PY_MayaVersionShort"] = str(
        pm.mel.substituteAllString(mayaVersionLong, ".", "")
    )
    # Strips the version zeroes if the version number length is less than 4
    if len(pm.melGlobals["gMP_PY_MayaVersionShort"]) < 4:
        pm.melGlobals["gMP_PY_MayaVersionShort"] = str(
            pm.mel.substituteAllString(pm.melGlobals["gMP_PY_MayaVersionShort"], "0", "")
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
    pm.melGlobals[EGG_OBJECT_TYPE_ARRAY] = sorted(OT_ENTRIES.keys())
    # Removed:
    # polylight portal
    # todo: maybe add option to type own number for seqX
    # Global variable that keeps track of whether user has seen the import Panda file notification.
    # It is designed so that the user only sees the notification once during session.
    pm.melGlobals.initVar("int", "gMP_PY_ChoosePandaFileNotice")
    pm.melGlobals["gMP_PY_ChoosePandaFileNotice"] = 0


def MP_PY_CreatePandaExporterWindow():
    """
    Creates the GUI control
    """
    pm.melGlobals.initVar("string[]", PANDA_FILE_VERSIONS)
    # Process Variables
    pm.melGlobals.initVar("string", "gMP_PY_MayaVersionShort")
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
    pm.rowLayout(
        numberOfColumns = 2, rowAttach = [(1, "top", 0), (2, "top", 0), (3, "top", 0)]
    )
    # region  Construct LEFT Column
    pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0)
    pm.frameLayout(width = 200, height = 65, label = "Export File Type")
    pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0)
    pm.radioCollection("MP_PY_ExportOptionsRC")
    pm.rowLayout(numberOfColumns = 3)
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
    pm.rowLayout(numberOfColumns = 2)
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
    pm.frameLayout(width = 200, height = 65, label = "Transforms To Save:")
    pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0)
    pm.radioCollection("MP_PY_TransformModeRC")
    pm.rowLayout(numberOfColumns = 3)
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
    pm.rowLayout(numberOfColumns = 3)
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
    pm.frameLayout(width = 200, height = 215, label = "Export Options")
    pm.columnLayout(columnAttach = ("left", 0))
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
                "Use this flag to turn off modern (Phong) shader generation"
                + "\nand treat shaders as if they were "
                  "Lamberts (legacy)"
        ),
        value = 0,
        label = "Only legacy shaders",
    )
    pm.checkBox(
        "MP_PY_ExportKeepUvsCB",
        annotation = (
                "Convert all UV sets on all vertices, even those that do"
                + "\nnot appear to be referenced by any "
                  "textures."
        ),
        value = 1,
        label = "Keep all UV's",
    )
    pm.checkBox(
        "MP_PY_ExportRoundUvsCB",
        annotation = (
                "Round up uv coordinates to the nearest 1/100th. i.e."
                + "\n-0.001 becomes0.0; 0.444 becomes 0.44; 0.778 "
                  "becomes 0.78"
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
        changeCommand = lambda *args: MP_PY_LightsSelectedUI(),
        value = 0,
        label = "Convert Lights",
    )
    pm.checkBox(
        "MP_PY_ExportCamerasCB",
        annotation = (
            "Convert all camera nodes to locators. Will preserve position and rotation"
        ),
        enable = 1,
        changeCommand = lambda *args: MP_PY_CamerasSelectedUI(),
        value = 0,
        label = "Convert Cameras",
    )
    pm.checkBox(
        "MP_PY_RemoveGroundPlaneCB",
        annotation = (
            'Removes the "groundPlane_transform" node from the exported EGG file(s).\n'
            "Currently, this is only supported for Mesh exporting.\n\n"
            "NOTE: Ensure the node is EMPTY before enabling this option.\n"
            "This feature allows for the removal of an empty node from the EGG file during the maya2egg export process."
        ),
        enable = 1,
        changeCommand = lambda *args: MP_PY_RemoveGroundPlaneUI(),
        value = 1,
        label = "Remove groundPlane_transform",
    )
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    pm.frameLayout(width = 200, height = 85, label = "Bam Specific Options")
    pm.columnLayout(columnAttach = ("left", 0))
    pm.rowLayout(numberOfColumns = 3)
    pm.optionMenu(
        "MP_PY_BamVersionOptionMenu",
        width = 100,
        annotation = (
                "Bam file version to use for creating the bam file"
                + "These can be added to the "
                  "$gMP_PY_PandaFileVersions Array as "
                  "needed"
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
    pm.rowLayout(numberOfColumns = 2)
    # region rawtex
    pm.checkBox("MP_PY_RawtexCB", value = 0, label = "Pack Textures into Bam (-rawtex)")
    pm.setParent(upLevel = 1)
    pm.rowLayout(numberOfColumns = 2)
    # endregion
    # region flatten
    pm.checkBox("MP_PY_FlattenCB", value = 0, label = "Flatten (-flatten 1)")
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    # endregion
    # region convert units from
    pm.frameLayout(width = 200, height = 50, label = "Convert Units From")
    pm.columnLayout(columnAttach = ("left", 0))
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
        onCommand = lambda *args: MP_PY_OutputPandaFileTypeUI(),
        select = 1,
        collection = "MP_PY_OutputPandaFileTypeRC",
        label = "EGG (ASCII) Only",
    )
    pm.radioButton(
        "MP_PY_ChooseEggBamRB",
        onCommand = lambda *args: MP_PY_OutputPandaFileTypeUI(),
        collection = "MP_PY_OutputPandaFileTypeRC",
        label = "EGG(ASCII)   and   BAM(Binary)",
    )
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    # endregion
    pm.frameLayout(width = 200, height = 50, label = "Egg-Object-Types:")
    pm.columnLayout(columnAttach = ("left", 0))
    pm.rowLayout(numberOfColumns = 2)
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
    pm.columnLayout(columnAttach = ("left", 0), rowSpacing = 0)
    pm.frameLayout(width = 270, height = 320, label = "Output Path & Name Options:")
    pm.columnLayout(columnAttach = ("left", 0))

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
    pm.rowLayout(numberOfColumns = 3, rowAttach = (1, "top", 0))
    pm.textField(
        "MP_PY_CustomEggTexPathTF",
        width = 215,
        enable = 0,
        annotation = (
            "Egg File custom texture reference path.\n\n"
            "NOTE: If using the copy-to option for textures, this will be the copied-to directory.\n"
            "If exporting both an EGG and BAM file, the BAM file texture referencing can be further modified below."
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
            "If exporting both an EGG and BAM file, the BAM file texture referencing can be further modified below."
        ),
        label = "Browse",
    )
    pm.setParent(u = 1)
    pm.text(label = "Bam File Texture Ref Path:")
    pm.rowLayout(numberOfColumns = 3, rowAttach = (1, "top", 0))
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
                + "\nThe Bam file reference path MUST start with the path to where textures are located."
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
    pm.rowLayout(numberOfColumns = 2, rowAttach = (1, "top", 0))
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
    pm.rowLayout(numberOfColumns = 2)
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
    pm.rowLayout(rowAttach = (1, "top", 0), nc = 3)
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
    # endregion

    # region Animation options
    pm.frameLayout(width = 270, height = 120, label = "Animation Options")
    pm.columnLayout(columnAttach = ("left", 0))
    pm.rowLayout(numberOfColumns = 2)
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
    pm.rowLayout(numberOfColumns = 2)
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
    pm.rowLayout(numberOfColumns = 2)
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
    pm.rowLayout(numberOfColumns = 6)
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
        changeCommand = lambda *args: MP_PY_AnimationOptionsUI("updateFrameValues", "startFrameIFChanged"),
        annotation = ("Set the animation start frame: Default is 0" + "\nRange is 0 to 10,000"),
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
        annotation = ("Set the animation start frame: Default is 0" + "\nRange is 0 to 10,000"),
    )
    pm.text(
        "MP_PY_AnimationEndFrameLabel",
        enable = 0,
        annotation = ("Set the animation end frame: Default is 48" + "\nRange is 0 to 10,000"),
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
        changeCommand = lambda *args: MP_PY_AnimationOptionsUI("updateFrameValues", "endFrameIFChanged"),
        annotation = (
                "Set the animation end frame: Default is 48" + "\nRange is 0 to 10,000"
        ),
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
        annotation = (
                "Set the animation end frame: Default is 48" + "\nRange is 0 to 10,000"
        ),
    )

    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    # endregion
    # region Export scene/nodes options
    pm.frameLayout(width = 270, height = 80, label = "Export Scene or Export Nodes:")
    pm.columnLayout(columnAttach = ("left", 0))
    pm.rowLayout(numberOfColumns = 2)
    pm.button(
        "MP_PY_ExportSceneBTN",
        width = 110,
        height = 20,
        command = lambda *args: MP_PY_StartSceneExport(),
        annotation = (
            "Creates a Panda Egg file (and a BAM file if both are chosen) "
            "by first exporting the scene as a Maya file.\n"
            "It then runs maya2egg[version] on the Maya file using the selected export options.\n\n"
            "If both EGG and BAM files are chosen, it will run the selected version of egg2bam on the EGG file, "
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
            "Sends either the selected nodes or the entire scene (if nothing is selected) to the libmayapview plugin, "
            "if it is installed and loaded.\n"
            "If the plugin is not installed or loaded, it prompts for a file to view instead."
        ),
        label = "Sent To Pview",
    )
    pm.setParent(upLevel = 1)
    pm.rowLayout(numberOfColumns = 3)
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
    pm.frameLayout(width = 270, height = 80, label = "Convert Files:")
    pm.columnLayout(columnAttach = ("left", 0))
    pm.rowLayout(numberOfColumns = 3)
    pm.button(
        "MP_PY_GetMayaFile2EggBTN",
        width = 85,
        height = 20,
        command = lambda *args: MP_PY_GetMayaFile2Egg(),
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
        command = lambda *args: MP_PY_GetEggFile2Bam(),
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
        command = lambda *args: MP_PY_GetBamFile2Egg(),
        annotation = "Runs bam2egg on the selected bam file(s)",
        label = "Bam File 2 Egg",
    )
    pm.setParent(upLevel = 1)
    pm.rowLayout(numberOfColumns = 3)
    # endregion
    pm.button(
        "MP_PY_ImportPandaFileBTN",
        width = 100,
        height = 20,
        command = lambda *args: MP_PY_ImportPandaFile(),
        annotation = "Imports selected Panda Bam or Egg file(s).",
        label = "Import Panda File",
    )
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    pm.setParent(upLevel = 1)
    # endregion
    pm.setParent(top = 1)
    # endregion


pm.melGlobals.initVar("string", "gMainWindow")
pm.setParent(pm.melGlobals["gMainWindow"])
# Delete any current instances of the menu
if pm.menu("MP_PY_PandaMenu", exists = 1):
    pm.deleteUI("MP_PY_PandaMenu", menu = 1)

if pm.window("MP_PY_NodesExportedToPandaFilesGUI", exists = 1):
    pm.deleteUI("MP_PY_NodesExportedToPandaFilesGUI", window = 1)
# Delete any current instances of the exportedPandaFile window

if pm.window("MP_PY_PandaExporter", exists = 1):
    pm.deleteUI("MP_PY_PandaExporter", window = 1)
# Delete any current instances of the MP_PY_PandaExporter window

if pm.window("MP_PY_AddEggObjectTypesWindow", exists = 1):
    pm.deleteUI("MP_PY_AddEggObjectTypesWindow", window = 1)
# Delete any current instances of the MP_PY_AddEggObjectTypesWindow window
# endregion

if pm.window("MP_PY_DeleteEggObjectTypesWindow", exists = 1):
    pm.deleteUI("MP_PY_DeleteEggObjectTypesWindow", window = 1)
# Delete any current instances of the MP_PY_DeleteEggObjectTypesWindow window

pm.menu("MP_PY_PandaMenu", label = "Panda3D_Python")
# region Init menu
# Define main menu and menu items
# Set the MP_PY_PandaMenu as the parent for the following menuItems
pm.setParent("MP_PY_PandaMenu", menu = 1)
pm.menuItem(
    command = lambda *args: MP_PY_PandaExporterUI(), label = "Panda Export GUI..."
)
pm.menuItem(
    command = lambda *args: MP_PY_GetFile2Pview(), label = "View file in PView..."
)
pm.menuItem(
    command = lambda *args: MP_PY_AddEggObjectTypesGUI(),
    label = "Add Egg-Type Attribute",
)
pm.menuItem(command = lambda *args: MP_PY_GotoPanda3D(), label = "Panda3D Home")
pm.menuItem(command = lambda *args: MP_PY_GotoPanda3DManual(), label = "Panda3D Manual")
pm.menuItem(
    command = lambda *args: MP_PY_GotoPanda3DForum(), label = "Panda3D Help Forums"
)
pm.menuItem(
    command = lambda *args: MP_PY_GotoPanda3DSDKDownload(),
    label = "Download Panda3D-SDK",
)


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
    file_name = os.path.splitext(os.path.basename(egg_file))[0]
    file_extension = os.path.splitext(egg_file)[1]
    file_path = os.path.dirname(egg_file)

    # Check for bam output options
    raw_tex = "-rawtex " if pm.checkBox("MP_PY_RawtexCB", query = True, value = True) else ""
    flatten = "-flatten 1 " if pm.checkBox("MP_PY_FlattenCB", query = True, value = True) else ""
    path_store = ""
    path_directory = ""
    target_directory = ""
    dirname = ""

    # Handle custom output options in exportMode 1
    if export_mode == 1:
        custom_filename = pm.textField("MP_PY_CustomFilenameTF", query = True, text = True)
        if custom_filename:
            file_name = custom_filename

        custom_output_path = pm.textField("MP_PY_CustomOutputPathTF", query = True, text = True)
        if custom_output_path:
            file_path = custom_output_path

    # Custom texture referencing options
    tex_path_option = pm.radioCollection("MP_PY_TexPathOptionsRC", query = True, select = True)
    output_panda_file_type = pm.radioCollection("MP_PY_OutputPandaFileTypeRC", query = True, select = True)
    custom_bam_tex_path = pm.textField("MP_PY_CustomBamTexPathTF", query = True, text = True)
    custom_egg_tex_path = pm.textField("MP_PY_CustomEggTexPathTF", query = True, text = True)

    if tex_path_option == "MP_PY_ChooseCustomRefPathRB":
        path_store = "-ps rel "
        if output_panda_file_type == "MP_PY_ChooseEggRB":
            path_directory = f"-pd \"{custom_egg_tex_path or file_path}\" "
            dirname = f"-pp \"{file_path}\" "
        elif output_panda_file_type == "MP_PY_ChooseEggBamRB":
            path_directory = f"-pd \"{custom_bam_tex_path or file_path}\" "
            dirname = f"-pp \"{file_path}\" "

    # Handle copy textures option
    if tex_path_option == "MP_PY_ChooseCustomTexPathRB":
        path_store = "-ps rel "
        if output_panda_file_type == "MP_PY_ChooseEggRB":
            path_directory = f"-pd \"{file_path}\" "
            if export_mode == 1:
                target_directory = f"-pc \"{custom_egg_tex_path or file_path}\" "
            dirname = f"-pp \"{file_path}\" "
        elif output_panda_file_type == "MP_PY_ChooseEggBamRB":
            path_directory = f"-pd \"{custom_bam_tex_path or file_path}\" "
            if export_mode == 1:
                target_directory = f"-pc \"{custom_egg_tex_path or file_path}\" "
            dirname = f"-pp \"{file_path}\" "

    # Define the .bam file path
    bam_file = os.path.join(file_path, f"{file_name}.bam")
    print(f"Your file is: {file_name}{file_extension}")
    print(f"Found in path: {file_path}/")
    print(f"Your bam file will be saved as: {bam_file}")

    # Get the appropriate egg2bam version
    egg2bam = MP_PY_PandaVersion("getEgg2Bam")  # Returns the egg2bam version

    # Overwrite mode or not
    overwrite = pm.checkBox("MP_PY_ExportOverwriteCB", query = True, value = True)
    cmd = (
        f"{egg2bam} {raw_tex}{flatten}{path_store}{path_directory}"
        f"{target_directory}{dirname}"
        f"{'-o ' if overwrite else ''}\"{bam_file}\" \"{egg_file}\""
    )

    # Execute the system command
    result = os.system(cmd)

    # Format and display the options used
    path_store = f"\n{path_store}" if path_store else ""
    path_directory = f"\n{path_directory}" if path_directory else ""
    target_directory = f"\n{target_directory}" if target_directory else ""
    dirname = f"\n{dirname}" if dirname else ""

    print(f"Using these options:\n{cmd}")

    # Run Pview if the option is selected
    if pm.checkBox("MP_PY_ExportPviewCB", query = True, value = True):
        MP_PY_Send2Pview(bam_file)

    print(f"Finished converting (.egg -> .bam), unit: {pm.optionMenu('MP_PY_UnitMenu', query = True, value = True)}")




def MP_PY_Send2Pview(file_path=""):
    """
    Sends the specified file to Pview or uses the Pview plugin for Maya to preview the scene.

    :param file_path: The file to preview. If empty, uses Maya's Pview plugin to preview the scene.
    """
    # Process Variables
    maya_version_short = pm.melGlobals["gMP_PY_MayaVersionShort"]

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
    result = os.system(cmd)
    print(f"{result}\n")

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
            "You must select a directory where the exported files will go.\n"
            "Click \"Choose Directory\" to select the directory and continue\n"
            "or click \"Cancel\" to exit process.",
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
        pm.cmds.file(temp_mb_file, op="v=1", typ="mayaBinary", exportSelected=True, force=True)
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
    if option == "customFilename":
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


MP_PY_Globals()
# Variable to hold our release revision
pm.melGlobals.initVar("string", ADDON_RELEASE_VERSION)
pm.melGlobals[ADDON_RELEASE_VERSION] = "v1.9"
# Call the GUI creation process
MP_PY_CreatePandaExporterWindow()
