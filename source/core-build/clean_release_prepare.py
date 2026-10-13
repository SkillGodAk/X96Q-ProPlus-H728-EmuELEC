#!/usr/bin/env python3
"""Remove only verified tracing sources on isolated copies; keep AXP323 and UART fixes."""
from pathlib import Path
import hashlib,json,shutil
S=Path('/home/ubuntu/h728-cold-start-20261012')
O=Path('/home/ubuntu/build/emuelec/build.EmuELEC-H728.aarch64-4/build')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 backup=S/'clean-release-diagnostic-source-before-20261013'
 assert not backup.exists(),'Clean preparation already exists'
 scan=json.loads(Path('/tmp/h728-clean-source-scan.json').read_text())
 replacements={};deletes=[];retained={}
 for group,base_name in [('uboot','u-boot-2026.07'),('atf','atf-b5de74a685fb73b784e45bbbd18dd9a0c528d8b2')]:
  tree=S/(group+'-trace-source');base=O/base_name
  for item in scan[group]:
   name=item['name'];p=tree/name;q=base/name
   if name.startswith(('include/generated/','include/config/')):continue
   assert sha(p)==item['current_sha'],str(p)
   if item['before_sha'] is None:
    assert 'h728_bootstage' in name,name
    deletes.append(p);continue
   assert sha(q)==item['before_sha'],str(q)
   if group=='atf' and name=='drivers/ti/uart/aarch64/16550_console.S':
    assert item['current_sha']=='003950b955e4f92d7d4cf0f0a1537231807cee7c1b8d6d3400678ca6af82e6e3'
    retained[str(p.relative_to(S))]=sha(p);continue
   data=q.read_bytes()
   if group=='atf' and name=='plat/allwinner/sun55i_a523/platform.mk':
    data+=b'\nifeq (${H728_UART_FLUSH_BOUNDED},1)\n$(eval $(call add_define,H728_UART_FLUSH_BOUNDED))\nendif\n'
   replacements[p]=data
 k=S/'kernel-handoff-source';base=O/'linux-6.18.38'
 pins={
 'arch/arm64/kernel/head.S':('74c72eebb761980921ef92e2c7f5780e3ec7e67082653a51c1972c4d966e9509','805d3f0d2aef717c0c2ce5ae0e7f9add65cf1f669d1791cc34b4765a7c1caa3a'),
 'arch/arm64/kernel/setup.c':('21c7f0b110f1cdf7a5aac935fd4078c34ccc40a89a140f0f8c0337bd0b02501d','d0572642224a071b14de5fdd61243d2086016faf3c29765817fd459b503110d6'),
 'init/main.c':('17024aefbfbabb7a787f17995aa900ae94dd91f3814220bc4249c72ebee1d3f3','621696308d23f74d385c711f18386e90171cb912a0a6821e7345b31fddb35618'),
 'drivers/base/dd.c':('8edcbb7ce27f429f1cbfd6ce364ddee734f1bd5accd08ce7725303585247e085','6f92acf937930623b6ff7fe55927305f4e23b59a115c16b505b13b65420488cc')}
 for name,(old,new) in pins.items():
  p=k/name;q=base/name;assert sha(p)==old and sha(q)==new,name
  replacements[p]=q.read_bytes()
 deletes.append(k/'include/linux/h728_linux_gpio_trace.h')
 assert deletes[-1].is_file()
 for name,pin in [('drivers/regulator/axp20x-regulator.c','74df776fdd134a5e067ff0809e70cd98fa8d16d936797145ba79825a7de0d6b5'),('.config','e73aeb9a99ae78ac41c3e54bbca8ffc47b900714b128e74f2c04374767cc48d7'),('drivers/mfd/axp20x.c','1f25593cc5114fa5154284de6b7fd2d2fc7847a57d88223443c13f72b045de88'),('arch/arm64/boot/dts/allwinner/sun55i-h728-x96qpro+.dts','b6b8409eac39928df35f03151e4366b78c9f7b00239d0e27fc1ebf306a99a753')]:
  p=k/name;assert sha(p)==pin,name;retained[str(p.relative_to(S))]=pin
 backup.mkdir()
 for p in [*replacements,*deletes]:
  saved=backup/p.relative_to(S);saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
 try:
  for p,data in replacements.items():p.write_bytes(data)
  for p in deletes:p.unlink()
  checked={str(p.relative_to(S)):sha(p) for p in replacements}
  checked.update(retained)
  for p in replacements:
   assert 'h728_bootstage' not in p.read_text() and 'h728_linux_stage' not in p.read_text(),str(p)
  report={'changed_and_retained_sha256':checked,'deleted_trace_headers':[str(p.relative_to(S)) for p in deletes],'kernel_config_unchanged':True,'axp323_fix_unchanged':True,'uart_bound_fix_retained':True,'original_builder_written':False}
  (S/'clean-release-source-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 except BaseException:
  for p in [*replacements,*deletes]:shutil.copy2(backup/p.relative_to(S),p)
  raise
 print('CLEAN_RELEASE_SOURCE_PREPARATION_PASS')
if __name__=='__main__':main()
