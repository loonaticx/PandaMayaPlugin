# PandaMayaPlugin

A modified version of Panda3D Maya Tools with custom object types to help expedite some of the processes required to get models game-ready.

These tools are made specifically around development for Toontown content. Some of the egg-type attributes available prior have been commented out for ease of use.

There are a few egg-type attributes that will not automatically register when importing in bam or egg files. Specifically, some intended for tube object types or DCS object types do not automatically get picked up and need to be manually re-applied in the Add Egg Object-Types menu.

This plugin should work for newer Maya versions, as it's working perfectly fine with my version of Maya 2016 and Maya 2019 installations.

# Instructions

Copy the two ".mel" files. "MayaPandaUI.mel" & "eggImportOptions.mel" to:
C:\Users\{YOURACCOUNT}\Documents\maya\scripts\

In the above folder, may be a Maya MEL file named "userSetup.mel".
If the userSetup.mel file is NOT present, simply use any text
editor and manually create the file with the entry below,
and make sure to save-as "userSetup.mel".
If the file is present, open it up for editing in something like notepad.
Add the following line entry into it and save it.
source MayaPandaUI.mel;

This file above is used to load scripts on starting up Maya
and can be used for any script the user wishes to load at started time.

"MayaPandaUI.mel" is the main script file of this exporter.
On Maya start-up, the script will place a new menu item on the main menu
inside of Maya, at the top of the Maya GUI.

The file "eggImportOptions.mel" is for a sub menu,
which is used/called when a user runs File>Import.
It creates an option menu inside that GUI window.

Finally, you must copy the two ".mll" from your Panda3d>plugins directory,
that reflect the version of Maya your running, to your
"\Program Files\Autodesk\[MayaVersion]\bin\plug-ins" directory
File to copy to Maya installation:
"mayaeggimport[mayaVersion].mll"
"libmayapview[mayaVersion].mll"

After the above has been done, start up Maya.
Go to "Window>Settings>Preferences>Plug-In Manager"
When the Plug-In Manager GUI opens, find and "Check" the following:
Under "mayaeggimport[mayaVersion].mll"    Check both "Loaded" & "Auto load"
Under "libmayapview[mayaVersion].mll"    Check both "Loaded" & "Auto load"

That's it!  You should now be able to import and export egg and bam files,
along with adding egg-object-types and taking advantage of many export options.

Final Note:
If you just installed the Panda3d SDK and have yet to reboot your computer,
a restart is highly recommended so your computer can find the Panda3d installation!

# Custom Egg Object Types

This plugin reads certain egg nodes (like Collide, Scalar alpha, etc.) and then applies a pre-defined object type in lieu of a bundle of nodes.

So, for example, if a certain node in an egg file calls for both
``<Scalar> collide-mask { 0x02 }`` and ``<Collide> { Polyset descend level }``
then the plugin would replace the two with simply ``<ObjectType> { floor }``

Refer to eggattribs.txt for a list of custom egg object types. In order for Panda to interpret the custom object types, paste the list from eggattribs.txt to your panda's Config.prc file.
