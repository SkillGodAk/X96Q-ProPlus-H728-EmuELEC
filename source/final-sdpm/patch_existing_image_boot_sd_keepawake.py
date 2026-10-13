"""Patch only KERNEL in an owned OEM-corrected candidate image, on a Linux loop.

The file must be the pinned MD80 image; no physical block device accepted.
Boot, P2, SYSTEM, DTB, extlinux and color splash are compared before/after.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

STAGE = Path('/home/ubuntu/h728-cold-start-20261012')
WORK = STAGE / 'boot-sd-keepawake-image'
IMAGE = WORK / 'H728_EmuELEC_4.8_Crystal_Standalone_ColdFix_SDPM_TEST_20261013.img'
BASE = 'c7d7fb942978cd07dde6b6260aedb7eb60d491fe9a62689d0537a70cbb48cb8d'
CONFIG = 'e73aeb9a99ae78ac41c3e54bbca8ffc47b900714b128e74f2c04374767cc48d7'


def digest(path, offset=0, size=None):
    h = hashlib.sha256()
    with path.open('rb') as f:
        f.seek(offset)
        while size is None or size:
            chunk = f.read(8 * 1024 * 1024 if size is None else min(size, 8 * 1024 * 1024))
            if not chunk:
                if size is not None:
                    raise ValueError('Short bounded read')
                break
            h.update(chunk)
            if size is not None:
                size -= len(chunk)
    return h.hexdigest()


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(str(args[0]) + ': ' + result.stdout[-1500:] + result.stderr[-1500:])
    return result.stdout.strip()


def inventory(root):
    return {str(p.relative_to(root)): {'bytes': p.stat().st_size, 'sha256': digest(p)}
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    assert os.geteuid() == 0
    assert IMAGE.resolve().is_relative_to(WORK.resolve()) and IMAGE.is_file()
    assert IMAGE.stat().st_size == 4294967296 and digest(IMAGE) == BASE
    assert (STAGE / 'boot-sd-keepawake-build-r2.rc').read_text().strip() == '0'
    assert digest(STAGE / 'kernel-handoff-source/.config') == CONFIG
    kernel = STAGE / 'KERNEL-BOOT-SD-KEEPAWAKE-CANDIDATE'
    assert kernel.is_file() and 20000000 < kernel.stat().st_size < 35000000
    source_report = json.loads((STAGE / 'boot-sd-keepawake-source-report.json').read_text())
    assert source_report['system_sleep_pm_unchanged'] and source_report['frequency_voltage_dma_unchanged']
    before = {'boot': digest(IMAGE, 0, 4194304),
              'p2': digest(IMAGE, 2151677952, 2143289344)}
    loop = run('losetup', '--find', '--show', '--partscan', str(IMAGE))
    assert loop.startswith('/dev/loop')
    assert Path(run('losetup', '-n', '-O', 'BACK-FILE', loop)).resolve() == IMAGE.resolve()
    mount = WORK / 'mount-p1'
    mount.mkdir(exist_ok=True)
    checks = {}
    try:
        for name, args in [('p1-before', ['fsck.vfat', '-n', loop + 'p1']),
                           ('p2-before', ['e2fsck', '-fn', loop + 'p2'])]:
            checks[name] = run(*args)
        run('mount', '-t', 'vfat', loop + 'p1', str(mount))
        old = inventory(mount)
        assert old['KERNEL']['sha256'] == '467b19f1e002f5fe5fede19deed8cfca22d68bd3c0db4db775164939ded03427'
        assert old['oemsplash-1080.png']['sha256'] == '3128f8928f43c1a3d585368052d1f8e3641deb646130758a81ac2d8af89794df'
        shutil.copyfile(kernel, mount / 'KERNEL')
        run('sync')
        run('umount', str(mount))
        for name, args in [('p1-after', ['fsck.vfat', '-n', loop + 'p1']),
                           ('p2-after', ['e2fsck', '-fn', loop + 'p2'])]:
            checks[name] = run(*args)
        run('mount', '-t', 'vfat', '-o', 'ro', loop + 'p1', str(mount))
        new = inventory(mount)
        assert set(new) == set(old)
        assert {key: value for key, value in old.items() if key != 'KERNEL'} == {
            key: value for key, value in new.items() if key != 'KERNEL'}
        assert new['KERNEL']['sha256'] == digest(kernel)
        run('umount', str(mount))
        assert not Path(loop + 'p3').exists()
    finally:
        if subprocess.run(['mountpoint', '-q', str(mount)]).returncode == 0:
            run('umount', str(mount))
        run('losetup', '-d', loop)
    after = {'boot': digest(IMAGE, 0, 4194304),
             'p2': digest(IMAGE, 2151677952, 2143289344)}
    assert before == after
    sha = digest(IMAGE)
    for name, log in checks.items():
        (WORK / (name + '.fsck.txt')).write_text(log + '\n')
    report = {'image': IMAGE.name, 'bytes': IMAGE.stat().st_size, 'sha256': sha,
              'base_img_sha256': BASE, 'kernel_sha256': digest(kernel),
              'kernel_config_sha256': CONFIG, 'source_change': source_report,
              'preserved_p1_files': {k: v for k, v in new.items() if k != 'KERNEL'},
              'boot_and_p2_byte_identical': before == after, 'range_hashes': after,
              'filesystem_checks': {k: 0 for k in checks}, 'initial_p3_absent': True,
              'physical_sd_modified': False, 'android_emmc_modified': False,
              'hardware_acceptance': 'PENDING; firstboot ext4 causal hypothesis not proven',
              'scope': 'One SD runtime-PM variable; all MD80 P2 files retained. Not a public clean release.'}
    (WORK / 'CANDIDATE_VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    (WORK / (IMAGE.name + '.sha256')).write_text(sha + '  ' + IMAGE.name + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
