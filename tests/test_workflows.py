import copy
import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import entra_toolkit as toolkit

AS_OF = '2026-09-07T00:00:00Z'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.users = toolkit.load_users(ROOT / 'samples/users.json')
        self.memberships = json.loads((ROOT / 'samples/memberships.json').read_text())

    def classify(self, users=None):
        return toolkit.stale_report(self.users if users is None else users, 90, toolkit.timestamp(AS_OF))

    def test_sample_statuses_and_inclusive_boundary(self):
        self.assertEqual([r['status'] for r in self.classify()], [
            'recentActivity', 'staleCandidate', 'unknownActivity', 'disabled', 'staleCandidate'])

    def test_timestamp_timezone_required(self):
        with self.assertRaises(ValueError):
            toolkit.timestamp('2026-09-07T00:00:00')

    def test_equivalent_timezone_boundary(self):
        self.users[0]['lastSuccessfulSignInDateTime'] = '2026-06-09T02:00:00+02:00'
        self.assertEqual(self.classify()[0]['status'], 'staleCandidate')

    def test_invalid_timelines(self):
        for field, value in [('createdDateTime', '2027-01-01T00:00:00Z'),
                             ('lastSuccessfulSignInDateTime', '2027-01-01T00:00:00Z'),
                             ('lastSuccessfulSignInDateTime', '2024-01-01T00:00:00Z')]:
            users = copy.deepcopy(self.users)
            users[0][field] = value
            self.assertEqual(self.classify(users)[0]['status'], 'invalidTimeline')

    def test_nonpositive_threshold(self):
        with self.assertRaises(ValueError):
            toolkit.stale_report(self.users, 0, toolkit.timestamp(AS_OF))

    def test_report_preserves_disabled_and_unknown(self):
        report = toolkit.user_report(self.users)
        self.assertEqual(len(report), 5)
        self.assertIsNone(report[2]['lastSuccessfulSignInDateTime'])
        self.assertFalse(report[3]['accountEnabled'])

    def test_review_is_pending(self):
        rows = toolkit.review_packet(self.users, self.memberships)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['userPrincipalName'], 'active@example.com')
        self.assertTrue(all(row['decision'] == 'Pending' for row in rows))

    def test_invalid_review_references(self):
        bad = copy.deepcopy(self.memberships)
        bad[0]['userId'] = 'missing'
        with self.assertRaises(ValueError):
            toolkit.review_packet(self.users, bad)
        with self.assertRaises(ValueError):
            toolkit.review_packet(self.users, self.memberships * 2)

    def test_csv_formula_escaping(self):
        for text in ['=1+1', '+cmd', '-2', '@SUM(1)', '  =1', '\t=1']:
            self.assertEqual(toolkit.csv_cell(text), "'" + text)
        self.assertEqual(toolkit.csv_cell('user@example.com'), 'user@example.com')

    def test_invalid_user_input(self):
        variants = [self.users * 2, {}, [None]]
        for key, value in [('accountEnabled', 'false'), ('id', ''),
                           ('lastSuccessfulSignInDateTime', 'bad')]:
            bad = copy.deepcopy(self.users)
            bad[0][key] = value
            variants.append(bad)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'users.json'
            for bad in variants:
                path.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    toolkit.load_users(path)

    def test_empty_input(self):
        self.assertEqual(toolkit.user_report([]), [])
        self.assertEqual(self.classify([]), [])
        self.assertEqual(toolkit.review_packet([], []), [])

    def command(self, workflow, output):
        return [sys.executable, str(ROOT / 'python/entra_toolkit.py'), workflow,
                '--users', str(ROOT / 'samples/users.json'), '--memberships',
                str(ROOT / 'samples/memberships.json'), '--as-of', AS_OF,
                '--output', str(output)]

    def test_cli_all_workflows_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            for workflow in ('users', 'stale', 'review'):
                output = Path(directory) / workflow
                subprocess.run(self.command(workflow, output), check=True, capture_output=True)
                before = output.read_bytes()
                rerun = subprocess.run(self.command(workflow, output), capture_output=True)
                self.assertNotEqual(rerun.returncode, 0)
                self.assertEqual(output.read_bytes(), before)
                if workflow == 'review':
                    rows = list(csv.DictReader(io.StringIO(output.read_text())))
                    self.assertEqual(len(rows), 2)
                else:
                    self.assertEqual(len(json.loads(output.read_text())), 5)

    @unittest.skipUnless(shutil.which('pwsh'), 'PowerShell runtime is not installed')
    def test_powershell_sample_parity(self):
        with tempfile.TemporaryDirectory() as directory:
            for workflow in ('users', 'stale', 'review'):
                output = Path(directory) / workflow
                command = ['pwsh', '-NoProfile', '-File', str(ROOT / 'powershell/Invoke-EntraWorkflow.ps1'),
                           '-Workflow', workflow, '-UsersPath', str(ROOT / 'samples/users.json'),
                           '-MembershipsPath', str(ROOT / 'samples/memberships.json'),
                           '-AsOf', AS_OF, '-OutputPath', str(output)]
                subprocess.run(command, check=True, capture_output=True)
                if workflow == 'review':
                    actual = list(csv.DictReader(io.StringIO(output.read_text(encoding='utf-8-sig'))))
                    expected = toolkit.review_packet(self.users, self.memberships)
                else:
                    actual = json.loads(output.read_text(encoding='utf-8-sig'))
                    expected = toolkit.user_report(self.users) if workflow == 'users' else self.classify()
                    if workflow == 'stale':
                        for row in actual + expected:
                            row['asOf'] = toolkit.timestamp(row['asOf']).isoformat()
                self.assertEqual(actual, expected)
                before = output.read_bytes()
                self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
                self.assertEqual(before, output.read_bytes())


if __name__ == '__main__':
    unittest.main()
