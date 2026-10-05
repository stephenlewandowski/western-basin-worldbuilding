"""Small Lucas County LOCA2 extraction from NOAA/Esri CRIS annual model tables.

Default: rebuild offline from retained responses. --fetch: deliberately refresh
the five public query/metadata snapshots, then rebuild. No Model Lab calculation.
"""
from pathlib import Path
from datetime import datetime, timezone
from statistics import mean
import argparse, hashlib, json, math, urllib.parse, urllib.request

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/'data/climate'
BASE='https://services3.arcgis.com/0Fs3HcaFfvzXvm7w/arcgis/rest/services/CRIS_County_D/FeatureServer'
MODELS=['IPSL-CM6A-LR','MPI-ESM1-2-HR','MRI-ESM2-0']
PATHS=['SSP245','SSP370','SSP585']
FIELDS={'TAVG': ('annual_temperature','degF'), 'TMEANJJA': ('summer_temperature','degF'),
        'TMAXDAYSGE90F': ('hot_days','days/year'), 'TMINDAYSGE70F': ('warm_nights','days/year'),
        'CDD': ('cooling_degree_days','degF-days; base 65 degF')}


def query_url(layer, window):
    where="GEOID='39095' AND MODEL_SET='LOCA2' AND MODEL IN ("+','.join(f"'{m}'" for m in MODELS)+') AND '+window
    fields=list(FIELDS) if layer==5 else [f'{field}_{path}' for field in FIELDS for path in PATHS]
    return BASE+f'/{layer}/query?'+urllib.parse.urlencode({'where':where,'outFields':','.join(['GEOID','MODEL_SET','MODEL','YEAR',*fields]),
                'orderByFields':'MODEL,YEAR','returnGeometry':'false','resultRecordCount':500,'f':'json'})


def fetch():
    sources={
        'cris_lucas_historical.json': query_url(5,'YEAR >= 1991 AND YEAR <= 2014'),
        'cris_lucas_future.json': query_url(6,'((YEAR >= 2015 AND YEAR <= 2020) OR (YEAR >= 2061 AND YEAR <= 2090))'),
        'cris_county_item.json': 'https://www.arcgis.com/sharing/rest/content/items/f5134f46a5a3491f8259145271644eed?f=pjson',
        'cris_historical_schema.json': BASE+'/5?f=pjson',
        'cris_future_schema.json': BASE+'/6?f=pjson',
    }
    records=[]
    for name,url in sources.items():
        raw=urllib.request.urlopen(url,timeout=60).read()
        data=json.loads(raw)
        if 'error' in data: raise ValueError(data['error'])
        file=DATA/'sources'/name
        file.write_bytes(raw)
        records.append({'file':file.relative_to(ROOT).as_posix(),'url':url,
                        'retrieved_utc':datetime.now(timezone.utc).isoformat(),
                        'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        print(name,len(raw))
    manifest={'edition':'2026-10-05','provider':'NOAA Climate Resilience Information System / Esri hosted CRIS county data',
              'license':'CC BY 4.0; retain NOAA/Esri CRIS attribution and source links',
              'source_documentation':'https://cris.climate.gov/pages/about-the-data','sources':records}
    (DATA/'projection_source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')


def verified_rows(name):
    data=json.loads((DATA/'sources'/name).read_bytes())
    assert not data.get('exceededTransferLimit'), 'Truncated response'
    assert 'error' not in data
    rows=[feature['attributes'] for feature in data['features']]
    for r in rows:
        assert r['GEOID']=='39095' and r['MODEL_SET']=='LOCA2' and r['MODEL'] in MODELS
    assert len({(r['MODEL'],r['YEAR']) for r in rows})==len(rows), 'Duplicate model/year'
    return rows


def summarize(historical, future):
    assert len(historical)==72 and len(future)==108
    samples=[]
    for path in PATHS:
        by_model=[]
        for model in MODELS:
            hist=[r for r in historical if r['MODEL']==model]
            recent=[r for r in future if r['MODEL']==model and 2015<=r['YEAR']<=2020]
            later=[r for r in future if r['MODEL']==model and 2061<=r['YEAR']<=2090]
            assert {r['YEAR'] for r in hist}==set(range(1991,2015))
            assert {r['YEAR'] for r in recent}==set(range(2015,2021))
            assert {r['YEAR'] for r in later}==set(range(2061,2091))
            metrics={}
            for field,(key,unit) in FIELDS.items():
                before=[r[field] for r in hist]+[r[f'{field}_{path}'] for r in recent]
                after=[r[f'{field}_{path}'] for r in later]
                assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in before+after), (model,path,key)
                if unit=='days/year': assert all(0<=v<=366 for v in before+after)
                b,a=mean(before),mean(after)
                metrics[key]={'unit':unit,'baseline':round(b,4),'future':round(a,4),'change':round(a-b,4)}
                if unit=='degF':
                    metrics[key].update({'baseline_c':round((b-32)*5/9,4),'future_c':round((a-32)*5/9,4),
                                        'change_c':round((a-b)*5/9,4)})
            by_model.append({'model':model,'baseline_years':30,'future_years':30,'metrics':metrics})
        summary={}
        for key in [v[0] for v in FIELDS.values()]:
            metrics=[r['metrics'][key] for r in by_model]
            summary[key]={'unit':metrics[0]['unit']}
            for statistic in ['baseline','future','change']+(['baseline_c','future_c','change_c'] if metrics[0]['unit']=='degF' else []):
                vals=[r[statistic] for r in metrics]
                summary[key][statistic]={'mean':round(mean(vals),4),'sample_min':min(vals),'sample_max':max(vals)}
        samples.append({'path':path,'series':by_model,'summary':summary})
    return samples


def build():
    manifest=json.loads((DATA/'projection_source_manifest.json').read_text(encoding='utf-8'))
    for source in manifest['sources']:
        assert hashlib.sha256((ROOT/source['file']).read_bytes()).hexdigest()==source['sha256'],source['file']
    historical=verified_rows('cris_lucas_historical.json')
    future=verified_rows('cris_lucas_future.json')
    result={'schema_version':'1.0','edition':'2026-10-05','status':'Small published-model-series projection sample; not a full ensemble uncertainty envelope',
            'geography':{'name':'Lucas County, Ohio','geoid':'39095','boundary_product':'US Census TIGER 2023',
                         'scope':'County spatial summary of LOCA2 grids; not an airport, street or entire watershed'},
            'provenance':{'product':'CRIS annual county summaries; MODEL_SET=LOCA2 only','downscaling':'CMIP6 LOCA2-derived annual metrics; parent product approximately 6 km, service resampling not asserted',
                          'provider':'NOAA / Esri Climate Resilience Information System','source_manifest':'data/climate/projection_source_manifest.json',
                          'documentation':'https://cris.climate.gov/pages/about-the-data','service':BASE,
                          'model_member_identity':'Variant IDs/within-model aggregation not exposed by this county service; not claimed as individual CMIP6 members',
                          'upstream_release':'Exact upstream release not exposed by county service; retained query/schema/item snapshots are identified by retrieval time and SHA256',
                          'spatial_method':'County zonal mean, TIGER2023 boundaries. Documentation/example code disagree about resampling direction; unchanged native grid not claimed.',
                          'source_calendar':'Annual statistics supplied by provider; source daily calendar handling not reconstructed here'},
            'windows':{'baseline':[1991,2020],'future':[2061,2090],
                       'baseline_join':'1991–2014 historical plus 2015–2020 from the same SSP as the future; modeled baseline, not observed normals'},
            'selection':{'models':MODELS,'paths':PATHS,'weight_per_model':1/3,
                         'reason':'Three distinct GCM families available for all selected metrics and pathways; small availability-based sample',
                         'limits':'Equal weight across these three published model series only. Not member-balanced, representative of all 27 LOCA2 models, probabilistic or an upper/lower bound.'},
            'definitions':{'temperature':'Provider annual/summer mean daily midpoint in Fahrenheit; temperature changes also converted to Celsius',
                           'hot_days':'County-average annual count of daily maxima >=90 F; fractional days arise from spatial averaging',
                           'warm_nights':'County-average annual count of daily minima >=70 F; daily minimum proxy, not hourly night exposure',
                           'cooling_degree_days':'Annual cooling degree-days in Fahrenheit-degree-days, base65 F; not electrical load',
                           'aggregation':'Arithmetic mean of each annual metric over 30 years; changes within the same model/product/path; then equal-weight mean and min/max of three model-series climatologies',
                           'spread':'Three-series min/max, not annual variability, percentile, confidence interval, full-model range or 2075 weather'},
            'scenarios':summarize(historical,future)}
    (DATA/'local_projections.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    for scenario in result['scenarios']:
        t=scenario['summary']['annual_temperature']['change_c']; h=scenario['summary']['hot_days']['future']
        print(scenario['path'],'warming C',t,'hot days/year',h)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--fetch',action='store_true',help='Deliberately download/replace the retained CRIS subset and metadata')
    args=parser.parse_args()
    if args.fetch: fetch()
    build()
