#!/usr/bin/env python3
"""Generate routing and inventory metadata; never install, evaluate or delete.

Default/check mode reads the public tree and a dated, generated environment
snapshot, so CI needs no private checkout. Explicit capture refreshes that
snapshot and writes the complete reconciliation ONLY outside this repository.
Private-only identities never enter either public generated artifact.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_repository import parse_skill
from eval_tally import canonical_verdict_lines, verdict_token

START = '<!-- generated-skills:start -->'
END = '<!-- generated-skills:end -->'
REPO = Path(__file__).resolve().parents[1]
SKIP = {'.git', '__pycache__', '.pytest_cache'}


def encoded(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n'


def discover(directory):
    try:
        entries=list(directory.iterdir())
    except OSError:
        return None
    return {p.name:p for p in sorted(entries) if (p/'SKILL.md').is_file()}


@lru_cache(maxsize=None)
def repository_identity(root):
    p=subprocess.run(['git','-C',str(root),'rev-parse','--path-format=absolute','--git-common-dir'],capture_output=True,text=True)
    return p.stdout.strip() if p.returncode==0 else None


def fingerprints(directory):
    records=[]
    for p in sorted(directory.rglob('*')):
        if p.is_file() and not SKIP.intersection(p.relative_to(directory).parts):
            records.append([p.relative_to(directory).as_posix(),hashlib.sha256(p.read_bytes()).hexdigest()])
    return {'skill_sha256':hashlib.sha256((directory/'SKILL.md').read_bytes()).hexdigest(),
            'bundle_sha256':hashlib.sha256(encoded(records).encode()).hexdigest(),
            'files':len(records)}


def capture(root, private_root, installed_root, observed_on, install_lock=None):
    public=discover(root/'skills')
    if public is None:
        raise ValueError('public skills directory unavailable')
    private=discover(private_root/'skills')
    installed=discover(installed_root)
    pvt=private or {}; ins=installed or {}
    lock={}
    if install_lock is not None:
        try:
            lock=json.loads(install_lock.read_text()).get('skills',{})
        except (OSError,ValueError):
            lock={}
    details=[]; observations={}
    for name in sorted(set(public)|set(pvt)|set(ins)):
        homes=[]
        for label,repo,skills in [('public',root,public),('private',private_root,pvt)]:
            if name in skills:
                homes.append({'repository':label,'path':str(skills[name]),**fingerprints(skills[name])})
        home_state='unique' if len(homes)==1 else 'ambiguous' if homes else 'unresolved'
        canonical=homes[0]['path'] if len(homes)==1 else None
        install=ins.get(name); state='not-installed' if installed is not None else 'could-not-measure'
        actual=None
        if install:
            actual=fingerprints(install)
            if canonical and (install.resolve()==Path(canonical).resolve() or
                              install.is_symlink() and install.resolve().name==name and
                              repository_identity(Path(canonical).parents[1]) is not None and
                              repository_identity(Path(canonical).parents[1])==repository_identity(install.resolve().parents[1])):
                state='linked-to-canonical'
            elif homes and any(actual['bundle_sha256']==h['bundle_sha256'] for h in homes):
                state='identical-installed-copy'
            else:
                state='divergent-or-unresolved-install'
        detail={'name':name,'canonical_home':canonical,'home_state':home_state,'homes':homes,
                'installed_where':str(install) if install else None,'install_state':state,
                'installed_hashes':actual,'repo_copies_identical':len(homes)>1 and len({h['bundle_sha256'] for h in homes})==1,
                'scope':'public' if name in public else 'personal-only (provisional; private is not proof of scope)',
                'authorship':authorship(root if name in public else private_root,Path(canonical)) if canonical else {'class':'unknown'},
                'eval':eval_status(Path(canonical)) if canonical else {'status':'could-not-measure','reason':'No unique accessible home'},
                'packaging':packaging(Path(canonical)) if canonical else {'status':'could-not-measure','reason':'No unique accessible home'}}
        if not homes and install and name in lock:
            source=lock[name]
            url=source.get('sourceUrl','')
            if source.get('sourceType')=='github' and re.fullmatch(r'https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',url):
                detail.update(canonical_home=url,home_state='unique-from-installer-lock',
                              scope='public (provisional upstream distribution; usage scope unverified)',
                              authorship={'class':'jon-or-agent-attributed' if source.get('source','').startswith('jonhill90/') else 'third-party',
                                          'basis':'Explicit installer provenance; upstream bytes not independently fetched.'},
                              installer_provenance=source,
                              eval=eval_status(install),packaging=packaging(install))
        details.append(detail)
        if name in public:
            # Strict allowlist: never serialize a private name, path, or hash.
            observations[name]={'state':state,'where':'claude-user' if install else None,
                                'skill_matches_public':actual['skill_sha256']==fingerprints(public[name])['skill_sha256'] if actual else None,
                                'repo_home_count':len(homes) if private is not None else None}
    counts={'public_skills':len(public),'private_skills':len(private) if private is not None else None,
            'installed_skills':len(installed) if installed is not None else None,
            'installed_outside_public':len(set(ins)-set(public)) if installed is not None else None,
            'repo_duplicate_names':len(set(public)&set(pvt)) if private is not None else None,
            'third_party_installed':sum(d['authorship'].get('class')=='third-party' and d['installed_where'] is not None for d in details) if installed is not None else None,
            'unresolved_installed':sum(d['home_state'] in {'unresolved','ambiguous'} and d['installed_where'] is not None for d in details) if installed is not None else None}
    return {'observed_on':observed_on,'counts':counts,'public_installs':observations}, {'observed_on':observed_on,'counts':counts,'skills':details}


def eval_status(skill):
    p=skill/'references/eval-result.md'
    if not p.exists():
        return {'status':'no-evals','evidence':None,'reason':'No bundled evaluation record; external coverage not inspected.'}
    try:
        lines=canonical_verdict_lines(p.read_text())
        token=verdict_token(lines[0]) if len(lines)==1 else None
    except (OSError,UnicodeError):
        token=None
    if token not in {'keep','improve','rename','drop','no_effect_observed','scenario_inadequate'}:
        status='could-not-measure'
    else:
        status='has-evals'
    return {'status':status,'evidence':f'skills/{skill.name}/references/eval-result.md',
            'recorded_verdict':token,'reason':'Existing record inspected, not rerun; record presence is not a passing result.'}


def packaging(skill):
    """Static upload-shape audit, not a claim of tested cross-harness behavior."""
    findings=[]
    patterns=[('machine-path',r'/Users/[^\s`]+|/Applications/[^\s`]+|~/[A-Za-z.]'),
              ('cli-dependency',r'(?:`|^\s*)(?:gh|tmux|obsidian|linear|uv|python3|pip|brew|sqlite3|npx) (?:auth|search|list|install|add|run|test|new-session|send-keys|wait-for|version|pr|issue|capture-pane|status|validate|skills|scripts/|/)'),
              ('shell-instructions',r'^```(?:bash|sh|shell|zsh)\s*$'),
              ('external-vault',r'\$AGENT_MEMORY_VAULT'),
              ('external-skill-reference',r'\]\(\.\./[^)]+SKILL\.md\)')]
    # Audit instructions and bundled Markdown references. Do not reinterpret
    # historical eval reports as runtime requirements.
    files=[skill/'SKILL.md']+sorted(p for p in (skill/'references').glob('*.md') if p.name!='eval-result.md')
    for p in files:
        historical=False
        for n,line in enumerate(p.read_text().splitlines(),1):
            if line.startswith('## '):
                historical=line == '## Where this came from'
            if historical:
                continue
            for label,pattern in patterns:
                if re.search(pattern,line):
                    findings.append({'reason':label,'file':f'skills/{skill.name}/'+p.relative_to(skill).as_posix(),'line':n})
    grouped={}
    for finding in findings:
        key=(finding['file'],finding['reason'])
        if key not in grouped:
            grouped[key]={**finding,'occurrences':0}
        grouped[key]['occurrences']+=1
    return {'status':'FAIL' if findings else 'PASS','findings':list(grouped.values()),
            'meaning':'Static upload-only audit: flagged local/CLI assumptions need review; PASS means none detected, not a web execution test.'}


def authorship(root, skill):
    p=subprocess.run(['git','-C',str(root),'log','--reverse','--diff-filter=A','--format=%H|%an','--',f'skills/{skill.name}/SKILL.md'],capture_output=True,text=True)
    first=p.stdout.splitlines()[0] if p.returncode==0 and p.stdout.splitlines() else ''
    commit,_,author=first.partition('|')
    return {'class':'jon-or-agent-attributed' if author.lower() in {'jon hill','jonhill90'} else 'unknown',
            'basis':'Earliest available addition commit; git attribution does not prove absence of upstream copying.',
            'commit':commit or None}


def build(root, snapshot):
    rows=[]
    for name,skill in (discover(root/'skills') or {}).items():
        metadata,_=parse_skill(skill/'SKILL.md')
        installation=snapshot.get('public_installs',{}).get(name,{'state':'could-not-measure','where':None,'repo_home_count':None})
        # No snapshot free text is copied into the manifest: only known states.
        allowed={'not-installed','could-not-measure','linked-to-canonical','identical-installed-copy','divergent-or-unresolved-install'}
        if installation.get('state') not in allowed:
            raise ValueError('invalid environment observation')
        rows.append({'name':name,'canonical_home':f'https://github.com/jonhill90/skills/tree/main/skills/{name}' if installation.get('repo_home_count')==1 else None,
                     'home_state':'unique-at-observation' if installation.get('repo_home_count')==1 else 'ambiguous' if installation.get('repo_home_count',0) and installation['repo_home_count']>1 else 'could-not-measure',
                     'scope':'public','scope_basis':'Current public repository placement; deployment scope may be narrower.',
                     'authorship':authorship(root,skill),'installed':{
                         'state':installation['state'],
                         'where':'claude-user' if installation.get('where')=='claude-user' else None,
                         'skill_matches_public':installation.get('skill_matches_public') if type(installation.get('skill_matches_public')) is bool else None,
                         'repo_home_count':installation.get('repo_home_count') if type(installation.get('repo_home_count')) is int else None},
                     'hashes':fingerprints(skill),'packaging':packaging(skill),'eval':eval_status(skill)})
    return {'schema':1,'generated_by':'scripts/reconcile_skills.py',
            'environment_observed_on':snapshot.get('observed_on') if re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(snapshot.get('observed_on',''))) else 'could-not-measure',
            'environment_counts':{k:v if type(v) is int else None for k,v in snapshot.get('counts',{}).items() if k in {'public_skills','private_skills','installed_skills','installed_outside_public','repo_duplicate_names','third_party_installed','unresolved_installed'}},'skills':rows}


def render(manifest):
    rows=manifest['skills']; lines=[START,'',f"Generated from {len(rows)} current skill bundles and the dated environment observation; do not hand-edit.",
        'Regenerate with `python3 scripts/reconcile_skills.py`; verify with `--check`.',
        'The [machine-readable manifest](docs/skills-reconciliation.json) names evidence and static audit locations.',
        f"Installed observations: {manifest['environment_observed_on']}; refresh explicitly, never interpret this as a live roster.",
        '`claude-user` in the manifest means the user-level Claude skills directory; host paths are omitted.',
        'Packaging PASS = no local coupling detected; FAIL = local/CLI assumptions require review. Web execution is unrun.',
        'Eval status reports existing evidence, not quality approval; missing external coverage remains unknown.','',
        '| Skill | Scope | Installed observation | Upload audit | Eval evidence |','|---|---|---|---|---|']
    for row in rows:
        ev=row['eval'];label=ev['status']
        if ev.get('evidence'):label=f"[{label}]({ev['evidence']})"
        lines.append(f"| [`{row['name']}`](skills/{row['name']}/) | {row['scope']} | {row['installed']['state']} | {row['packaging']['status']} | {label} |")
    counts=manifest['environment_counts']
    lines+=['',f"Private skills observed: {counts.get('private_skills') if counts.get('private_skills') is not None else 'could-not-measure'}; installed outside this public collection: {counts.get('installed_outside_public') if counts.get('installed_outside_public') is not None else 'could-not-measure'}. Private identities are excluded. Installer-attributed third-party entries: {counts.get('third_party_installed') if counts.get('third_party_installed') is not None else 'could-not-measure'}; unresolved installed homes: {counts.get('unresolved_installed') if counts.get('unresolved_installed') is not None else 'could-not-measure'}.", '',END]
    return '\n'.join(lines)


def write_outputs(root, manifest, check=False):
    readme=root/'README.md';text=readme.read_text()
    if text.count(START)!=1 or text.count(END)!=1:
        raise ValueError('README must have exactly one generated-skills section')
    start=text.index(START);end=text.index(END)+len(END)
    outputs={root/'docs/skills-reconciliation.json':encoded(manifest),readme:text[:start]+render(manifest)+text[end:]}
    stale=[]
    for path,value in outputs.items():
        if not path.exists() or path.read_text()!=value:
            stale.append(path.name)
            if not check:path.write_text(value)
    if check and stale:
        print('STALE: '+', '.join(stale));return 1
    print(('Verified' if check else 'Generated')+f" {len(manifest['skills'])} public skill records; changed={len(stale)}")
    return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--capture-private',type=Path)
    parser.add_argument('--installed',type=Path)
    parser.add_argument('--install-lock',type=Path,help='optional installer provenance, inspected only during capture')
    parser.add_argument('--observed-on')
    parser.add_argument('--private-report',type=Path)
    args=parser.parse_args()
    observation=REPO/'docs/skills-environment.json'
    if args.capture_private is not None:
        if args.check or not all([args.installed,args.observed_on,args.private_report]):
            parser.error('capture requires --installed, --observed-on and --private-report; not --check')
        if args.private_report.resolve().is_relative_to(REPO.resolve()):
            parser.error('private report must be outside the public repository')
        snapshot,detail=capture(REPO,args.capture_private,args.installed,args.observed_on,args.install_lock)
        args.private_report.write_text(encoded(detail));args.private_report.chmod(0o600)
        observation.write_text(encoded(snapshot))
    else:
        snapshot=json.loads(observation.read_text())
    return write_outputs(REPO,build(REPO,snapshot),args.check)

if __name__=='__main__':
    raise SystemExit(main())
