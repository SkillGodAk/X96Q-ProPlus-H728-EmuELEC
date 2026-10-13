#!/usr/bin/env python3
"""Rebuild a clean Standalone release on owned loop-backed files, never an SD."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,re,shutil,stat,struct,subprocess,tarfile,zipfile
S=Path('/home/ubuntu/h728-cold-start-20261012')
W=S/'clean-image-20261013'
INPUT=S/'accepted-live-release-input.tar'
IMAGE=W/'H728_EmuELEC_4.8_Crystal_Standalone_ColdFix_20261013.img'
SIZE=4294967296
SYSTEM_SHA='0a97c8324dcaa132a09e2dcccf0661cd5a0fa8d22cb8d72db757dcefbf085816'
KERNEL_SHA='467b19f1e002f5fe5fede19deed8cfca22d68bd3c0db4db775164939ded03427'
DTB_SHA='f652512c72aa30464517662300d6acaa3267481b6a1192c2c12c0649ad1a937e'
FACTORY_SHA='264d4e4f2486d849051af93b239ca6716d7f3d2580428d9c928503132768f1e2'
OEM_SPLASH_SHA='3128f8928f43c1a3d585368052d1f8e3641deb646130758a81ac2d8af89794df'
def sha(p):
 with p.open('rb') as f:
  h=hashlib.sha256()
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
def run(*args):
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(str(args[0])+': '+p.stdout[-2000:]+p.stderr[-2000:])
 return p.stdout.strip()
def remove(root,name,audit):
 p=root/name
 assert p.parent.resolve().is_relative_to(root.resolve()),name
 if p.is_symlink():p.unlink();audit.append(name)
 elif p.is_dir():shutil.rmtree(p);audit.append(name)
 elif p.exists():p.unlink();audit.append(name)
def file_inventory(root):
 result={}
 for p in sorted(root.rglob('*')):
  rel=str(p.relative_to(root));st=p.lstat()
  if p.is_symlink():result[rel]={'link':os.readlink(p),'mode':stat.S_IMODE(st.st_mode)}
  elif p.is_file():result[rel]={'bytes':st.st_size,'sha256':sha(p),'mode':stat.S_IMODE(st.st_mode)}
 return result
def main():
 assert os.geteuid()==0 and not W.exists()
 assert sha(INPUT)=='ef9f8982aa9051ea5bc4097fb4fe6b8af97d301f66a4f5959cdbb97f263cdae9'
 assert sha(S/'KERNEL-CLEAN-AXP323')==KERNEL_SHA
 assert sha(S/'UBOOT-CLEAN-RELEASE.bin')=='3aaf1fd4648f0e77ec36f735804e2f47271eda2b352b2d1c12025c93d9037bd4'
 W.mkdir();source=W/'source';source.mkdir()
 with tarfile.open(INPUT) as archive:
  for m in archive.getmembers():
   n=PurePosixPath(m.name)
   assert not n.is_absolute() and '..' not in n.parts and n.parts[0] in ('storage','flash'),m.name
   assert not (m.isdev() or m.isfifo()),m.name
   if m.islnk():assert '..' not in PurePosixPath(m.linkname).parts and not PurePosixPath(m.linkname).is_absolute()
 run('tar','--numeric-owner','--same-permissions','-xf',str(INPUT),'-C',str(source))
 storage=source/'storage';flash=source/'flash'
 # Early init reads /flash before user configuration is mounted. A P2-only
 # splash cannot replace the embedded fallback at this stage.
 assert sha(storage/'.config/splash/splash-1080.png')==OEM_SPLASH_SHA
 assert sha(flash/'SYSTEM')==SYSTEM_SHA and sha(flash/'sun55i-h728-x96qpro+.dtb')==DTB_SHA
 assert sha(flash/'extlinux/extlinux.conf')=='e8da4acde7c6d4844aecd18e719cf3ce102204bfb6f8502e347e7f1e445415c1'
 # These source bytes are already fully verified and extracted; release neither embeds tar nor live state.
 INPUT.unlink()
 removed=[]
 private=['.ssh','.cache','.config/pulse','.config/emulationstation/gamelists','.config/emulationstation/collections',
 '.config/emulationstation/recovery','.config/emulationstation/tmp','.config/retroarch/savefiles',
 '.config/retroarch/saves','.config/retroarch/states','.config/retroarch/screenshots','.config/retroarch/playlists',
 '.config/h728/wifi-identity/identities','.config/h728/poweroff-ab-20261011/backup',
 '.config/h728/es-l10n/rollback','.config/h728/power-led',
 '.config/h728/firstboot/p3-dynamic.started','.config/h728/firstboot/p3-dynamic.done','.config/h728/firstboot/p3-dynamic.log',
 '.config/emuelec/ip.txt','.config/emulationstation/imagecache.db',
 '.config/system.d/multi-user.target.wants/debug-shell.service',
 '.config/system.d/h728-android-default.service','.config/system.d/h728-android-default.timer',
 '.config/system.d/timers.target.wants/h728-android-default.timer','.h728-bin/h728-powerbridge-request',
 '.config/emulationstation/scripts/quit/99-h728-powerbridge.sh']
 for n in private:remove(storage,n,removed)
 # Old editor copies and diagnostics are not runtime payloads. Keep real core fallback files.
 for p in list(storage.rglob('*')):
  if not p.exists() and not p.is_symlink():continue
  if p.name=='__pycache__' or p.name.endswith(('~','.bak','.backup','.log','.jsonl')) or '.before-' in p.name or '.pre-' in p.name or p.name.endswith('.incoming.xml'):
   remove(storage,str(p.relative_to(storage)),removed)
  elif p.parent==storage/'.config/h728' and (p.name.startswith('cold-start-') or p.name.startswith('diag-')):
   remove(storage,str(p.relative_to(storage)),removed)
 first=storage/'.config/h728/firstboot'
 assert sha(first/'p3-grow.py')=='71543aa27d1188aa69b3fcc34cd3d4077a08406fb6d6593ff01e7d64f6795139'
 assert sha(first/'factory-eeroms.zip')==FACTORY_SHA
 manifest=json.loads((first/'factory-eeroms-manifest.json').read_text())
 assert len(manifest['files'])==43 and len(manifest['directories'])==123
 assert manifest['payload_sha256']==FACTORY_SHA
 with zipfile.ZipFile(first/'factory-eeroms.zip') as z:
  assert set(z.namelist())==set(manifest['files'])|{n+'/' for n in manifest['directories']}
  for name,meta in manifest['files'].items():
   data=z.read(name);assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
 # Remove credentials from active user configuration, never print their values.
 cleared=[]
 for p in storage.rglob('*'):
  if p.is_symlink() or not p.is_file() or p.stat().st_size>300000 or p.suffix not in ('.cfg','.conf','.ini'):continue
  try:text=p.read_text()
  except (UnicodeError,OSError):continue
  def scrub(m):
   key=m[1].strip().lower()
   if key in ('wifi.ssid','wifi.key','wifi.password','global.retroachievements.username','global.retroachievements.password','cheevos_username','cheevos_password','scraperuser','scraperpassword','screenscraperuser','screenscraperpass','usercreds'):
    cleared.append(str(p.relative_to(storage))+':'+key)
    quoted=m[2].strip().startswith('"');return m[1]+'= '+('""' if quoted else '')
   return m[0]
  new=re.sub(r'(?m)^([^#;\n=]+)=([^\n]*)$',scrub,text)
  if new!=text:p.write_text(new)
 # ES and RetroArch use traditional Chinese by default; preserve accepted theme and performance.
 settings=storage/'.config/emulationstation/es_settings.cfg'
 txt=settings.read_text()
 assert 'name="Language" value="zh_TW"' in txt and 'name="ThemeSet" value="Crystal"' in txt
 # Setup has no game entries in a new card; begin with all platforms rather than remembered user position.
 txt=txt.replace('name="LastSystem" value="setup"','name="LastSystem" value="all"')
 settings.write_text(txt)
 for p in storage.rglob('retroarch.cfg'):
  if p.is_symlink():continue
  text=p.read_text();text=re.sub(r'(?m)^user_language = "[0-9]+"$', 'user_language = "11"',text);p.write_text(text)
 for d in ['roms','savefiles','savestates','playlists','.cache','.config/h728/wifi-identity/identities']:
  (storage/d).mkdir(parents=True,exist_ok=True)
 # Runtime guard: actual active shutdown entry and standby worker remain.
 wrapper=storage/'.config/h728/native-virtualoff/systemctl-virtualoff'
 assert (storage/'.h728-bin/systemctl').read_bytes()==wrapper.read_bytes()
 assert stat.S_IMODE(wrapper.stat().st_mode)==0o755
 worker=(storage/'.config/h728/native-virtualoff/virtualoff.py').read_text()
 assert 'target="emuelec"' in worker and 'def enqueue_reboot():' in worker and 'REBOOT_QUEUED = False' in worker
 assert (storage/'.config/h728/poweroff-ab-20261011/mode').read_text().strip()=='native-ee-virtualoff-v1-test'
 assert sha(storage/'.config/h728/native-virtualoff/sunxi-cir.ko')=='ec15d44d7647f032322235d28c9427835936cda7931e68079924aafa23839488'
 for name in ['.config/h728/es-l10n/emulationstation','.config/h728/front-led/front_led.py','.config/h728/bluetooth-audio/audio-route.py','.config/h728/wifi-identity/stable_mac.py','.h728-bin/select_core.py','.h728-bin/emuelecRunEmu.sh','.h728-bin/h728-game-static.sh']:
  assert (storage/name).is_file(),name
 grow=(storage/'.config/system.d/h728-p3-grow.service').read_text()
 assert os.readlink(storage/'.config/system.d/debug-shell.service')=='/dev/null','Keep debug-shell masked'
 assert 'After=local-fs.target userconfig.service' in grow and 'Before=emuelec-autostart.service emustation.service' in grow
 for unit in ('emustation','emuelec-autostart'):
  data=(storage/f'.config/system.d/{unit}.service.d/10-h728-p3-grow.conf').read_text()
  assert 'Requires=h728-p3-grow.service' in data and 'After=h728-p3-grow.service' in data
 # Source capture contains no ROMs. Payload media must be themes/assets, never private games.
 assert not list((storage/'roms').iterdir())
 inventory=file_inventory(storage)
 (W/'clean-storage-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 (W/'sanitization-audit.json').write_text(json.dumps({'removed_paths':sorted(set(removed)),'cleared_credential_key_names':cleared,'private_cache_not_captured':True,'roms_bios_saves_not_captured':True},indent=2)+'\n')
 print('CLEAN_PAYLOAD_FACTORY_43_AND_PRIVACY_PASS',len(inventory),flush=True)
 # Fresh MBR and new filesystems: no copying live dirty filesystem metadata or unallocated user sectors.
 header=bytearray(512);header[510:512]=b'\x55\xaa'
 for index,(ptype,start,size) in enumerate(((0x0c,8192,4194304),(0x83,4202496,4186112))):
  o=446+index*16;header[o]=0x80 if index==0 else 0;header[o+1:o+4]=b'\xfe\xff\xff';header[o+4]=ptype;header[o+5:o+8]=b'\xfe\xff\xff';struct.pack_into('<II',header,o+8,start,size)
 with IMAGE.open('xb') as f:
  f.truncate(SIZE);f.write(header);f.seek(8192);f.write((S/'UBOOT-CLEAN-RELEASE.bin').read_bytes());f.flush();os.fsync(f.fileno())
 loop=run('losetup','--find','--show','--partscan',str(IMAGE))
 assert loop.startswith('/dev/loop') and Path(run('losetup','-n','-O','BACK-FILE',loop)).resolve()==IMAGE.resolve()
 m1=W/'mount-p1';m2=W/'mount-p2';m1.mkdir();m2.mkdir()
 try:
  run('mkfs.vfat','-F','32','-s','32','-i','07102211','-n','EMUELEC',loop+'p1')
  run('mkfs.ext4','-F','-b','4096','-I','256','-N','65536','-L','STORAGE','-U','c520a133-832f-425e-a83a-8c679362a15c','-E','lazy_itable_init=0,lazy_journal_init=0',loop+'p2')
  run('mount','-t','vfat',loop+'p1',str(m1));run('mount','-t','ext4',loop+'p2',str(m2))
  shutil.copyfile(S/'KERNEL-CLEAN-AXP323',m1/'KERNEL');shutil.copyfile(flash/'SYSTEM',m1/'SYSTEM')
  shutil.copyfile(flash/'sun55i-h728-x96qpro+.dtb',m1/'sun55i-h728-x96qpro+.dtb')
  (m1/'extlinux').mkdir();shutil.copyfile(flash/'extlinux/extlinux.conf',m1/'extlinux/extlinux.conf')
  shutil.copyfile(storage/'.config/splash/splash-1080.png',m1/'oemsplash-1080.png')
  run('rsync','-aHAX','--numeric-ids',str(storage)+'/',str(m2)+'/')
  run('sync');run('umount',str(m1));run('umount',str(m2))
  checks={}
  for name,command in [('p1',['fsck.vfat','-n',loop+'p1']),('p2',['e2fsck','-fn',loop+'p2'])]:
   p=subprocess.run(command,capture_output=True,text=True);(W/(name+'-fsck.txt')).write_text(p.stdout+p.stderr)
   assert p.returncode==0,(name,p.stdout,p.stderr);checks[name]=p.returncode
  run('mount','-t','vfat','-o','ro',loop+'p1',str(m1));run('mount','-t','ext4','-o','ro,noload',loop+'p2',str(m2))
  assert sha(m1/'KERNEL')==KERNEL_SHA and sha(m1/'SYSTEM')==SYSTEM_SHA and sha(m1/'sun55i-h728-x96qpro+.dtb')==DTB_SHA
  assert sha(m1/'oemsplash-1080.png')==OEM_SPLASH_SHA
  actual=file_inventory(m2)
  assert all(actual.get(n)==v for n,v in inventory.items()),'Copied payload differs after reopen'
  assert not Path(loop+'p3').exists()
  run('umount',str(m1));run('umount',str(m2))
 finally:
  for m in (m1,m2):
   if subprocess.run(['mountpoint','-q',str(m)]).returncode==0:run('umount',str(m))
  run('losetup','-d',loop)
 assert IMAGE.stat().st_size==SIZE
 with IMAGE.open('rb') as f:
  mbr=f.read(512);assert mbr[478:510]==bytes(32)
  f.seek(2151677952+1024);sb=f.read(1024);assert 1024<<struct.unpack_from('<I',sb,24)[0]==4096
 report={'profile':'Standalone','image':IMAGE.name,'bytes':SIZE,'sha256':sha(IMAGE),'kernel_sha256':KERNEL_SHA,'system_sha256':SYSTEM_SHA,'dtb_sha256':DTB_SHA,'bootloader_sha256':sha(S/'UBOOT-CLEAN-RELEASE.bin'),'atf_sha256':sha(S/'ATF-CLEAN-RELEASE.bin'),'p2_block_bytes':4096,'factory_files':43,'factory_directories':123,'factory_zip_sha256':FACTORY_SHA,'filesystem_checks':checks,'copied_payload_reopen_hashes_verified':len(inventory),'initial_p3_absent':True,'diagnostic_boot_codes_removed':True,'firstboot_bootstrap_dependency_preserved':True,'sd_modified':False,'android_emmc_modified':False,'hardware_acceptance':'PENDING user full burn; diagnostic AXP323 kernel cold USER PASS'}
 (W/'CLEAN_IMAGE_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
 (W/(IMAGE.name+'.sha256')).write_text(report['sha256']+'  '+IMAGE.name+'\n')
 print('CLEAN_STANDALONE_FULL_IMAGE_OFFLINE_PASS',json.dumps(report),flush=True)
if __name__=='__main__':main()
