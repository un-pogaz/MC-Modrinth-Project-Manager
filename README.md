# Simple Modrinth Project Manager for Minecraft
mcsmp is a light CLI project manager that gets mods and resourcepacks from Modrinth. One of it's strengths is that it can handle multiple folders.
mcsmp use the packages `requests`.

mcsmp is higly inspire by [Fxomt-III/Minecraft-package-manager](https://github.com/Fxomt-III/Minecraft-package-manager).

Setup:
First, install Minecraft with your favorite laucher.
Second, install the mod loader that you use.
Then, install the python script in the folder of your choice.

After installing mcsmp, you have to define a .minecraft folder to manage.
To add this, use this command:
```bat
mcsmp add <DIRECTORY_NAME> <PATH TO THE .MINECRAFT FOLDER>
```

Once directory are defined, you have to set the Minecraft version assosiated to it, as well as the mod loader used.
```bat
mcsmp version <DIRECTORY_NAME> <VERSION_ID>
```
```bat
mcsmp loader <DIRECTORY_NAME> <LOADER_NAME>
```

<br>

You can display the defined directorys with the command:
```bat
mcsmp list
```

<br>

When a directory is defined, you can manage it with the other commands.

To install a project, use this command:
```bat
mcsmp install <DIRECTORY_NAME> <PROJECT>
```
To instal a project, you need to recover and use its slug-name.
The slug-name is usually the name of the project you are looking for, in lower case and with hyphens (-) instead of space. For example "Sodium" and "Sodium Extra" have respectively the slug-name `sodium` and `sodium-extra`.
But this is not always the case! For example, the "Iris Shaders" has as slug-name `iris` and not `iris-shaders`. One way to get the slug-name of a project is to regad its name in the modrinth link: https://modrinth.com/mod/iris.
This is sometimes more devious as [FerriteCore](https://modrinth.com/mod/ferrite-core) where the slug-name is `ferrite-core`. Caution is therefore required.
Note, to update a project you just have to do this command again.

<br>

You can shows the installed projects:
```bat
mcsmp list <DIRECTORY_NAME>
```

Check if a specific project is installed:
```bat
mcsmp check <DIRECTORY_NAME> <PROJECT>
```

Eventualy, enabled or disabled:
```bat
mcsmp enable <DIRECTORY_NAME> <PROJECT>
```
```bat
mcsmp disable <DIRECTORY_NAME> <PROJECT>
```
(This will add, or remove, a ".disabled" string at the end of the project file, so that it will not be loaded by Minecraft, but it will still be possible to use the mcsmp commands on this project)

And removing a project:
```bat
mcsmp remove <DIRECTORY_NAME> <PROJECT>
```

<br>

A key feature is the possibility to update all the projects in a directory with a simple command:
```bat
mcsmp update <DIRECTORY_NAME>
```

<br>

Also, you can shows the info about a project:
```bat
mcsmp info <PROJECT>
```

<br>

examples:
```bat
mcsmp add fabric-1.18.2 C:\Users\ME\AppData\Roaming\.minecraft
mcsmp check fabric-1.18.2 sodium
mcsmp install fabric-1.18.2 sodium
mcsmp install fabric-1.18.2 sodium-extra
mcsmp install fabric-1.18.2 indium
mcsmp install fabric-1.18.2 lithium
mcsmp install fabric-1.18.2 phosphor
mcsmp install fabric-1.18.2 ferrite-core
mcsmp list fabric-1.18.2
mcsmp info sodium
```

<br>

The `mcsmp.bat` and `mcsmp.sh` are little bash to facilitating the use and execution of many commands.