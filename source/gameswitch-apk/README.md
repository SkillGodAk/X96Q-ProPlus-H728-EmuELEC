# H728 GameSwitch APK source

This directory contains the project-owned source representation used for H728-GameSwitch.apk. It is not a third-party APK.

The helper does one job: on a Root version of the original X96Q Pro+ H728 Android environment, it requests the existing su binary, locates a removable/SD MMC block device, changes only the guarded eGON.OFF/eGON.BT0 boot marker, verifies the write, syncs and reboots.

It does not root Android and it does not contain a rooting exploit.

Release APK SHA256:
f0dc7a8dcf4ddae0c764d164622c65a5992d580507226efa7eaf6f8923bdce7c

The published files are the manifest, apktool metadata, resource ID file and MainActivity.smali. Generated classes.dex, packaged resources, signatures and signed APK output are intentionally not duplicated here.