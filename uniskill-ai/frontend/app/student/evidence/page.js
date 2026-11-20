"use client";
import { useCallback, useEffect, useState } from "react";
import Shell, { Level, Msg } from "../../../components/Shell";
import { api, CATEGORY, STATUS } from "../../../lib/api";

const TYPES = { project: "Loyiha", assignment: "Amaliy topshiriq", certificate: "Sertifikat", grade: "Fan bahosi", self: "O‘zini baholash" };
const empty = { skill_id: "", type: "project", title: "", description: "", url: "", claimed_level: 3 };

export default function Evidence() {
  const [skills, setSkills] = useState([]);
  const [list, setList] = useState([]);
  const [f, setF] = useState(empty);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    try { const [s, e] = await Promise.all([api("/skills"), api("/evidence")]); setSkills(s); setList(e); } catch (x) { setErr(x.message); }
  }, []);
  useEffect(() => { load(); }, [load]);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault(); setErr(""); setOk("");
    try {
      await api("/evidence", { method: "POST", body: { ...f, skill_id: Number(f.skill_id), claimed_level: Number(f.claimed_level), url: f.url || null } });
      setF(empty);
      setOk(f.type === "self" ? "Saqlandi. O‘zini baholash tasdiq hisoblanmaydi." : "Dalil ekspert tekshiruviga yuborildi.");
      load();
    } catch (x) { setErr(x.message); }
  }
  async function analyze(id) {
    setBusyId(id); setErr("");
    try { await api(`/evidence/${id}/analyze`, { method: "POST" }); await load(); } catch (x) { setErr(x.message); } finally { setBusyId(null); }
  }
  async function remove(id) {
    if (!confirm("Dalil o‘chirilsinmi?")) return;
    try { await api(`/evidence/${id}`, { method: "DELETE" }); load(); } catch (x) { setErr(x.message); }
  }

  return (
    <Shell role="student">
      <h1>Dalillar</h1>
      <Msg error={err} ok={ok} />
      <section className="card">
        <h2>Yangi dalil qo‘shish</h2>
        <form onSubmit={submit} className="grid2">
          <label>Kompetensiya
            <select required value={f.skill_id} onChange={set("skill_id")}>
              <option value="">— tanlang —</option>
              {skills.map((s) => <option key={s.id} value={s.id}>{s.name} ({CATEGORY[s.category]})</option>)}
            </select>
          </label>
          <label>Dalil turi
            <select value={f.type} onChange={set("type")}>{Object.entries(TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
          </label>
          <label>Sarlavha<input required minLength={2} value={f.title} onChange={set("title")} /></label>
          <label>Havola (GitHub, sertifikat…)<input type="url" value={f.url} onChange={set("url")} placeholder="https://" /></label>
          <label className="full">Tavsif — nima qildingiz, natija nima?<textarea rows={3} maxLength={4000} value={f.description} onChange={set("description")} /></label>
          <label>O‘z darajangiz (1–5): {f.claimed_level}<input type="range" min="1" max="5" value={f.claimed_level} onChange={set("claimed_level")} /></label>
          <div className="full"><button className="btn">Qo‘shish</button> <span className="muted small">Hujjat yuklashning o‘zi tasdiq emas: ekspert tekshiradi.</span></div>
        </form>
      </section>

      <section className="card">
        <h2>Mening dalillarim</h2>
        {list.length === 0 && <p className="muted">Hali dalil yo‘q.</p>}
        {list.map((e) => (
          <div className="ev" key={e.id}>
            <div className="ev-head">
              <b>{e.title}</b> <span className="muted">· {e.skill.name} · {TYPES[e.type]}</span>
              <span className={`tag ${e.status}`}>{STATUS[e.status]}</span>
            </div>
            <div className="small">Da’vo: <Level value={e.claimed_level} />{e.verified_level ? <> &nbsp; Tasdiqlangan: <Level value={e.verified_level} /></> : null}</div>
            {e.description && <p className="small">{e.description}</p>}
            {e.url && <a className="small" href={e.url} target="_blank" rel="noopener noreferrer">{e.url}</a>}
            {e.ai_feedback && <div className="ai"><b>AI dastlabki bahosi: {e.ai_level}/5.</b> {e.ai_feedback}<div className="muted small">AI yakuniy hukm chiqarmaydi.</div></div>}
            {e.reviewer_note && <div className="small"><b>Ekspert izohi:</b> {e.reviewer_note}</div>}
            <div className="row">
              <button className="ghost" disabled={busyId === e.id} onClick={() => analyze(e.id)}>{busyId === e.id ? "Tahlil qilinmoqda…" : "AI tahlil"}</button>
              {e.status !== "verified" && <button className="ghost danger" onClick={() => remove(e.id)}>O‘chirish</button>}
            </div>
          </div>
        ))}
      </section>
    </Shell>
  );
}
