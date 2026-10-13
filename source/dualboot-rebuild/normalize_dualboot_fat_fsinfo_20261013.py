"""Normalize only verified backup FAT FSInfo advisory hints in owned IMG files."""
from pathlib import Path
import argparse,hashlib,json,os,struct,sys
from fat32_readonly import Fat32

def digest(p,offset=0,size=None):
    h=hashlib.sha256()
    with p.open('rb') as f:
        f.seek(offset)
        while size is None or size:
            b=f.read(8*1024*1024 if size is None else min(size,8*1024*1024))
            if not b:
                assert size is None;break
            h.update(b)
            if size is not None:size-=len(b)
    return h.hexdigest()

def main():
    a=argparse.ArgumentParser();a.add_argument('--image',type=Path,required=True);a.add_argument('--validation',type=Path,required=True);args=a.parse_args()
    p=args.image.resolve();v=args.validation.resolve()
    assert p.is_file() and not p.is_symlink() and p.suffix=='.img' and v.parent==p.parent
    allowed=(r'I:\H728_BUILD\H728_EmuELEC_4.8_Crystal_20261013\TEST_DualBoot_AndroidFirst_20261013', '/home/ubuntu/h728-cold-start-20261012/dualboot-20261013')
    assert str(p.parent) in allowed
    r=json.loads(v.read_text());old='3f462ad95912b1c90a9c19687aabb033fefef945179651439556e40f3c436820'
    assert r['sha256']==old and p.stat().st_size==4294967296 and digest(p)==old
    f=Fat32(p,4194304,strict_mirrors=False);prior=f.audit();f.close()
    with p.open('r+b',buffering=0) as f:
        f.seek(4194304);b=f.read(512)
        assert struct.unpack_from('<HH',b,48)==(1,6)
        f.seek(4194304+6*512);assert f.read(512)==b
        f.seek(4194304+512);primary=f.read(512)
        f.seek(4194304+7*512);backup=f.read(512)
        assert primary[:488]==backup[:488] and primary[496:]==backup[496:]
        assert struct.unpack_from('<I',primary,488)[0]==prior['free_clusters']
        assert primary!=backup
        f.seek(4194304+7*512);assert f.write(primary)==512;os.fsync(f.fileno())
    f=Fat32(p,4194304);assert f.audit()==prior;f.close()
    assert digest(p,0,4194304)==r['boot_sha256']
    assert digest(p,2151677952,2143289344)==r['p2_sha256']
    new=digest(p)
    r.update(sha256=new,prior_pre_fsinfo_sha256=old,
             backup_fsinfo_synced=True,actual_free_clusters=prior['free_clusters'],
             fat_strict_independent_pass=True,boot_p2_unchanged_by_fsinfo=True)
    v.write_text(json.dumps(r,indent=2)+'\n')
    (p.parent/(p.name+'.sha256')).write_text(new+'  '+p.name+'\n')
    proof={'prior_sha256':old,'sha256':new,'changed_region':'P1 backup FSInfo sector7 hints only','primary_hints':list(struct.unpack_from('<II',primary,488)),'prior_backup_hints':list(struct.unpack_from('<II',backup,488)),'fat_files_and_free_count_unchanged':True,'boot_p2_unchanged':True}
    (p.parent/'FAT_FSINFO_NORMALIZATION.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof),flush=True)

if __name__=='__main__':main()
