"""Apply one scoped runtime-PM experiment to the isolated clean kernel tree.

This is a candidate, not a proven fix for the firstboot ext4 corruption.
Other MMC controllers and system-sleep PM callbacks remain unchanged.
"""
from pathlib import Path
import hashlib
import json
import sys

BASE_SHA = '885cb0dec475d25436a5602eb890b71a95c3bcb036b87b14e5dba4ccc674a01a'


def main():
    tree = Path(sys.argv[1]).resolve()
    assert tree.name == 'kernel-handoff-source'
    path = tree / 'drivers/mmc/host/sunxi-mmc.c'
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == BASE_SHA, 'Unexpected base MMC source'
    text = data.decode()
    before = '\tpm_runtime_set_active(&pdev->dev);\n\tpm_runtime_set_autosuspend_delay(&pdev->dev, 50);'
    after = '''\tpm_runtime_set_active(&pdev->dev);
\t/*
\t * Candidate workaround for firstboot storage corruption on X96Q Pro+.
\t * Keep only its boot SD controller active between requests. System
\t * sleep still uses the existing force_suspend/force_resume callbacks.
\t * No change to SD frequency, voltage, DMA geometry, SDIO or eMMC.
\t */
\tif (of_machine_is_compatible("amediatech,x96q-pro-plus") &&
\t    of_device_is_compatible(pdev->dev.of_node,
\t\t\t\t    "allwinner,sun55i-a523-mmc")) {
\t\tstruct resource *res;

\t\tres = platform_get_resource(pdev, IORESOURCE_MEM, 0);
\t\tif (res && res->start == 0x04020000) {
\t\t\tpm_runtime_set_autosuspend_delay(&pdev->dev, -1);
\t\t\tdev_info(&pdev->dev, "keeping boot SD active between requests\\n");
\t\t} else {
\t\t\tpm_runtime_set_autosuspend_delay(&pdev->dev, 50);
\t\t}
\t} else {
\t\tpm_runtime_set_autosuspend_delay(&pdev->dev, 50);
\t}'''
    assert text.count(before) == 1
    original_pm = text[text.index('static const struct dev_pm_ops sunxi_mmc_pm_ops'):]
    updated = text.replace(before, after)
    assert updated[updated.index('static const struct dev_pm_ops sunxi_mmc_pm_ops'):] == original_pm
    backup = tree.parent / 'sunxi-mmc-before-keepawake.c'
    assert not backup.exists(), 'Candidate already prepared'
    backup.write_bytes(data)
    path.write_text(updated)
    report = {'base_sha256': BASE_SHA,
              'candidate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'scope': 'X96Q Pro+ A523 boot SD controller at 0x04020000 only',
              'system_sleep_pm_unchanged': True,
              'frequency_voltage_dma_unchanged': True,
              'physical_sd_written': False,
              'acceptance': 'NOT PROVEN; controlled runtime-PM candidate'}
    (tree.parent / 'boot-sd-keepawake-source-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
