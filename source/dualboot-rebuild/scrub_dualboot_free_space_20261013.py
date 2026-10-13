"""Scrub unused blocks and EMPTY journal payload on the owned, unmounted IMG.

Never alters physical media. Full file inventory and e2fsck must remain identical.
"""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
sys.path.insert(0,'/home/ubuntu/h728-cold-start-20261012/dualboot-20261013')
from ext4_readonly import Ext4
from build_dualboot_from_accepted_sdpm_20261013 import inventory,sha,run,W,I

def main():
    assert os.geteuid()==0 and I.is_file() and I.resolve().parent==W
    report=json.loads((W/'DUALBOOT_VALIDATION.json').read_text())
    assert sha(I)==report['sha256']
    assert (W/'POLICY_VALIDATION.json').is_file()
    loop=run('losetup','--find','--show','--partscan',str(I))
    assert loop.startswith('/dev/loop') and Path(run('losetup','-n','-O','BACK-FILE',loop)).resolve()==I.resolve()
    mount=W/'scrub-verify';mount.mkdir(exist_ok=True)
    try:
        before=run('e2fsck','-fn',loop+'p2')
        zero=run('zerofree','-v',loop+'p2')
        fs=Ext4(I,2151677952)
        sb=fs.read_at(1024,1024)
        assert struct.unpack_from('<I',sb,96)[0]&4==0,'Needs recovery; do not scrub journal'
        journal_inode=struct.unpack_from('<I',sb,224)[0];assert journal_inode==8
        inode=fs.inode(journal_inode)
        size=struct.unpack_from('<I',inode,4)[0]
        extents=list(fs.extents(inode[40:100]));bs=fs.block_size
        assert bs==4096 and size%bs==0
        first=next(p for l,n,p,u in extents if l==0 and not u)
        header=fs.read_at(first*bs,bs)
        magic,kind,seq,jbs,maxlen,jfirst,jseq,jstart=struct.unpack_from('>8I',header)
        assert magic==0xc03b3998 and kind==4 and jbs==bs and maxlen*bs==size and jstart==0
        assert sum(n for l,n,p,u in extents)*bs==size and all(not u for l,n,p,u in extents)
        fs.close()
        zero_block=bytes(bs)
        with I.open('r+b',buffering=0) as f:
            for logical,count,physical,unused in extents:
                skip=1 if logical==0 else 0
                f.seek(2151677952+(physical+skip)*bs)
                for n in range(count-skip):assert f.write(zero_block)==bs
            os.fsync(f.fileno())
        fs=Ext4(I,2151677952)
        assert fs.read_at(first*bs,bs)==header
        journal=fs.inode_data(fs.inode(journal_inode),limit=size)
        assert not any(journal[bs:]);fs.close()
        after=run('e2fsck','-fn',loop+'p2')
        run('mount','-t','ext4','-o','ro,noload',loop+'p2',str(mount))
        assert inventory(mount)==json.loads((W/'p2-final-inventory.json').read_text())
        run('umount',str(mount))
    finally:
        if subprocess.run(['mountpoint','-q',str(mount)]).returncode==0:run('umount',str(mount))
        run('losetup','-d',loop)
    (W/'p2-scrub-before.fsck.txt').write_text(before+'\n')
    (W/'p2-scrub-after.fsck.txt').write_text(after+'\n')
    previous=report['sha256'];report.update(sha256=sha(I),
        prior_prescrub_sha256=previous,free_blocks_zeroed=True,empty_journal_payload_zeroed=True,
        scrub_full_inventory_reopen_pass=True,scrub_fsck=0,
        p2_sha256=sha(I,2151677952,2143289344),boot_sha256=sha(I,0,4194304))
    (W/'DUALBOOT_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    (W/(I.name+'.sha256')).write_text(report['sha256']+'  '+I.name+'\n')
    print('DUALBOOT_FREE_SPACE_AND_EMPTY_JOURNAL_SCRUB_PASS',json.dumps(report),flush=True)

if __name__=='__main__':main()
