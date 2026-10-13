"""Exercise real systemd ordering and actual image shell policy on owned fixtures."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, tempfile

W=Path('/home/ubuntu/h728-cold-start-20261012/dualboot-20261013')
I=W/'H728_EmuELEC_4.8_Crystal_DualBoot_20261013.img'

def run(*a,check=True):
    p=subprocess.run(a,capture_output=True,text=True,timeout=60)
    if check and p.returncode:raise RuntimeError(str(a[0])+':'+p.stderr[-1500:]+p.stdout[-1500:])
    return p

def main():
    assert os.geteuid()==0 and (W/'DUALBOOT_VALIDATION.json').is_file()
    loop=run('losetup','--read-only','--find','--show','--partscan',str(I)).stdout.strip()
    assert loop.startswith('/dev/loop')
    assert Path(run('losetup','-n','-O','BACK-FILE',loop).stdout.strip()).resolve()==I.resolve()
    m=W/'test-readonly';m.mkdir(exist_ok=True)
    report={}
    try:
        run('mount','-o','ro,noload',loop+'p2',str(m))
        with tempfile.TemporaryDirectory(prefix='h728-dualboot-policy-',dir=W) as d:
            d=Path(d);(d/'usr/config/emuelec/themes/SkillGodAK').mkdir(parents=True)
            (d/'usr/config/emulationstation/themes/Stock').mkdir(parents=True)
            (d/'usr/config/emuelec/emuelec.conf').write_text('default')
            (d/'usr/config/emulationstation/input.cfg').write_text('input')
            (d/'usr/config/test.sample').write_text('new sample')
            (d/'storage/.config/emuelec/themes/Crystal').mkdir(parents=True)
            (d/'storage/.config/emuelec/emuelec.conf').write_text('accepted')
            (d/'storage/.config/test.sample').write_text('old sample')
            seed=(m/'.config/h728/userconfig-clean.sh').read_text()
            seed=seed.replace('/usr/config',str(d/'usr/config')).replace('/storage/.config',str(d/'storage/.config'))
            script=d/'seed.sh';script.write_text(seed);run('/bin/sh',str(script))
            assert (d/'storage/.config/emuelec/emuelec.conf').read_text()=='accepted'
            assert (d/'storage/.config/emulationstation/input.cfg').read_text()=='input'
            assert (d/'storage/.config/test.sample').read_text()=='new sample'
            assert not (d/'storage/.config/emuelec/themes/SkillGodAK').exists()
            assert not (d/'storage/.config/emulationstation/themes/Stock').exists()
            report['real_shell_userconfig_defaults_preserved_and_old_themes_excluded']=True
            # Run the actual wrapper with fixture-local helpers/systemctl.
            log=d/'calls';(d/'bin').mkdir()
            for name in ('rebootfromnand','reboottoemuelec'):
                p=d/'bin'/name;p.write_text('#!/bin/sh\necho '+name+' >> '+str(log)+'\n');p.chmod(0o755)
            sysctl=d/'bin/sysctl';sysctl.write_text('#!/bin/sh\necho "systemctl $*" >> '+str(log)+'\n');sysctl.chmod(0o755)
            wrapper=(m/'.h728-bin/systemctl').read_text().replace('/storage/.h728-bin',str(d/'bin')).replace('/usr/bin/systemctl',str(sysctl)).replace('/run/h728-reboot-android',str(d/'android'))
            p=d/'wrapper';p.write_text(wrapper);p.chmod(0o755)
            cases=[]
            for action,android,expected in [('reboot',False,['reboottoemuelec','systemctl reboot']),('reboot',True,['rebootfromnand','systemctl reboot']),('poweroff',False,['systemctl --no-block start h728-native-virtualoff.service']),('status',False,['systemctl status'])]:
                log.unlink(missing_ok=True);(d/'android').unlink(missing_ok=True)
                if android:(d/'android').touch()
                run('/bin/sh',str(p),action);assert log.read_text().splitlines()==expected
                cases.append({'action':action,'android_quit':android,'calls':expected})
            report['actual_wrapper_cases']=cases
            # Real systemd graph from production units; replace only external work.
            prefix='h728-dualboot-audit-'
            names={k:prefix+k+'.service' for k in ['grow','default','auto','es','user']}
            mapping={'h728-p3-grow.service':names['grow'],'h728-android-default.service':names['default'],'emuelec-autostart.service':names['auto'],'emustation.service':names['es'],'userconfig.service':names['user']}
            events=d/'events';fail=d/'fail';done=d/'done'
            grow=(m/'.config/system.d/h728-p3-grow.service').read_text()
            default=(m/'.config/system.d/h728-android-default.service').read_text()
            for a,b in mapping.items():grow=grow.replace(a,b);default=default.replace(a,b)
            grow=grow.replace('RequiresMountsFor=/storage','').replace('ConditionPathExists=!/storage/.config/h728/firstboot/p3-dynamic.done','ConditionPathExists=!'+str(done))
            grow=grow.replace('ExecStart=/usr/bin/python3 /storage/.config/h728/firstboot/p3-grow.py',"ExecStart=/bin/sh -c 'echo grow >> "+str(events)+"; test ! -e "+str(fail)+" && touch "+str(done)+"'")
            default=default.replace('RequiresMountsFor=/storage /flash','').replace('ExecStart=/storage/.h728-bin/rebootfromnand',"ExecStart=/bin/sh -c 'echo android-default >> "+str(events)+"'")
            units={names['grow']:grow,names['default']:default,names['user']:'[Service]\nType=oneshot\nExecStart=/bin/true\n'}
            for k in ['auto','es']:
                units[names[k]]='[Unit]\nRequires='+names['default']+'\nAfter='+names['default']+'\n[Service]\nType=oneshot\nExecStart=/bin/sh -c \'echo '+k+' >> '+str(events)+"'\n"
            root=Path('/run/systemd/system');outcomes=[]
            try:
                for n,t in units.items():assert not (root/n).exists();(root/n).write_text(t)
                run('systemctl','daemon-reload')
                for case in ['firstboot','grow-failure','already-initialized']:
                    run('systemctl','stop',*units);run('systemctl','reset-failed',*units,check=False)
                    for p in [events,fail,done]:p.unlink(missing_ok=True)
                    if case=='grow-failure':fail.touch()
                    if case=='already-initialized':done.touch()
                    result=run('systemctl','start',names['auto'],names['es'],check=False)
                    rows=events.read_text().splitlines()
                    if case=='firstboot':assert result.returncode==0 and rows[:2]==['grow','android-default'] and set(rows[2:])=={'auto','es'}
                    elif case=='grow-failure':assert result.returncode!=0 and rows==['grow']
                    else:assert result.returncode==0 and rows[0]=='android-default' and set(rows[1:])=={'auto','es'}
                    outcomes.append({'case':case,'events':rows,'returncode':result.returncode})
            finally:
                run('systemctl','stop',*units,check=False)
                for n in units:(root/n).unlink(missing_ok=True)
                run('systemctl','daemon-reload');run('systemctl','reset-failed',*units,check=False)
            report['real_systemd_firstboot_and_failure_gate']=outcomes
    finally:
        if run('mountpoint','-q',str(m),check=False).returncode==0:run('umount',str(m))
        run('losetup','-d',loop)
    (W/'POLICY_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DUALBOOT_REAL_SHELL_AND_SYSTEMD_POLICY_PASS',json.dumps(report),flush=True)

if __name__=='__main__':main()
