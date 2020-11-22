///////////////////////////////////////////////////////////////////////////////////
// Panda3D Exporter Tool                                                         //
// Carnegie Mellon University ETC (Entertainment Technology Center) Panda3D Team //
// Author: Shao Zhang                                                            //
// 04/14/2005                                                                    //
//                                                                               //
// This tool will allow an artist to export and view assets directly from maya.  //
//                                                                               //
// To run this mel script, drag and drop it (the .mel file) into your current    //
// maya workspace.                                                               //
///////////////////////////////////////////////////////////////////////////////////
//
// EDIT HISTORY
//
// 06/26/06: ynjh_jo - Major edits; described in http://panda3d.net/phpbb2/viewtopic.php?t=2503
// 07/03/06: Mark Tomczak (fixermark@gmail.com) - Added "Actor" option to export with -a model option
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
// maya panda exporter GUI
//
// 10/1/2011 : updated custom filepath buttons to use new fileDialog2 command
//
// rewrite by ben chang, 9/16/09
//
// - redid layout for linux
// - added menu command with handy tools
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// - 2/17/2014 : Mods by Sean / a.k.a "Sweet"
// - Rewrote some of the script for menu layout
// - --(this was done as it wouldn't fit on my monitor resolution of 1360 x 768)
// - Edited some of the code so that the egg/bam output would actually create a "bam file"
// - On exporting a Bam, the script still lacks in this feature somewhat,
// - --in that it will not let you pick a previous egg file and create a Bam.
// - Also, you have to choose BOTH on export if you want Maya to create a egg & bam file set
// -
// - 2/25/2014 : Mods by Sean / a.k.a "Sweet"
// - Modified GUI layout to clear some un needed free spacing
// - Fixed the Bam file exporting
// -
// - 6/12/2014 : Mods by Sean / a.k.a "Sweet"
// - Modified GUI layout to accomodate changes
// - Added buttons & functions for "Maya File 2 Egg", "Egg File 2 Bam", "Egg Preview"
// - Added checkbox and function for "-rawtex" Bam file output option
// -
// - 6/13/2014 : Mods by Sean / a.k.a "Sweet"
// - Added Title separator for the "-rawtex" Bam Specific Options
// -
// - 06/14/2014 : Mods by Sean / a.k.a "Sweet"
// - Added button and Functions for "Bam2Egg" conversion
// -
// - 06/09/2015 : Mods by Sean / a.k.a "Sweet"
// - Cleaned up some of the coding to be more efficient.
// - Adjusted frameLayout calls to be Maya MEL 2016 compliant. (still funtions with Maya 2015 MEL).
// - They depreciated the '-borderStyle(-bs)' command in Maya 2016.
// - Added text boxes and commands for [-cn <name>] , maya2egg* command, for adding a Character Name
// - --to exported file.
// - Added text boxes and commands for utilizing the [-force-joint <name>] , maya2egg* command.
// - Added an automatic single -v for diplaying some verbosity in script editor when exporting.
// - Added more [-trans type] options, to cover all maya2egg* options available.
// - --The option may be one of all, model, dcs, or none.
// - Rewrote exporting code some to enable the ability to export, using custom name and directory without
// - --needing to save the scene first.
// - It will export the temp file using the chosen custom name, in the custom directory first, then convert that // - file.
// - It will now always export the temp file into a chosen custom directory path, if one is chosen.
// - Added Bam Specific Option [-flatten flag] to choices.
// -
// - 07/06/2015 : Mods by Sean / a.k.a "Sweet"
// - Corrected bad entry to the pview program call. I had pview_638 and should be just pview.
// -
// - 09/15/2015 : Mods by Sean / a.k.a "Sweet"
// - Rewrote the addCollisionFlags process. It now takes a string variable.
// - Added 'Convert Lights' to Export Options.
// - ----NOTE: Will Convert any lights to locators in the egg/bam file.
// - --Lights will only export in a static mesh model, Not in actor/animation files.
// - Rewrote the force-joint process in the ARGS process.
// - --It now can process multiple enitries, space separated, in the Force Joint text box.
// - --It also checks the entered node names to verify that they have the DCS egg-type flag.
// - --If it detects one or more do not, it will add the DCS flag to them and restart the export process.
// - Changed naming conventions for the egg2bam & bam2egg variables.
// - Corrected diplayed revision number.
// - Updated all fileDialog calls to fileDialog2.
// -
// - 10/08/2015 : Mods by Sean / a.k.a "Sweet"
// - Added code to Panda File importing to prevent selected Bam files from being deleted
// - --if the file originates from the Phase Root Folder.
// -
// - 03/08/2016 : Mods by Sean /a.k.a. "Sweet"
// - Changed name of 'addCollisionFlags' process to more appropriate 'MP_AddEggObjectFlags'.
// - Completely rewrote 'MP_AddEggObjectFlags' process for both optimization and for backward compatibility with // - Maya2012.
// - For Maya2012 compatible:
// - --Maya2012 did not support my previous update utilizing the 'stringArrayFind' command.
// - Added a sub-process MP_SetEggObjectTypeAttribute which gets passed numerous variables.
// - --The main process verifies the tag is not already assigned to the node eliminating possible duplicates.
// - --If tag is already present, user gets prompted of such.
// - --The global array that holds the egg-object-type tags is user editable so updates can be made to it.
// - --The main process 'MP_AddEggObjectFlags' gets passed a string variable which is the tag to be added
// - --This now makes it possible to add tags via scripts by simply passing the tag to the process.
// - Rewrote 'Bam2EggVersion' & 'Egg2BamVersion' code and combined the two processes
// - --into one, which is now just called BamFileVersions. The purpose for modifying these into one,
// - --was for streamlining code and for the ability to now handle multiple Panda3D bam file version of the
// - --executables.
// - The user can modify the array '$gMP_PandaFileVersions' that holds the executable names for the ability to
// - --export scenes to the initial egg file then have it compile using different Bam versions.
// - ----(Provided others are installed).
// - --This also allows for multiple pview and egg2bam versions to be utilized through the GUI.
// - ----(Read more about this in the MP_Globals process section)
// - Added a global process 'MP_Globals' to hold the global variables used in script.
// - Added a sub process for handling animation start & end frames
// - --Now, when an animation layer is selected, (highlighted in Maya)
// - --and the user selects to export a type supportive of animations
// - --the script determines the last key frame in the animation layer and uses that number to adjust
// - --the endFrame text on the GUI and also updates the Time Slider
// - --and Range Sliders based on the frames it found.
// - --Since it is based on key frames, if the last key frame is not the last frame,
// - --as before, the user will have to manually adjust the setting prior to exporting.
// - Rewrote most of the code related to the 'pview' operations.
// - --Prior to this release, the code relied completely on calling
// - ----the system command process which ran the pview command.
// - --Now, with a little better understanding of the pview plugins, the code
// - ----utilizes them when the user has selected to run pview after exporting.
// - --Primarily, when the mayapview[version].mll is loaded.
// - --When this one plugin is loaded, it calls pview from within the Maya program after exporting,
// - ----substantially speeding up the process.
// - --Conversly, if the 'mayasavepview[version].mll is the loaded plugin, or if neither plugin is loaded,
// - ----we still rely on the system being queried to run pview.exe
// - Added the 'Import Panda File' button and process.
// - --When this button is clicked, if it is the first time in the session,
// - ----it first asks the user to choose the parent directory
// - ----that has all the extracted phase_* folders in it. i.e., the phase root folder.
// - --After this has been chosen, the user then chooses either a Panda Egg or Panda Bam file.
// - --Once one of those have been selected, if it was a bam file, it first converts it to an egg file,
// - ----then it imports the file into the current scene.
// - --If it is an egg file, it simply imports it to the current scene.
// - --The process asks for the [Phase Root Folder], simply because, based on Disney's file structure,
// - ----the bam file textures are reletive to this root folder.
// - --The process creates a temporary copy of the bam file in this root directory,
// - ----and runs egg2bam on it there.
// - --After the converted egg file has been imported, it removes the copied bam file but leaves the egg file.
// - --Added a routine to check if Panda Egg Import Plugin is currently loaded in Maya
// - ----when importing a Panda file.
// - --Since this is necesary for importing eggs, if it is not loaded, we prompt the user they are NOT loaded
// - ----and directs them to download Panda3D-SDK.
// - Added the 'Convert Nodes To Panda' button and process.
// - Added a child window for adding egg-object-type tags. This should make adding the tags a lot simpler
// - --as they can now be directly added instead of adding a basic tag, then editing it to the type needed.
// - --It auto-creates the buttons based on teh global array entries that can be user edited as needed.
// - Added an over-looked missing file from previous releases, 'eggImportOptions.mel'
// - --This file creates/displays the import options when the file>import GUI screen is called.
// -
// - 03/20/2016 : Mods by Sean /a.k.a. "Sweet"
// - Added Export Option 'Convert Cameras' which will Convert all camera nodes to locators.
// - --There position and rotation will be preserved.
// - Added Texture Reference Path option to 'Output Path & Name Options'.
// - --It's now posssible to reference textures to a specified path without it also copying the
// - ----textures to that directory.
// - --The option to copy textures and reference them to a custom file output path exists as an option as well.
// - --This feature works when clicking 'Maya File 2 Egg' or 'Egg File 2 Bam' as well.
// - Modified 'MP_ArgsBuilder' and 'MP_Export2Bam' process to support updated relative texture pathing options.
// - Modified 'MP_BrowseForFolderPreProcess' processing code to allow for updated
// - --relative texture pathing options above
// - --Cleaned out some unused switch options in process.
// - Miscellaneous code cleanups.
// - Modified, cleaned and streamlined 'MP_ExportPrep' and 'MP_Export2Bam' processes for complex functions
// - --that were no longer needed due to previous revisions.
// - Reworked the 'pview' related codes.
// - --Now, if exporting scene or node(s) to panda files, system command pview is run against final exported file.
// - --If not exporting, then it sends either the selected or entire scene to the 'libmayapview' plugin if loaded.
// - The use of 'libmayasavepview' has been completely eliminated as it's simply not needed.
// -
// - 06/08/2016 : Mods by Sean /a.k.a. "Sweet"
// - Modified main GUI layout to add section for Egg-Object-Tag buttons.
// - Added new method and functions for easily deleting current egg-object-type tags that nodes contain.
// -
// - 06/22/2016 : Mods by Sean /a.k.a. "Sweet"
// - Recode GUI to accomodate the 'Bam file Texture Ref Path'
// - Added 'MP_OutputPandaFileTypeUI' process for new text box and corrected options
// - Adjusted coding of the 'MP_TexPathOptionsUI' process for new text box and corrected options
// - Modified code in 'MP_ArgsBuilder' and 'MP_Export2Bam' process to add to and correct for errors
// - --from a previous update involving texture referencing:
// - 
// - When using 'Reference textures relative to specified path':
// - If exporting to ONLY an egg file:
// - --The egg file textures will be referenced to the specified path.
// - --NOTE: The reference path MUST start with the path to the Maya file being utilized
// - If exporting to both an egg file and a bam file, the bam file is now properly generated.
// - --The egg file textures WILL be referenced relative to the Maya file.
// - --The bam file textures will be referenced to the specified path.
// - --NOTE: The reference path MUST start with the path to the Maya file being utilized
// - If calling an egg file to bam up, the referencing and/or copying options will also
// - --function as they should. Referencing options in this case change based on the
// - --setting of 'Output File Type' prior to browsing for egg file.
// - 
// - When using 'Copy textures and make relative to specified path':
// - If exporting to ONLY an egg file:
// - --The textures will be copied-to the specified path.
// - --The egg file textures will be referenced to the copied-to path.
// - If exporting to both an egg file and a bam file, the bam file is now properly generated.
// - --The textures will be copied-to the specified path.
// - --The egg file textures WILL be referenced relative to the Maya file.
// - --The bam file textures will be referenced to the copied-to path.
// - If calling an egg file to bam up:
// - --The referencing and/or copying options also function as they do above.
// - --Referencing options in this case, however, change based on the setting of 'Output File Type'
// - ----prior to browsing for egg file.
// - --If the egg only option is enabled:
// - ----The original textures will be copied-to the specified path.
// - ----The bam file textures will be made relative to this path.
// - --If the egg and bam file option is enabled:
// - ----The original textures will be copied-to the specified path in the 'Egg file Texture Ref Path' text box.
// - ----The bam file textures will be relative to the path specified in the 'Bam file Texture Ref Path' text box.
// - ----NOTE: The reference path MUST start with the path to the copied-to path being utilized.
// - 
// - 07/11/2017 : Mods by Sean /a.k.a. "Sweet" (primary coding was done 07/06/2016)
// - Added support to the following processes to handle converting multiple files at one time.
// - --MP_BrowseForFile, MP_GetEggFile2Bam, MP_GetMayaFile2Egg, MP_GetBamFile2Egg, MP_ImportPandaFile
// - By adding multiple file support,
// - --The script can now process more than one file at a time when performing these tasks.
// - Example: User wants to convert multiple files from eggs to bams.
// - --After clicking on the appropriate button to start processing, user can use standard windows function of
// - ----holding down the shift or control keys and click on the file(s) to select for conversion.
// - --The script will then process all the selected file(s) one at a time.
// - !!!!!!!!!!!!WARNING WHEN USING MULTIPLE FILE CONVERSIONS:!!!!!!!!!!!!
// - When attempting to convert multiple files, DO NOT USE THE CUSTOM NAME FEATURE. Doing so
// - --gives EVERY FILE the same export name. This will result in only the last file being created,
// - --as all previous files will have been over-writen by the previous file as they are created.
// - Added "MP_" suffix every process and many variables so the script cannot interfere with other scripts.
// - Added GUI checkBox and needed function(s) to remove the "groundPlane_transform" tuple from exported egg MESH files.
// - --While this Maya node is normally empty, care should be taken to ensure it is empty when exporting.
// - --Otherwise there runs the risk of data loss in the egg/bam file(s).
// - 
// - 10/01/2017 : Mods by Sean /a.k.a. "Sweet"
// - Added the ability to add UVScroll values to nodes via the "Add Egg Tags" GUI.
// - Recoded the way confirmDialogs pull their menu and annotation values.
// - Added egg-object-type button annotation.
// ---Now, descriptions pop up, when the mouse is hovered over the button(s), that describe what each button is for.
// - --This annotation was primarily taken right from the Panda3d information.
// - Added release notes from original developer that were missing from the version I initialy used to rewrite this script.
// ---Why 'Ben Chang' left these out from his version, I have no idea.
// ---But, I added them so the original developers would get their credit.
// -
// - 1/14/2020 : Mods by Benjamin Frisby
// - Added the "shadow-cast" egg-type-attribute to the "Add Egg Tags" GUI.
// - Added the "smooth-floors" egg-type-attribute to the "Add Egg Tags" GUI.
// -
// - 11/22/2020 : Mods by Benjamin Frisby
// - Added the "camera-collide" egg-type-attribute to the "Add Egg Tags" GUI.
// -
/////////////////////////////////////////////////////////////////////////////////////////////
