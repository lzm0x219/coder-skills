from pathlib import Path
import subprocess,hashlib,json
r=Path(__file__).parent
results={}
for check in ['wrong-check','correct-check']:
 for side in ['before','after']:
  z=subprocess.run(['node',str(r/(check+'.cjs')),str(r/side/'index.cjs')],capture_output=True,text=True)
  key=check+'-'+side
  (r/(key+'.log')).write_text(z.stdout+z.stderr)
  results[key]={'exit':z.returncode}
(r/'results.json').write_text(json.dumps(results,indent=2))
(r/'fingerprints.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['before','after'] for p in (r/d).glob('*.cjs')},indent=2))
print(json.dumps(results,indent=2))
