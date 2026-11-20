"use client";
import { useCallback, useEffect, useState } from "react";
import Shell, { Msg } from "../../../components/Shell";
import { api, KIND } from "../../../lib/api";

export default function Roadmap() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => { try { setItems(await api("/roadmap")); } catch (x) { setErr(x.message); } }, []);
  useEffect(() => { load(); }, [load]);

  async function generate() {
    setErr(""); setBusy(true);
    try { setItems(await api("/roadmap/generate", { method: "POST" })); } catch (x) { setErr(x.message); } finally { setBusy(false); }
  }
  async function toggle(it) {
    try { const r = await api(`/roadmap/${it.id}`, { method: "PATCH", body: { done: !it.done } }); setItems(items.map((x) => (x.id === it.id ? r : x))); } catch (x) { setErr(x.message); }
  }
  const done = items.filter((i) => i.done).length;

  return (
    <Shell role="student">
      <h1>Individual rivojlanish xaritasi</h1>
      <Msg error={err} />
      <div className="row"><button className="btn" onClick={generate} disabled={busy}>{busy ? "Tuzilmoqda…" : items.length ? "Rejani yangilash" : "Reja tuzish"}</button>
        {items.length > 0 && <span className="muted">{done} / {items.length} bajarildi</span>}</div>
      <p className="muted small">Reja Skill Gap natijasiga ko‘ra tuziladi. Yangilanganda bajarilgan bandlar saqlanadi.</p>
      {items.length === 0 && <section className="card muted">Hozircha reja yo‘q. Avval bosh sahifada kasbiy maqsadni tanlang, so‘ng “Reja tuzish”ni bosing.</section>}
      {items.map((it) => (
        <label key={it.id} className={`card step ${it.done ? "done" : ""}`}>
          <input type="checkbox" checked={it.done} onChange={() => toggle(it)} />
          <div><b>{it.title}</b> <span className="tag">{KIND[it.kind]}</span><div className="muted small">{it.detail}</div></div>
        </label>
      ))}
    </Shell>
  );
}
