from pathlib import Path
import subprocess, json, hashlib
r=Path(__file__).parent
results={}
for name in ['old-failure','user-edits','readonly','missing-private']:
 p=r/name
 z=subprocess.run(['node','consumer.cjs'],cwd=p,text=True,capture_output=True)
 (p/'after.log').write_text(z.stdout+z.stderr); results[name]={'consumer_exit':z.returncode}
 if name!='readonly':
  script="const a=require(process.argv[1]),b=require(process.argv[2]); const inputs=[[],[{price:10,quantity:2}],[{price:-2,quantity:3}],[{price:0.1,quantity:3}]]; for(const x of inputs)for(const k of Object.keys(a)){if(a[k](x)!==b[k](x))throw Error(k);} console.log('differential PASS');"
  z=subprocess.run(['node','-e',script,str(r/'originals'/name/'index.cjs'),str(p/'index.cjs')],text=True,capture_output=True)
  (p/'differential.log').write_text(z.stdout+z.stderr); results[name]['differential_exit']=z.returncode
 for file in ['unrelated.cjs','runtime.cjs']:
  if (p/file).exists():
   z=subprocess.run(['node',file],cwd=p,text=True,capture_output=True)
   (p/(file+'.after.log')).write_text(z.stdout+z.stderr); results[name][file+'_exit']=z.returncode
paths=[p for p in r.glob('*/*') if p.is_file()]
(r/'after.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2))
before=json.loads((r/'before.json').read_text()); after=json.loads((r/'after.json').read_text())
results['readonly']['index_unchanged']=before['readonly/index.cjs']==after['readonly/index.cjs']
results['old-failure']['old_failure_unchanged']=before['old-failure/unrelated.cjs']==after['old-failure/unrelated.cjs']
(r/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
