import os, json, pathlib
from hf_gradio import GradioClient

role=os.environ["ROLE"]
model=os.environ["MODEL"]
focus=os.environ.get("FOCUS","")
packet=json.load(open("source_packet.json",encoding="utf-8"))
# keep prompt bounded but provenance-rich
sources=packet.get("sources",[])[:80]
context=json.dumps({"generated_at_utc":packet.get("generated_at_utc"),"sources":sources},ensure_ascii=False)
prompt=f'''You are role {role} in CEREBRON Farm 08 Research Web.
FOCUS: {focus}
Rules: CLAIM<=EVIDENCE. Analyze ONLY the supplied collected source packet. Do not claim live web access. For every external factual claim, identify source title/provider/url or DOI from the packet. Distinguish ESTABLISHED / PREPRINT-OR-UNVERIFIED / INFERENCE / UNKNOWN. Detect weak or irrelevant sources. Return concise JSON-like text with: findings, source_links, caveats, routing_targets, unknowns.
SOURCE_PACKET:
{context}'''

try:
    client=GradioClient(model)
    result=client.predict(prompt, api_name="/chat")
    ok=True; err=None
except Exception as e:
    result=""; ok=False; err=repr(e)

out={"role":role,"model":model,"focus":focus,"inference_success":ok,"error":err,"result":result}
pathlib.Path("out").mkdir(exist_ok=True)
open(f"out/{role}.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({"role":role,"inference_success":ok}))
