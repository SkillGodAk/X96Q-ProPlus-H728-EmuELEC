# H728 release asset verification (local pre-publication snapshot)

2026-10-14, Asia/Taipei. These are **local verified package filenames and recorded hashes**, not evidence that the release has been uploaded or made public.

| Proposed Release asset | Bytes | SHA256 |
| --- | ---: | --- |
| `X96Q pro+_H728_EmuELEC_4.8_Root.7z` | 1,804,414,683 | `528a9a09839546c6339d0dd129c5a4131422487d7bdd59126856afc2d176314b` |
| `X96Q pro+_H728_EmuELEC_4.8_NoRoot.7z` | 1,804,661,810 | `9722ac827ba50234f8211cfe38cadfbb1d5b7e2d607bf366bd12e6805041eab5` |
| `H728-GameSwitch.apk` | 16,924 | `f0dc7a8dcf4ddae0c764d164622c65a5992d580507226efa7eaf6f8923bdce7c` |

Root archive 7z listing contains only `H728_EmuELEC_4.8_Crystal_DualBoot_20261013.img` (4 GiB); NoRoot listing contains only `H728_EmuELEC_4.8_Crystal_Standalone_20261013.img` (4 GiB).

Corresponding full extracted IMG SHA256 values from MD83:

- Root: `f7340855da489c164fc4b0994ec13f56a357a95a1b393d57496f424a38c552b3`
- NoRoot: `97d67fb8d0cb0f27f7e3682a7a0be28d859a92ec522cb448d302b205f44036c9`

Before any public Release, execute a full archive decompression hash verification and finalize corresponding-source licensing audit. **NoRoot original IR remote wake target: EmuELEC; Root original IR remote wake target: Android.**
