#!/usr/bin/env python3
"""
Call-Intel Report Generator
• Reads a net2phone Call-History CSV
• Creates Markdown + JSON reports (charts included)
• Optional six-bullet GPT-4o-mini executive summary
"""

import argparse, os, json, warnings, datetime as dt, re, textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytz
import phonenumbers
from phonenumbers import geocoder

try:
    from openai import OpenAI          # SDK ≥1.0
except ModuleNotFoundError:
    OpenAI = None

warnings.filterwarnings("ignore", message="Could not infer format")

# ───── constants
TZ_IL = pytz.timezone("Asia/Jerusalem")
TODAY  = dt.date.today()

HEADERS = {                        # normalise messy CSV column names
    "direction":"Direction","call result":"Call Result",
    "from name":"From Name","from number":"From Number",
    "via":"Via","to name":"To Name","to number":"To Number",
    "duration":"Duration","time":"Time",
}

CITY_ST_RE = re.compile(r"(.+?)[,\s]+([A-Z]{2})$")   # “City, ST” or “City ST”

# ───── loaders & parsers
def load_csv(path:str)->pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={c:HEADERS.get(c.split("(")[0].strip().lower(), c)
                            for c in df.columns})
    return df

def parse_time(df:pd.DataFrame)->pd.DataFrame:
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce", utc=True)
    df = df.dropna(subset=["Time"])
    df["Time"] = df["Time"].dt.tz_convert(TZ_IL)
    df["Date"], df["Hour"] = df["Time"].dt.date, df["Time"].dt.hour
    return df

def to_td(txt:str)->pd.Timedelta:
    try: h,m,s = map(int, str(txt).split(":")); return pd.Timedelta(hours=h,minutes=m,seconds=s)
    except: return pd.Timedelta(0)

# ───── location helpers
def loc_from_name(name:str)->str:
    m=CITY_ST_RE.search(name)
    return f"{m.group(1).strip()}, {m.group(2)}" if m else ""

def loc_from_number(num:str)->str:
    digits="".join(filter(str.isdigit, num))
    if not digits: return ""
    if not digits.startswith("+"):
        digits="+1"+digits if len(digits)==10 else "+"+digits
    try:
        pn=phonenumbers.parse(digits, None)
        return geocoder.description_for_number(pn, "en")  # may fall back to State
    except phonenumbers.NumberParseException:
        return ""

def row_location(row)->str:
    by_name = loc_from_name(str(row.get("From Name","")))
    return by_name if by_name else loc_from_number(str(row.get("From Number","")))

# ───── metrics
pct = lambda a,b: round(100*a/b,1) if b else 0.0

def aggregate(df)->dict:
    total=len(df)
    inbound_mask = df["Direction"].str.lower().str.startswith("in") if "Direction" in df else pd.Series(False,index=df.index)
    inbound, outbound = inbound_mask.sum(), total - inbound_mask.sum()
    res = df["Call Result"].str.lower() if "Call Result" in df else pd.Series([],dtype=str)
    count = lambda k:(res==k).sum()
    longest = df.loc[df["DurTD"].idxmax()] if total else None
    return dict(
        total=total, inbound=inbound, outbound=outbound,
        answered_pct=pct(count("answered"),total),
        missed_pct=pct(count("not answered"),total),
        vm_pct=pct(count("voicemail"),total),
        blocked_pct=pct(count("blocked"),total),
        avg_dur=str(df["DurTD"].mean()),
        median_dur=str(df["DurTD"].median()),
        talk_time=str(df["DurTD"].sum()),
        longest=dict(duration=str(longest["DurTD"]),
                     from_name=longest["From Name"],
                     to_name=longest["To Name"],
                     time=str(longest["Time"])) if longest is not None else None
    )

def peak_hour(df): return df.groupby("Hour").size().idxmax()

def top_talk(df,n=5):
    owner_col="Via" if "Via" in df else "To Name"
    g=(df.groupby(df[owner_col].fillna("Unassigned"))["DurTD"]
       .sum().sort_values(ascending=False).head(n).reset_index())
    g.columns=["owner","talk_time"]
    g["talk_time"]=g["talk_time"].astype(str)
    return g

def top_numbers(df,inbound_mask,n=5):
    sub=df[inbound_mask] if inbound_mask.any() else df
    g=sub.groupby("From Number").size().sort_values(ascending=False).head(n).reset_index(name="calls")
    return g

def top_locations(df,inbound_mask,n=10):
    sub=df[inbound_mask] if inbound_mask.any() else df
    sub=sub.assign(location=sub.apply(row_location,axis=1))
    sub=sub[sub["location"]!=""]
    g=sub.groupby("location").size().sort_values(ascending=False).head(n).reset_index(name="calls")
    return g

def missed_by_owner(df,th=20):
    owner_col="Via" if "Via" in df else "To Name"
    if "Call Result" not in df: return pd.DataFrame()
    tmp=df.assign(owner=df[owner_col].fillna("Unassigned"),
                  missed=df["Call Result"].str.lower()=="not answered")
    g=tmp.groupby("owner").agg(total=("missed","size"), missed=("missed","sum"))
    g["missed_pct"]=round(100*g["missed"]/g["total"],1)
    return g[g["missed_pct"]>th].reset_index()

def missed_days(df,th=30):
    if "Call Result" not in df: return pd.DataFrame()
    tmp=df.assign(missed=df["Call Result"].str.lower()=="not answered")
    g=tmp.groupby("Date").agg(total=("missed","size"), missed=("missed","sum"))
    g["missed_pct"]=round(100*g["missed"]/g["total"],1)
    return g[g["missed_pct"]>th].reset_index()

# ───── charts
def chart_call(df,path):
    if "Call Result" not in df:return
    ax=df["Call Result"].value_counts().plot(kind="bar")
    ax.set_ylabel("Count");ax.set_xlabel("Call Result");ax.set_title("Call-Result Distribution")
    plt.tight_layout(); plt.savefig(path,dpi=160); plt.close()

def chart_daily(df,path):
    rng=pd.date_range(TODAY-dt.timedelta(days=29),TODAY)
    series=df.groupby("Date").size().reindex(rng,fill_value=0)
    ax=series.plot(); ax.set_ylabel("Calls"); ax.set_xlabel("Date"); ax.set_title("Daily Call Volume – last 30 days")
    plt.tight_layout(); plt.savefig(path,dpi=160); plt.close()

# ───── GPT summary
def gpt_summary(kpi_md,key):
    if not key or OpenAI is None: return "⚠️ OpenAI key missing – summary not generated.\n"
    client=OpenAI(api_key=key)
    chat=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":(
            "You are Call-Intel, a data analyst for UCaaS admins.\n"
            "Write a six-bullet executive summary with actionable points.\n\n"
            f"Metrics:\n{kpi_md}")}],
        temperature=0.3,
    )
    return chat.choices[0].message.content.strip()

# ───── markdown helpers
def md(df,index=False):
    return "\n"+(df.to_markdown(index=index,tablefmt="github") if not df.empty else "_— no data —_")+"\n"

def kpi_table(st,peak):
    long_str = ("N/A" if st["longest"] is None else
                f"{st['longest']['duration']} ({st['longest']['from_name']} → {st['longest']['to_name']} on {st['longest']['time']})")
    tbl=pd.DataFrame({
        "Metric":["Total Calls","Inbound Calls","Outbound Calls","Answered %","Missed %",
                  "Voicemail %","Blocked %","Avg Duration","Median Duration",
                  "Total Talk Time","Longest Call","Peak Hour"],
        "Value":[st['total'],f"{st['inbound']} ({pct(st['inbound'],st['total'])} %)",
                 f"{st['outbound']} ({pct(st['outbound'],st['total'])} %)",
                 f"{st['answered_pct']} %",f"{st['missed_pct']} %",f"{st['vm_pct']} %",
                 f"{st['blocked_pct']} %",st['avg_dur'],st['median_dur'],st['talk_time'],
                 long_str,f"{peak:02d}:00"]})
    return md(tbl)

def section(title,body): return f"## {title}\n{body}"

def build_markdown(summary,kpi,bar,line,talk,nums,locs,miss_own,miss_day):
    return "\n\n".join([
        section("Executive Summary",summary),
        section("Key Metrics",kpi),
        section("Call-Result Distribution",f"\n![]({bar})\n"),
        section("Daily Call Volume",f"\n![]({line})\n"),
        section("Top Talk-Time Owners",md(talk)),
        section("Top External Inbound Numbers",md(nums)),
        section("Top Inbound Locations",md(locs)),
        section("High-Miss Owners (> 20 % missed)",md(miss_own)),
        section("Days Over 30 % Missed",md(miss_day,index=True)),
    ])+"\n"

# ───── main
def main():
    p=argparse.ArgumentParser(description="Generate Markdown + JSON call report")
    p.add_argument("--input",required=True); p.add_argument("--output",default="report.md")
    p.add_argument("--openai-key"); args=p.parse_args()
    key=args.openai_key or os.getenv("OPENAI_API_KEY")

    df=load_csv(args.input)
    df=parse_time(df)
    df["DurTD"]=df.get("Duration","").astype(str).apply(to_td)

    inbound_mask=df["Direction"].str.lower().str.startswith("in") if "Direction" in df else pd.Series(False,index=df.index)

    # charts
    bar_png,line_png = Path("call_result.png"),Path("daily_volume.png")
    chart_call(df,bar_png); chart_daily(df,line_png)

    # metrics/tables
    stats = aggregate(df); peak=peak_hour(df)
    talk = top_talk(df)
    nums = top_numbers(df,inbound_mask)
    locs = top_locations(df,inbound_mask)
    miss_o= missed_by_owner(df)
    miss_d= missed_days(df)

    kpi_md = kpi_table(stats,peak)
    summary = gpt_summary(kpi_md,key)

    # write Markdown
    md_path = Path(args.output)
    md_path.write_text(build_markdown(summary,kpi_md,bar_png,line_png,
                                      talk,nums,locs,miss_o,miss_d),encoding="utf-8")
    print(f"✅  Markdown saved → {md_path}")

    # write JSON
    data={
        "kpi":stats,
        "top_talk":talk.to_dict(orient="records"),
        "top_numbers":nums.to_dict(orient="records"),
        "top_locations":locs.to_dict(orient="records"),
        "miss_by_owner":miss_o.to_dict(orient="records"),
        "miss_days":miss_d.to_dict(orient="records"),
        "charts":{"call_result":str(bar_png),"daily_volume":str(line_png)},
        "summary":summary.strip()
    }
    json_path = md_path.with_suffix(".json")
    json_path.write_text(json.dumps(data,default=str,indent=2),encoding="utf-8")
    print(f"✅  JSON saved → {json_path}")

if __name__=="__main__":
    main()