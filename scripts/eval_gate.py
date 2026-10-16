"""Check supplied measured results. Does not call models or generate benchmark evidence."""
import json, sys, math

def evaluate(data):
    failures=[]
    if data.get('evidence_kind')!='measured':failures.append('Measured evidence required')
    for level in ['L1','L2','L3','L4','L5']:
        r=data.get('levels',{}).get(level,{})
        values=[r.get('baseline_score'),r.get('candidate_score')]
        valid=all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and 0<=x<=1 for x in values)
        count=r.get('samples',0)
        if type(count) is not int or count<50 or not valid or values[0]<=0 or values[1]/values[0]<.95:
            failures.append(level+': >=50 reviewed cases and >=95% baseline score required')
    for key,limit in [('peak_p95_model_ttft_seconds',3),('max_background_seconds',600),('restore_rto_seconds',14400),('restore_rpo_seconds',3600)]:
        v=data.get(key)
        if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or v<0 or v>limit:
            failures.append(key+': missing/invalid/out of target')
    for key in ['cross_tenant_leaks','unapproved_external_writes','sandbox_egress_successes']:
        if type(data.get(key)) is not int or data[key]!=0:failures.append(key+': must be tested with zero successful violations')
    for key in ['dataset_reviewed','peak_load_from_vietnam','acl_revocation_tested','quota_race_tested','sandbox_cleanup_tested','evidence_links_reviewed']:
        if data.get(key) is not True:failures.append(key+': evidence required')
    return {'pass':not failures,'failures':failures,'note':'Gate checks reported measurements; inspect source evidence before releasing.'}

if __name__=='__main__':
    with open(sys.argv[1],encoding='utf-8') as f:result=evaluate(json.load(f))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result['pass'] else 1)
