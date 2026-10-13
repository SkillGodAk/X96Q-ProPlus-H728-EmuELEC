# H728 selected source files and build configurations

This archive was recovered from the actual Ubuntu 22.04.5 H728 build environment and SHA256-checked against its clean-release manifest.

- h728-selected-board-sources-20261014.tar.gz (SHA256: 8fdb49a61ae66ab074571e98d0f437c14caebc527faa325400d2548d17385adc): 27 selected Linux, U-Boot and Trusted Firmware source/config files plus two manifests.
- Upstream Linux: a90ee4305c4a5df72c11b31dacfdc76e00fcf78a
- Upstream U-Boot: a6ab6a66146ed0bf1420db0ee858b49005783222
- Upstream TF-A: b5de74a685fb73b784e45bbbd18dd9a0c528d8b2
- EmuELEC 4.8 base: 02b45fe53b85c45c75dbad8e44a648092dec2e72

The original 27-file snapshot was a preservation checkpoint. The formal release audit now also includes the accepted final SD/MMC delta, core build helpers, Root image rebuild scripts and EmuELEC 4.8 local patches. See SOURCE_AUDIT_20261014.json and ../SOURCE-AND-LICENSES.md for the exact hashes, upstream commits and source layout.