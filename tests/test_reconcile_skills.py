"""Inventory metadata tests; these do not execute any skill or behavioral eval."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('reconcile', pathlib.Path(__file__).parents[1]/'scripts/reconcile_skills.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class Reconciliation(unittest.TestCase):
    def skill(self, root, name, body='Think carefully.', extra=''):
        p=root/'skills'/name; p.mkdir(parents=True)
        (p/'SKILL.md').write_text(f'---\nname: {name}\ndescription: Fixture purpose.\n---\n{body}\n{extra}')
        return p

    def test_private_names_never_enter_public_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d); pub=root/'public'; private=root/'private'; installed=root/'installed';installed.mkdir()
            a=self.skill(pub,'visible'); b=self.skill(private,'private-canary')
            (installed/'visible').symlink_to(a);(installed/'private-canary').symlink_to(b)
            observation,detail=m.capture(pub,private,installed,'2026-09-07')
            encoded=json.dumps(observation)
            self.assertNotIn('private-canary',encoded);self.assertNotIn(str(root),encoded)
            self.assertEqual(observation['counts']['private_skills'],1)
            self.assertEqual(observation['public_installs']['visible']['state'],'linked-to-canonical')
            self.assertEqual(len(detail['skills']),2)

    def test_missing_environment_is_not_zero_skills(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);self.skill(root,'visible')
            observation,_=m.capture(root,root/'absent-private',root/'absent-installed','2026-09-07')
            self.assertIsNone(observation['counts']['private_skills'])
            self.assertEqual(observation['public_installs']['visible']['state'],'could-not-measure')

    def test_duplicate_different_bundles_and_installed_copies(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);pub=root/'public';private=root/'private';installed=root/'installed';installed.mkdir()
            self.skill(pub,'same');self.skill(private,'same',body='Different.')
            self.skill(root/'stage','same');(installed/'same').symlink_to(root/'stage/skills/same')
            observation,detail=m.capture(pub,private,installed,'2026-09-07')
            self.assertEqual(observation['counts']['repo_duplicate_names'],1)
            self.assertEqual(detail['skills'][0]['home_state'],'ambiguous')
            self.assertFalse(detail['skills'][0]['repo_copies_identical'])
            self.assertIsNone(m.build(pub,observation)['skills'][0]['canonical_home'])

    def test_installed_only_home_uses_explicit_installer_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);pub=root/'public';private=root/'private';installed=root/'installed';installed.mkdir()
            self.skill(pub,'visible');(private/'skills').mkdir(parents=True)
            foreign=self.skill(root/'upstream','foreign-canary');(installed/'foreign-canary').symlink_to(foreign)
            lock=root/'lock.json';lock.write_text(json.dumps({'skills':{'foreign-canary':{'source':'upstream/foreign-canary','sourceType':'github','sourceUrl':'https://github.com/upstream/foreign-canary.git'}}}))
            observation,detail=m.capture(pub,private,installed,'2026-09-07',lock)
            self.assertEqual(observation['counts']['unresolved_installed'],0)
            self.assertEqual(observation['counts']['third_party_installed'],1)
            row=next(r for r in detail['skills'] if r['name']=='foreign-canary')
            self.assertEqual(row['canonical_home'],'https://github.com/upstream/foreign-canary.git')
            self.assertNotIn('foreign-canary',json.dumps(observation))

    def test_eval_blindness_not_promoted_to_has_evals(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);p=self.skill(root,'visible');(p/'references').mkdir()
            f=p/'references/eval-result.md';f.write_text('**Verdict: could_not_measure**\n')
            self.assertEqual(m.eval_status(p)['status'],'could-not-measure')
            f.write_text('**Verdict: keep**\n');self.assertEqual(m.eval_status(p)['status'],'has-evals')
            f.unlink();self.assertEqual(m.eval_status(p)['status'],'no-evals')

    def test_static_packaging_reports_dependencies_with_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);p=self.skill(root,'visible',body='Run `gh pr list` in a terminal.')
            self.assertEqual(m.packaging(p)['status'],'FAIL')
            (p/'SKILL.md').write_text('---\nname: visible\ndescription: D\n---\nCompare the two supplied documents.\n')
            self.assertEqual(m.packaging(p)['status'],'PASS')

    def test_historical_cli_example_is_not_a_runtime_requirement(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            p=self.skill(root,'visible',body='Compare supplied evidence.\n## Where this came from\nSomeone ran `gh auth status` in an old incident.')
            self.assertEqual(m.packaging(p)['status'],'PASS')

    def test_snapshot_extra_fields_cannot_leak_into_public_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);self.skill(root,'visible')
            snap={'observed_on':'private-canary','counts':{'private-name':'private-canary'},
                  'public_installs':{'visible':{'state':'could-not-measure','where':'private-canary','private_name':'private-canary'}}}
            text=json.dumps(m.build(root,snap))
            self.assertNotIn('private-canary',text)
            self.assertIn('could-not-measure',m.render(m.build(root,snap)))

    def test_render_deterministic_and_stale_check_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);self.skill(root,'visible');(root/'docs').mkdir();(root/'state').mkdir()
            snapshot={'observed_on':'2026-09-07','counts':{},'public_installs':{}}
            a=m.build(root,snapshot);self.assertEqual(a,m.build(root,snapshot))
            (root/'README.md').write_text('# Test\n\n'+m.START+'\n'+m.END+'\n')
            self.assertEqual(m.write_outputs(root,a,check=False),0)
            self.assertEqual(m.write_outputs(root,a,check=True),0)
            (root/'skills/visible/SKILL.md').write_text('---\nname: visible\ndescription: Changed\n---\nBody\n')
            self.assertEqual(m.write_outputs(root,m.build(root,snapshot),check=True),1)

if __name__=='__main__':unittest.main()
