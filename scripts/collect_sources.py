import json, urllib.parse, urllib.request, datetime, time

QUERIES = [
  "artificial intelligence agents scientific literature",
  "systems engineering standards public report",
  "energy storage grid technology report",
  "space propulsion research preprint",
  "materials science advanced manufacturing review",
  "robotics autonomous systems research",
  "cybersecurity resilience standards",
  "climate infrastructure public data",
  "economics productivity technology report",
  "patent prior art artificial intelligence systems"
]

UA = {"User-Agent":"CEREBRON-Research-Web/1.0"}

def get_json(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=25) as r:
        return json.loads(r.read().decode("utf-8","replace"))

def crossref(q, rows=5):
    url="https://api.crossref.org/works?rows=%d&query=%s"%(rows,urllib.parse.quote(q))
    data=get_json(url)
    out=[]
    for x in data.get("message",{}).get("items",[]):
        title=(x.get("title") or [""])[0]
        doi=x.get("DOI")
        out.append({
          "provider":"Crossref","query":q,"title":title,"doi":doi,
          "url":x.get("URL"),"published":x.get("published-print") or x.get("published-online") or x.get("issued"),
          "type":x.get("type"),"publisher":x.get("publisher")
        })
    return out

def openalex(q, rows=5):
    url="https://api.openalex.org/works?per-page=%d&search=%s"%(rows,urllib.parse.quote(q))
    data=get_json(url)
    out=[]
    for x in data.get("results",[]):
        out.append({
          "provider":"OpenAlex","query":q,"title":x.get("title"),"doi":x.get("doi"),
          "url":x.get("id"),"published":x.get("publication_date"),"type":x.get("type"),
          "cited_by_count":x.get("cited_by_count"),"open_access":x.get("open_access")
        })
    return out

items=[]; errors=[]
for q in QUERIES:
    for fn in (crossref, openalex):
        try:
            items.extend(fn(q))
        except Exception as e:
            errors.append({"query":q,"provider":fn.__name__,"error":repr(e)})
        time.sleep(0.2)

# deterministic de-dup on DOI else normalized title
seen=set(); dedup=[]
for x in items:
    key=(x.get("doi") or (x.get("title") or "").strip().lower())
    if key and key not in seen:
        seen.add(key); dedup.append(x)

packet={
  "generated_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "queries":QUERIES,"raw_count":len(items),"dedup_count":len(dedup),
  "sources":dedup,"errors":errors
}
open("source_packet.json","w",encoding="utf-8").write(json.dumps(packet,ensure_ascii=False,indent=2))
print(json.dumps({"raw_count":len(items),"dedup_count":len(dedup),"errors":len(errors)}))
