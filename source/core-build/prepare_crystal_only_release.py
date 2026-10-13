#!/usr/bin/env python3
"""Audit exact H728 Release P2 theme/rollback removal candidates WITHOUT modifying images.
Original USB SD/source snapshot and user game content are untouched.
"""
from pathlib import Path
import subprocess,os,re,json,sys
ROOT=Path(r"C:\Users\SkillGodAK\Desktop\H728")
DB=ROOT/"PRIVATE"/"backup_128g_46"/"_compare_tools"/"cygwin-root"
BIN=DB/"usr"/"sbin"/"debugfs.exe"
ENV=os.environ.copy()
ENV["PATH"]=";".join(str(DB/x) for x in ("usr/bin","usr/sbin","bin"))+";"+ENV.get("PATH","")
BASE=ROOT/"PRIVATE"/"LIVE_SD_CAPTURE_20261011"
IMG=BASE/"p2_clean_dual.raw"
# Only explicit release-sanitization roots: do not remove live SD or core repair.
THEMES=["es-theme-Graphite-OGA","es-theme-EmuELEC-Roleta","es-theme-Spin-Master"]
THEME_DIRS=[f"/.config/{base}/themes/{name}" for base in ("emulationstation","emuelec") for name in THEMES]
CANDIDATES=[
"/.h728-c38-backup",
"/.h728-c38-stage",
"/.h728-backups",
"/.config/h728/poweroff-ab-20261011",
"/.config/h728/powerbridge-backup-20261009",
"/.config/emulationstation/recovery",
"/.config/emulationstation/tmp",
"/.config/emulationstation/pdftmp",
]
def ls(p):
    r=subprocess.run([str(BIN),"-R","ls -p "+p,str(IMG)],env=ENV,capture_output=True,text=True,errors="replace")
    rows=[]
    for line in r.stdout.splitlines():
        a=line.split("/")
        if len(a)<7 or not a[1].isdigit():continue
        if a[5] in (".",".."):continue
        rows.append((a[5],int(a[2],8),int(a[6]) if a[6].isdigit() else 0))
    return rows,("File not found" in r.stderr or "not a directory" in r.stderr)
def walk(root,limit=25000):
    counts={"files":0,"dirs":0,"bytes":0}
    cmds=[]
    def scan(path,recursive_count):
        if recursive_count>128:raise RuntimeError("too deep")
        entries,missing=ls(path)
        if missing:
            if path==root:return
            raise RuntimeError("unexpected missing "+path)
        for name,mode,size in entries:
            p=path.rstrip("/")+"/"+name
            if "\n" in p or '"' in p:raise RuntimeError("dangerous filename "+repr(p))
            if mode&0o170000==0o040000:
                scan(p,recursive_count+1)
            else:
                cmds.append("rm "+('"'+p+'"' if " " in p else p))
                counts["files"]+=1;counts["bytes"]+=size
            if len(cmds)>limit:raise RuntimeError("too many "+root)
        cmds.append("rmdir "+('"'+path+'"' if " " in path else path))
        counts["dirs"]+=1
    scan(root,0)
    return cmds,counts

# Build ONE exact path list using the verified dual cloned parent, then apply
# identically to dual and standalone. The source SD is NEVER a target.
release_roots=THEME_DIRS + [
    "/.config/h728/poweroff-ab-20261011/backup",
    "/.config/h728/powerbridge-backup-20261009",
]
release_files=[
    "/.config/h728/poweroff-ab-20261011/restore-android-5s.sh",
    "/.config/h728/poweroff-ab-20261011/enable-native-ee.sh",
    "/.config/h728/poweroff-ab-20261011/enable-virtualoff.sh",
    "/.config/h728/poweroff-ab-20261011/poweroff_mode.py",
]
commands=[];report=[]
for path in release_roots:
    c,summary=walk(path)
    commands.extend(c)
    report.append(dict(path=path,**summary))
    print("CANDIDATE",path,summary,flush=True)
for path in release_files:
    parent,name=path.rsplit("/",1)
    v,missing=ls(parent)
    if not missing and name in [x[0] for x in v]:
        commands.append("rm "+path)
        report.append(dict(path=path,files=1,dirs=0))
if not (len(commands)>10000 and len(commands)<20000):
    raise RuntimeError(f"unexpected # files {len(commands)}")
cmds=BASE/"work"/"crystal_only_release.debugfs"
cmds.write_text("\n".join(commands)+"\n",encoding="utf-8")
(BASE/"work"/"crystal_only_release_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("COMMAND_FILE_READY",len(commands),cmds,flush=True)
