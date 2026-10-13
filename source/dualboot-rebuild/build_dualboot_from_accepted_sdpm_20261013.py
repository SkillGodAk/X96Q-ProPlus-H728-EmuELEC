"""Derive Android-first DualBoot from the user-accepted SDPM ordinary IMG.

Runs on the isolated Ubuntu builder. No physical SD/eMMC opens or mkfs P2.
Preserves boot code, KERNEL, SYSTEM, DTB, splash and production P3 initializer.
"""
from pathlib import Path
import hashlib, json, os, shutil, stat, struct, subprocess

W = Path('/home/ubuntu/h728-cold-start-20261012/dualboot-20261013')
I = W/'H728_EmuELEC_4.8_Crystal_DualBoot_20261013.img'
BASE = '97d67fb8d0cb0f27f7e3682a7a0be28d859a92ec522cb448d302b205f44036c9'
APK_SHA = 'f0dc7a8dcf4ddae0c764d164622c65a5992d580507226efa7eaf6f8923bdce7c'
P2 = 2151677952

def sha(p, offset=0, size=None):
    h=hashlib.sha256()
    with p.open('rb') as f:
        f.seek(offset)
        while size is None or size:
            b=f.read(8*1024*1024 if size is None else min(size,8*1024*1024))
            if not b:
                assert size is None
                break
            h.update(b)
            if size is not None:size-=len(b)
    return h.hexdigest()

def run(*args):
    p=subprocess.run(args,capture_output=True,text=True,timeout=180)
    if p.returncode:raise RuntimeError(str(args[0])+': '+p.stdout[-2000:]+p.stderr[-2000:])
    return p.stdout.strip()

def inventory(root):
    result={}
    for p in sorted(root.rglob('*')):
        m=p.lstat()
        row={'mode':stat.S_IMODE(m.st_mode),'uid':m.st_uid,'gid':m.st_gid}
        if p.is_symlink():row['link']=os.readlink(p)
        elif p.is_file():row.update(bytes=m.st_size,sha256=sha(p))
        elif p.is_dir():continue
        else:raise RuntimeError('Unexpected special file '+str(p))
        result[str(p.relative_to(root))]=row
    return result

def mirror_fsinfo(image):
    """Linux FAT writes update primary advisory hints; keep backup identical."""
    with image.open('r+b',buffering=0) as f:
        f.seek(4194304);b=f.read(512)
        reserved=struct.unpack_from('<H',b,14)[0]
        fatsz=struct.unpack_from('<I',b,36)[0]
        assert b[16]==2 and struct.unpack_from('<HH',b,48)==(1,6)
        f.seek(4194304+512*reserved);fat=f.read(fatsz*512)
        f.seek(4194304+512*(reserved+fatsz));assert f.read(fatsz*512)==fat
        count=(struct.unpack_from('<I',b,32)[0]-reserved-2*fatsz)//b[13]
        free=sum((struct.unpack_from('<I',fat,i*4)[0]&0xfffffff)==0 for i in range(2,count+2))
        f.seek(4194304+512);primary=f.read(512)
        f.seek(4194304+7*512);backup=f.read(512)
        assert primary[:488]==backup[:488] and primary[496:]==backup[496:]
        assert struct.unpack_from('<I',primary,488)[0]==free
        f.seek(4194304+7*512);assert f.write(primary)==512;os.fsync(f.fileno())
        return {'actual_free_clusters':free,'backup_fsinfo_synchronized':True}

def main():
    assert os.geteuid()==0 and I.is_file() and not I.is_symlink()
    assert I.resolve().parent==W and I.stat().st_size==4294967296
    assert sha(I)==BASE
    apk=W/'H728-GameSwitch.apk';assert sha(apk)==APK_SHA
    original_boot=I.open('rb').read(4194304)
    assert original_boot[8196:8204]==b'eGON.BT0'
    loop=run('losetup','--find','--show','--partscan',str(I))
    assert loop.startswith('/dev/loop')
    assert Path(run('losetup','-n','-O','BACK-FILE',loop)).resolve()==I.resolve()
    m1=W/'p1';m2=W/'p2';m1.mkdir(exist_ok=True);m2.mkdir(exist_ok=True)
    checks={};changed=set();removed=[]
    def put(name,data,mode=0o644):
        p=m2/name;p.parent.mkdir(parents=True,exist_ok=True)
        assert not p.is_symlink()
        p.write_bytes(data.encode() if isinstance(data,str) else data)
        os.chmod(p,mode);os.chown(p,0,0);changed.add(name)
    try:
        for n,cmd in [('p1-before',['fsck.vfat','-n',loop+'p1']),('p2-before',['e2fsck','-fn',loop+'p2'])]:
            checks[n]=run(*cmd)
        run('mount','-t','vfat',loop+'p1',str(m1))
        old_p1=inventory(m1)
        assert old_p1['KERNEL']['sha256']=='b482527b4ac808c0bff409859be2a380c682552e06aa85d1ab532246b988f74b'
        assert old_p1['oemsplash-1080.png']['sha256']=='3128f8928f43c1a3d585368052d1f8e3641deb646130758a81ac2d8af89794df'
        stock=run('unsquashfs','-cat',str(m1/'SYSTEM'),'usr/bin/userconfig-setup')
        assert 'false | cp -iRp /usr/config/* /storage/.config/' in stock
        shutil.copyfile(apk,m1/'H728-GameSwitch.apk')
        run('mount','-t','ext4',loop+'p2',str(m2))
        old=inventory(m2)
        grow='.config/h728/firstboot/p3-grow.py'
        grow_sha=sha(m2/grow)
        assert grow_sha=='71543aa27d1188aa69b3fcc34cd3d4077a08406fb6d6593ff01e7d64f6795139'
        assert not (m2/'.config/h728/firstboot/p3-dynamic.done').exists()
        assert os.readlink(m2/'.config/system.d/debug-shell.service')=='/dev/null'
        worker='.config/h728/native-virtualoff/virtualoff.py'
        text=(m2/worker).read_text()
        assert hashlib.sha256(text.encode()).hexdigest()=='2ef5295352a80ef27a29dc3f32e89ea2899420106ecadd194cc97b635f7d4ee6'
        for a,b,n in [
            ('Native virtual-off: H728 s2idle + IR power wake + EmuELEC-first boot.',
             'Native virtual-off: H728 s2idle + IR power wake + Android-first boot.',1),
            ('for name in ("reboottoemuelec",):','for name in ("rebootfromnand",):',1),
            ('/storage/.h728-bin/reboottoemuelec','/storage/.h728-bin/rebootfromnand',2),
            ('if sd_boot_magic() != b"eGON.BT0":','if sd_boot_magic() != b"eGON.OFF":',2),
            ('EmuELEC-first boot policy verification failed','Android-first boot policy verification failed',1),
            ('EmuELEC boot policy verification failed','Android boot policy verification failed',1),
            ('emuelec_default_prepared','android_default_prepared',1),
            ('fresh_emuelec_reboot','fresh_android_reboot',2),
            ('target="emuelec"','target="android"',1),
            ('"wake_target": "emuelec"','"wake_target": "android"',1)]:
            assert text.count(a)==n,(a,text.count(a),n)
            text=text.replace(a,b)
        compile(text,worker,'exec');put(worker,text,0o755)
        # Strengthen the actual accepted SD-only helper before raw header writes.
        backup='.config/h728/poweroff-ab-20261011/backup-manifest.json'
        bm=json.loads((m2/backup).read_text())
        for name in ('rebootfromnand','reboottoemuelec'):
            p=m2/'.h728-bin'/name
            assert sha(p)==bm['files'][name]['sha256']
            t=p.read_text();needle='[ -b "$SD_DEV" ] ||'
            assert t.count(needle)==1
            guard='SD_NAME=${SD_DEV##*/}\n[ "$(cat "/sys/class/block/$SD_NAME/device/type" 2>/dev/null)" = SD ] || exit 1\n'
            t=t.replace(needle,guard+needle)
            put('.h728-bin/'+name,t,0o755)
            bm['files'][name].update(sha256=sha(p),bytes=p.stat().st_size)
            run('/bin/sh','-n',str(p))
        put(backup,json.dumps(bm,indent=2)+'\n')
        service='''[Unit]
Description=H728 restore Android default after firstboot storage initialization
Requires=h728-p3-grow.service
After=local-fs.target userconfig.service h728-p3-grow.service
Before=emuelec-autostart.service emustation.service
RequiresMountsFor=/storage /flash
[Service]
Type=oneshot
ExecStart=/storage/.h728-bin/rebootfromnand
RemainAfterExit=yes
TimeoutStartSec=30
[Install]
WantedBy=multi-user.target
'''
        put('.config/system.d/h728-android-default.service',service)
        wants=m2/'.config/system.d/multi-user.target.wants/h728-android-default.service'
        wants.parent.mkdir(exist_ok=True);assert not wants.exists() and not wants.is_symlink()
        wants.symlink_to('../h728-android-default.service');changed.add(str(wants.relative_to(m2)))
        put('.config/system.d/emuelec-autostart.service.d/20-h728-android-default.conf',
            '[Unit]\nRequires=h728-android-default.service\nAfter=h728-android-default.service\n')
        put('.config/system.d/emustation.service.d/20-h728-android-default.conf',
            '[Unit]\nRequires=h728-android-default.service\nAfter=h728-android-default.service\n')
        # UI NAND quit explicitly keeps Android; regular EE reboot restores BT0.
        hook='''#!/bin/sh
[ "${1:-}" = nand ] || exit 0
: > /run/h728-reboot-android
'''
        put('.config/emulationstation/scripts/quit/98-h728-boot-target.sh',hook,0o755)
        wrapper='''#!/bin/sh
set -eu
if [ "${1:-}" = poweroff ] && [ "$#" = 1 ]; then
 exec /usr/bin/systemctl --no-block start h728-native-virtualoff.service
fi
if [ "${1:-}" = reboot ] && [ "$#" = 1 ]; then
 if [ -e /run/h728-reboot-android ]; then
  /bin/sh /storage/.h728-bin/rebootfromnand
 else
  /bin/sh /storage/.h728-bin/reboottoemuelec
 fi
fi
exec /usr/bin/systemctl "$@"
'''
        put('.h728-bin/systemctl',wrapper,0o755)
        put('.config/h728/native-virtualoff/systemctl-virtualoff',wrapper,0o755)
        for name in ('.h728-bin/systemctl','.config/emulationstation/scripts/quit/98-h728-boot-target.sh'):
            run('/bin/sh','-n',str(m2/name))
        mf='.config/h728/native-virtualoff/manifest.json';man=json.loads((m2/mf).read_text())
        for name in changed:
            p=m2/name
            if name==backup or '/storage/'+name in man['files']:
                man['files']['/storage/'+name]=sha(p)
        man.update(profile='DualBoot',wake_target='android',worker_sha256=sha(m2/worker),
                   revision='android-first-sdpm-20261013',status='offline-verified-user-burn-pending',
                   physical_native_wake='pending-DualBoot-user-test')
        put(mf,json.dumps(man,indent=2)+'\n')
        # Keep the accepted runtime themes; stock sample setup must not add old themes.
        seed='''#!/bin/sh
# Preserve stock defaults without reinstalling unwanted bundled theme copies.
set -eu
find /storage/.config -name '*.sample' -type f | while IFS= read -r sample; do
 relative=${sample#/storage/.config/}
 [ ! -f "/usr/config/$relative" ] || rm -f "$sample"
done
copy_defaults() { false | cp -iRp "$1" "$2" >/dev/null 2>&1 || :; }
for source in /usr/config/*; do
 [ -e "$source" ] || continue
 name=${source##*/}
 case "$name" in
  emuelec|emulationstation)
   mkdir -p "/storage/.config/$name"
   for child in "$source"/*; do
    [ -e "$child" ] || continue
    [ "${child##*/}" = themes ] && continue
    copy_defaults "$child" "/storage/.config/$name/"
   done ;;
  *) copy_defaults "$source" /storage/.config/ ;;
 esac
done
'''
        put('.config/h728/userconfig-clean.sh',seed,0o755)
        put('.config/system.d/userconfig.service.d/20-h728-clean-themes.conf',
            '[Service]\nExecStart=\nExecStart=/bin/sh /storage/.config/h728/userconfig-clean.sh\n')
        run('/bin/sh','-n',str(m2/'.config/h728/userconfig-clean.sh'))
        for p in list((m2/'.h728-bin/playlists/logs').rglob('*.lrtl')):
            assert p.is_file() and not p.is_symlink()
            removed.append(str(p.relative_to(m2)));p.unlink()
        assert len(removed)==43,len(removed)
        assert sha(m2/grow)==grow_sha
        new=inventory(m2)
        differences={p for p in old.keys()|new.keys() if old.get(p)!=new.get(p)}
        assert differences==changed|set(removed),(differences-changed-set(removed),changed-differences)
        (W/'p2-file-delta.json').write_text(json.dumps({'modified_or_added':sorted(changed),'removed_history':removed,'before':{p:old.get(p) for p in differences},'after':{p:new.get(p) for p in differences}},indent=2)+'\n')
        (W/'p2-final-inventory.json').write_text(json.dumps(new,indent=2)+'\n')
        run('sync');run('umount',str(m2));run('umount',str(m1))
        # Only the Allwinner magic changes in the complete boot/MBR region.
        with I.open('r+b',buffering=0) as f:
            f.seek(8196);assert f.read(8)==b'eGON.BT0'
            f.seek(8196);assert f.write(b'eGON.OFF')==8;os.fsync(f.fileno())
        now=I.open('rb').read(4194304)
        assert now[:8196]==original_boot[:8196] and now[8204:]==original_boot[8204:]
        assert now[8196:8204]==b'eGON.OFF'
        fsinfo=mirror_fsinfo(I)
        for n,cmd in [('p1-after',['fsck.vfat','-n',loop+'p1']),('p2-after',['e2fsck','-fn',loop+'p2'])]:
            checks[n]=run(*cmd)
        run('mount','-t','vfat','-o','ro',loop+'p1',str(m1))
        p1=inventory(m1)
        assert {p:m for p,m in p1.items() if p!='H728-GameSwitch.apk'}==old_p1
        assert sha(m1/'H728-GameSwitch.apk')==APK_SHA
        run('mount','-t','ext4','-o','ro,noload',loop+'p2',str(m2))
        assert inventory(m2)==new
        assert not Path(loop+'p3').exists()
        run('umount',str(m2));run('umount',str(m1))
    finally:
        for p in (m2,m1):
            if subprocess.run(['mountpoint','-q',str(p)]).returncode==0:run('umount',str(p))
        run('losetup','-d',loop)
    for n,v in checks.items():(W/(n+'.fsck.txt')).write_text(v+'\n')
    report={'base_sha256':BASE,'image':I.name,'bytes':I.stat().st_size,'sha256':sha(I),
            'boot_magic':'eGON.OFF','boot_other_bytes_identical':True,'p1_preserved':old_p1,
            'apk_sha256':APK_SHA,'p3_initializer_sha256':grow_sha,'initial_p3_absent':True,
            'p2_allowed_file_delta':len(changed),'removed_play_history':len(removed),
            'p2_reopen_full_inventory_pass':True,'checks':{n:0 for n in checks},
            'user_acceptance':'PENDING DualBoot full burn/cold Android/APK/EE IR->Android',
            'physical_sd_android_emmc_modified':False,'fat_fsinfo':fsinfo}
    (W/'DUALBOOT_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    (W/(I.name+'.sha256')).write_text(report['sha256']+'  '+I.name+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
