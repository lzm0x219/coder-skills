#!/usr/bin/env python3
"""Evaluate fresh-agent artifacts against frozen behavioral contracts.

Run: python3 tests/agent-evals/verify.py WORK_ROOT FROZEN_JSON
This does not launch agents or grade their reasoning; report review is separate.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

def run(args, cwd):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    p = subprocess.run(["rtk", "proxy", *args], cwd=cwd, env=env,
                       capture_output=True, text=True, timeout=60)
    return {"exitCode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

def fix_checks(root, frozen):
    sys.path.insert(0, str(root))
    namespace = {"__name__": "jobs"}
    exec(compile((root / "jobs.py").read_text(), str(root / "jobs.py"), "exec"), namespace)
    Queue = namespace["JobQueue"]
    q = Queue()
    q.enqueue("a", "A", 5)
    q.enqueue("b", "B", 5)
    class Offline(Exception): pass
    def fail(value): raise Offline(value)
    try:
        q.drain(5, fail)
    except Offline:
        pass
    else:
        raise AssertionError("handler error was swallowed")
    assert list(q.pending) == ["a", "b"], "failed/untouched tasks lost"
    seen = []
    assert q.drain(5, seen.append) == 2 and seen == ["A", "B"]
    assert not q.pending

    q.enqueue("a", "old", 10)
    def successor(value):
        seen.append(value)
        q.enqueue("a", "new", 20)
        q.enqueue("c", "later-snapshot", 10)
    assert q.drain(10, successor) == 1
    assert q.pending["a"]["payload"] == "new", "success removed same-key successor"
    assert q.pending["c"]["payload"] == "later-snapshot"
    seen = []
    assert q.drain(19, seen.append) == 1 and seen == ["later-snapshot"]
    assert q.drain(20, seen.append) == 1 and seen[-1] == "new"

    q.enqueue("x", "X", 3)
    q.enqueue("y", "Y", 3)
    seen = []
    def second_fails(value):
        seen.append(value)
        if value == "Y": raise Offline()
    try: q.drain(3, second_fails)
    except Offline: pass
    else: raise AssertionError("second failure was swallowed")
    assert seen == ["X", "Y"] and list(q.pending) == ["y"]

    original = ast.parse(frozen["worktreeInputs"]["fix/test_jobs.py"])
    current = ast.parse((root / "test_jobs.py").read_text())
    functions = lambda tree: {n.name: ast.dump(n) for n in ast.walk(tree)
                              if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")}
    old, new = functions(original), functions(current)
    assert all(new.get(k) == v for k, v in old.items()), "original public tests modified"
    return {"behaviorChecks": "retry/error/order/successor/future/snapshot", "passed": True}

NODE_REFACTOR = r"""
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const api = require(path.resolve(process.argv[1], 'index.cjs'));
assert.deepEqual(Object.keys(api).sort(), ['createFeed','makeInvoice']);
const calls = [];
const inv = api.makeInvoice([{priceCents:105,quantity:2}],.1,(...a)=>calls.push(a));
assert.deepEqual(inv,{totalCents:231,label:'CNY 2.31'});
assert(Object.isFrozen(inv));
assert.deepEqual(calls,[['CNY 2.31',231]]);
assert.equal(api.makeInvoice([],0).label,'CNY 0.00');
assert.equal(api.makeInvoice([{priceCents:1,quantity:1}],.5).totalCents,2);
let effect = 0;
assert.throws(()=>api.makeInvoice(null,-1,()=>effect++),e=>e instanceof TypeError && e.message==='lines');
assert.throws(()=>api.makeInvoice([{priceCents:-1,quantity:1}],-1,()=>effect++),e=>e instanceof RangeError && e.message==='rate');
assert.throws(()=>api.makeInvoice([{priceCents:1,quantity:1},{priceCents:1,quantity:-1}],0,()=>effect++),e=>e instanceof RangeError && e.message==='line');
assert.equal(effect,0);
const marker = new Error('record failed');
assert.throws(()=>api.makeInvoice([],0,()=>{throw marker}),e=>e===marker);
(async()=>{
 const feed=api.createFeed(), seen=[];
 const a=x=>seen.push('a'+x), b=x=>seen.push('b'+x);
 const off=feed.subscribe(a); feed.subscribe(b);
 assert.equal(feed.publish(1),true); off();
 feed.subscribe(x=>seen.push('late'+x));
 await new Promise(r=>setImmediate(r));
 assert.deepEqual(seen,['b1']);
 feed.publish(2);
 await new Promise(r=>setImmediate(r));
 assert.deepEqual(seen,['b1','b2','late2']);
 feed.publish(3); feed.close(); feed.close();
 await new Promise(r=>setImmediate(r));
 assert.deepEqual(seen,['b1','b2','late2']);
 assert.equal(feed.publish(4),false);
 assert.throws(()=>feed.subscribe(()=>{}),/closed/);
 console.log('PASS frozen public shape, user edit, errors/effects and feed lifecycle');
})().catch(e=>{console.error(e);process.exitCode=1});
"""

NODE_REVIEW = r"""
const assert=require('node:assert/strict'),path=require('node:path');
const root=process.argv[1];
const read=require(path.resolve(root,'src/invoices.cjs')).readInvoice;
const db=new Map([['i1',{id:'i1',tenantId:'t1',amountCents:500}]]);
assert.deepEqual(read(db,{tenantId:'t2'},'i1'),{id:'i1',amountCents:500});
const resolve=require(path.resolve(root,'src/assets.cjs')).resolveAsset;
assert.throws(()=>resolve('/srv/assets','../assets-private/secret'),/outside/);
assert.throws(()=>resolve('/srv/assets','/etc/passwd'),/outside/);
assert.equal(resolve('/srv/assets','nested/../logo.png'),'/srv/assets/logo.png');
const out=[],err=[];
require(path.resolve(root,'src/export.cjs')).exportRows([{id:1}],{write:x=>out.push(x)},{write:x=>err.push(x)});
assert.equal(out[0],'preparing export\n'.replace('\\n','\n'));
assert.throws(()=>JSON.parse(out[0]));
console.log('PASS gold defects reproduced and asset protection confirmed');
"""

def master_checks(root, frozen):
    routes = json.loads((root / "routes.json").read_text())
    expected = frozen["gold"]["master"]["routes"]
    assert len(routes) == len(expected), "route count mismatch"
    assert len({x["id"] for x in routes}) == len(routes), "duplicate route IDs"
    for item in routes:
        primary = item["primary"]
        if primary in {"general", "常规能力"}:
            primary = "fallback"
        assert primary == expected[item["id"]], f"wrong route: {item['id']}"
        assert item["mode"] == "recommendation-only", "recommendation scope changed"
        assert item["additional"] == [], "unneeded second capability"
        assert item["reason"], "route rationale absent"
    assert (root / "REQUESTS.json").read_text() == frozen["worktreeInputs"]["master/REQUESTS.json"]
    observed = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    assert observed <= {"REQUESTS.json", "routes.json", "REPORT.md"}, "extra output outside recommendation"
    return {"passed": True, "matchedRoutes": len(expected), "limit": "five prompts in one fresh context; no task execution or installation test"}

API_PROBE = r"""
import json,sys,warnings
from pathlib import Path
warnings.filterwarnings("ignore", category=DeprecationWarning)
from openapi_spec_validator import validate_spec
from jsonschema import Draft202012Validator,RefResolver,FormatChecker
root=Path(sys.argv[1])
spec=json.loads((root/"openapi.json").read_text())
validate_spec(spec)
def deref(s):
    if "$ref" not in s: return s
    v=spec
    for k in s["$ref"][2:].split("/"): v=v[k]
    return deref(v)
creates=[v["post"] for v in spec["paths"].values() if "post" in v and "requestBody" in v["post"]]
assert len(creates)==1
schema=creates[0]["requestBody"]["content"]["application/json"]["schema"]
val=Draft202012Validator(schema,resolver=RefResolver.from_schema(spec),format_checker=FormatChecker())
good={"items":[{"sku":"SKU-1","quantity":1}]}
val.validate(good)
bad=[{},{"items":[]},{"items":[{"quantity":1}]},{"items":[{"sku":"SKU-1"}]},
     {"items":[{"sku":"SKU-1","quantity":0}]},{"items":[{"sku":"SKU-1","quantity":-1}]},
     {"items":[{"sku":"SKU-1","quantity":1.5}]},{"items":[{"sku":"SKU-1","quantity":"1"}]},
     {**good,"tenantId":"other-tenant"}]
assert all(not val.is_valid(x) for x in bad),"missing input refusal"
states=[]
for path,item in spec["paths"].items():
    if "get" not in item: continue
    for response in item["get"].get("responses",{}).values():
        c=response.get("content",{}).get("application/json",{})
        if "schema" in c:
            s=deref(c["schema"])
            if "oneOf" in s: states+=s["oneOf"]
terminal={b.get("properties",{}).get("status",{}).get("const"):b.get("required",[]) for b in states}
assert "result" in terminal.get("succeeded",[]),"success result not required in this carrier"
assert "error" in terminal.get("failed",[]),"failure error not required in this carrier"
print(json.dumps({"passed":True,"format":"official OpenAPI validator","inputRefusals":len(bad),
                  "terminalConstraints":["succeeded/result","failed/error"],
                  "limit":"schema evidence only; external effects/dedup/client recovery reviewed separately"}))
"""

def api_checks(root, api_python=None):
    if not (root / "openapi.json").is_file():
        return {"passed": False, "error": "OpenAPI carrier missing"}
    interpreter = api_python or (root / ".venv/bin/python")
    if not Path(interpreter).is_file():
        return {"passed": None, "error": "validator interpreter unavailable; supply --api-python"}
    result = run([str(interpreter), "-c", API_PROBE, str(root)], root)
    if result["exitCode"] == 0:
        result["schemaChecks"] = json.loads(result["stdout"])
    return result

def evaluate(root, frozen, api_python=None):
    result = {}
    try:
        result["fix"] = fix_checks(root / "fix", frozen)
    except Exception as exc:
        result["fix"] = {"passed": False, "error": type(exc).__name__ + ": " + str(exc)}
    result["fix"]["publicTests"] = run([sys.executable,"-m","unittest","-v"],root/"fix")
    result["refactor"] = run(["node","-e",NODE_REFACTOR,str(root/"refactor")],root/"refactor")
    notes = (root/"refactor/customer-notes.txt").read_text()
    result["refactor"]["userNotesPreserved"] = notes == frozen["worktreeInputs"]["refactor/customer-notes.txt"]
    result["refactor"]["publicTests"] = run(["node","test.cjs"],root/"refactor")
    result["reviewGold"] = run(["node","-e",NODE_REVIEW,str(root/"review")],root/"review")
    result["reviewGold"]["sourceUnchanged"] = all(
        (root/name).read_text() == text
        for name,text in frozen["worktreeInputs"].items()
        if name.startswith("review/")
    )
    try:
        result["master"] = master_checks(root / "master", frozen)
    except Exception as exc:
        result["master"] = {"passed": False, "error": type(exc).__name__ + ": " + str(exc)}
    result["limits"] = "Report content, route choices, API semantics and structure benefits require separate artifact review."
    result["api"] = api_checks(root / "api", api_python)
    return result

def edge_evaluate(root, frozen, tsc=None):
    """Check edge-case inputs and observable controls; semantic grading is separate."""
    import tempfile
    result = {}
    for role, files in frozen["fixtures"].items():
        unchanged = all((root / role / rel).is_file() and
                        (root / role / rel).read_text() == text
                        for rel, text in files.items())
        report = root / role / "REPORT.md"
        status = root / role / "result.json"
        structured = json.loads(status.read_text()) if status.is_file() else {}
        result[role] = {"inputsUnchanged": unchanged,
                        "reportPresent": report.is_file(),
                        "resultFieldsPresent": all(k in structured for k in
                            ("status", "scope", "findings", "checks", "limits")),
                        "reportCharacters": len(report.read_text()) if report.is_file() else 0}

    def check(role, name, command, expected, contains=None):
        observation = run(command, root / role)
        observation["passed"] = (observation["exitCode"] == expected if expected == 0
                                 else observation["exitCode"] != 0)
        if contains:
            observation["passed"] &= contains in observation["stdout"] + observation["stderr"]
        result[role][name] = observation

    check("fix", "environmentControl", [sys.executable, "-B", "reproduce.py"], 1, "warehouse_bridge")
    check("fix", "localTests", [sys.executable, "-B", "-m", "unittest", "-v"], 0)
    check("refactor", "oldFailure", [sys.executable, "-B", "test_legacy.py"], 1, "CNY")
    check("refactor", "currentContract", [sys.executable, "-B", "-c",
          "from source import receipt; assert receipt([])=='USD 0.00'; "
          "assert receipt([100,25])=='USD 1.25'; "
          "from baseline import receipt as old; assert old([100])=='CNY 1.00'"], 0)
    check("review", "baselineConsumer", [sys.executable, "-B", "baseline/consumer.py"], 0)
    check("review", "targetConsumer", [sys.executable, "-B", "target/consumer.py"], 1, "JSONDecodeError")
    check("review", "equivalentProtection", [sys.executable, "-B", "-c", r'''
import importlib.util
from pathlib import Path
for version in ('baseline', 'target'):
    spec=importlib.util.spec_from_file_location(version, Path(version)/'assets.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert module.resolve_asset('/srv/assets','nested/../logo.png')=='/srv/assets/logo.png'
    for name in ('../assets-private/secret','/etc/passwd','../../other'):
        try: module.resolve_asset('/srv/assets',name)
        except ValueError as exc: assert str(exc)=='outside'
        else: raise AssertionError('escape accepted')
print('PASS valid path and three refusals for both versions')
'''], 0)

    sdk = root / "sdk"
    result["sdk"]["declarationChecks"] = []
    compiler = Path(tsc) if tsc else None
    if compiler is None or not compiler.is_file() or not (sdk / "candidate.api.ts").is_file():
        result["sdk"]["declarationChecks"].append({"passed": False, "error": "supply --tsc and candidate.api.ts"})
    else:
        with tempfile.TemporaryDirectory(prefix="coder-sdk-probe-") as directory:
            probe = Path(directory)
            (probe / "candidate.api.ts").write_text((sdk / "candidate.api.ts").read_text())
            old = frozen["fixtures"]["sdk"]["old-consumer.ts"].replace("'./v1.api'", "'./candidate.api'")
            consumers = {"old": old, "new": """
import { iterate, Row } from './candidate.api';
const rows: readonly Row[] = [{id:'a',value:'A'}];
const cursor: IterableIterator<Row> = iterate(rows);
const zero: IterableIterator<Row> = iterate(rows,{limit:0});
const step: IteratorResult<Row> = cursor.next();
if (!step.done) { const id: string = step.value.id; void id; }
cursor.return?.(); zero.return?.();
""", "bad-limit": "import { iterate } from './candidate.api'; iterate([], {limit:'1'});",
                "bad-row-mutation": "import { iterate } from './candidate.api'; const step=iterate([]).next(); if(!step.done) step.value.id='changed';",
                "bad-result-mutation": "import { list } from './candidate.api'; list([]).push({id:'a',value:'A'});"}
            for name, content in consumers.items():
                (probe / (name + ".ts")).write_text(content)
                observation = run([str(compiler), "--noEmit", "--strict", "--target", "ES2022",
                                   "--module", "commonjs", name + ".ts"], probe)
                rejection = name.startswith("bad-")
                observation["passed"] = ((observation["exitCode"] != 0 and "error TS" in observation["stdout"])
                                         if rejection else observation["exitCode"] == 0)
                observation["name"] = name
                result["sdk"]["declarationChecks"].append(observation)
    result["limits"] = "Input preservation and actual controls/types only; report semantics, coverage and evidence references require separate review. No SDK implementation is executed."
    return result

def edge_passed(result):
    for role in ("fix", "refactor", "review", "sdk"):
        case = result[role]
        if not all(case[key] for key in ("inputsUnchanged", "reportPresent", "resultFieldsPresent")):
            return False
        observations = [v for v in case.values() if isinstance(v, dict) and "passed" in v]
        observations += case.get("declarationChecks", [])
        if not all(item.get("passed") for item in observations):
            return False
    return True

def main():
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path)
    parser.add_argument("frozen", nargs="?", type=Path)
    parser.add_argument("--replay", action="store_true",
                        help="Recreate captured inputs and first-pass artifacts from cases.json/run.json")
    parser.add_argument("--api-python", type=Path,
                        help="Python with openapi-spec-validator and jsonschema")
    parser.add_argument("--edge", action="store_true", help="Check the separate edge-case round")
    parser.add_argument("--tsc", type=Path, help="TypeScript compiler for edge SDK declarations")
    args = parser.parse_args()
    if args.replay:
        here = Path(__file__).resolve().parent
        prefix = "edge-" if args.edge else ""
        frozen = json.loads((here / (prefix + "cases.json")).read_text())
        record = json.loads((here / (prefix + "run.json")).read_text())
        if args.edge and hashlib.sha256((here / "edge-cases.json").read_bytes()).hexdigest() != record["frozenInputsSha256"]:
            raise ValueError("frozen edge inputs SHA mismatch")
        with tempfile.TemporaryDirectory(prefix="coder-agent-replay-") as directory:
            root = Path(directory).resolve()
            files = ({role + "/" + rel: text for role, inputs in frozen["fixtures"].items()
                      for rel, text in inputs.items()} if args.edge else dict(frozen["worktreeInputs"]))
            for name, case in record["cases"].items():
                for rel, text in case.get("artifacts", {}).items():
                    files[name + "/" + rel] = text
            for rel, text in files.items():
                path = (root / rel).resolve()
                if not path.is_relative_to(root):
                    raise ValueError("artifact path escapes replay root")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            for name, case in record["cases"].items():
                for rel, expected in case.get("artifactHashes", {}).items():
                    path = (root / name / rel).resolve()
                    if not path.is_relative_to(root) or not path.is_file():
                        raise ValueError("missing or unsafe captured artifact")
                    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                        raise ValueError("captured artifact SHA mismatch: " + name + "/" + rel)
            result = (edge_evaluate(root, frozen, args.tsc) if args.edge
                      else evaluate(root, frozen, args.api_python))
    else:
        if args.root is None or args.frozen is None:
            parser.error("root and frozen required unless --replay")
        frozen = json.loads(args.frozen.read_text())
        result = (edge_evaluate(args.root.resolve(), frozen, args.tsc) if args.edge
                  else evaluate(args.root.resolve(), frozen, args.api_python))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.edge:
        return 0 if edge_passed(result) else 1
    checks = [result["fix"].get("passed"),
              result["fix"]["publicTests"]["exitCode"] == 0,
              result["refactor"]["exitCode"] == 0,
              result["refactor"]["userNotesPreserved"],
              result["refactor"]["publicTests"]["exitCode"] == 0,
              result["reviewGold"]["exitCode"] == 0,
              result["reviewGold"]["sourceUnchanged"],
              result["master"].get("passed"),
              result["api"].get("exitCode") == 0]
    return 0 if all(checks) else 1

if __name__ == "__main__":
    raise SystemExit(main())
