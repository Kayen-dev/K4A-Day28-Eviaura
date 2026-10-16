import copy
import unittest
from eval_gate import evaluate

class GateTests(unittest.TestCase):
    def setUp(self):
        # Synthetic fixture validates gate logic only. This is not a VBot benchmark.
        self.data={'evidence_kind':'measured','levels':{k:{'samples':50,'baseline_score':1,'candidate_score':.96} for k in ['L1','L2','L3','L4','L5']},'peak_p95_model_ttft_seconds':2.9,'max_background_seconds':599,'restore_rto_seconds':14000,'restore_rpo_seconds':3500}
        for k in ['cross_tenant_leaks','unapproved_external_writes','sandbox_egress_successes']:self.data[k]=0
        for k in ['dataset_reviewed','peak_load_from_vietnam','acl_revocation_tested','quota_race_tested','sandbox_cleanup_tested','evidence_links_reviewed']:self.data[k]=True
    def test_empty_fails(self):self.assertFalse(evaluate({})['pass'])
    def test_valid_report_passes(self):self.assertTrue(evaluate(self.data)['pass'])
    def test_each_level_must_pass(self):
        self.data['levels']['L3']['candidate_score']=.94
        self.assertFalse(evaluate(self.data)['pass'])
    def test_measurements_and_safety_fail_closed(self):
        for key,value in [('peak_p95_model_ttft_seconds',3.1),('restore_rpo_seconds',3601),('cross_tenant_leaks',1),('unapproved_external_writes',False),('evidence_kind','synthetic')]:
            with self.subTest(key=key):
                d=copy.deepcopy(self.data);d[key]=value
                self.assertFalse(evaluate(d)['pass'])
    def test_missing_or_nonfinite_score(self):
        for value in [None,float('nan'),float('inf'),True]:
            with self.subTest(value=value):
                d=copy.deepcopy(self.data);d['levels']['L2']['candidate_score']=value
                self.assertFalse(evaluate(d)['pass'])

if __name__=='__main__':unittest.main()
