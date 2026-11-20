"use client";
import { useCallback, useEffect, useState } from "react";
import Shell, { Level, Msg } from "../../components/Shell";
import { api, CATEGORY } from "../../lib/api";

export default function Employer() {
  const [profs, setProfs] = useState([]);
  const [skills, setSkills] = useState([]);
  const [pid, setPid] = useState("");
  const [cands, setCands] = useState(null);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");
  const [np, setNp] = useState({ title: "", description: "", reqs: [{ skill_id: "", required_level: 3, weight: 2 }] });

  const loadProfs = useCallback(async () => {
    try { const [p, s] = await Promise.all([api("/professions"), api("/skills")]); setProfs(p); setSkills(s); } catch (x) { setErr(x.message); }
  }, []);
  useEffect(() => { loadProfs(); }, [loadProfs]);

  async function pick(id) {
    setPid(id); setCands(null); setErr("");
    if (!id) return;
    try { setCands(await api(`/employer/candidates?profession_id=${id}`)); } catch (x) { setErr(x.message); }
  }
  const setReq = (i, k, v) => setNp({ ...np, reqs: np.reqs.map((r, j) => (j === i ? { ...r, [k]: v } : r)) });

  async function create(e) {
    e.preventDefault(); setErr(""); setOk("");
    try {
      const requirements = np.reqs.map((r) => ({ skill_id: Number(r.skill_id), required_level: Number(r.required_level), weight: Number(r.weight) }));
      const p = await api("/professions", { method: "POST", body: { title: np.title, description: np.description, requirements } });
      setOk(`“${p.title}” talablari saqlandi.`);
      setNp({ title: "", description: "", reqs: [{ skill_id: "", required_level: 3, weight: 2 }] });
      await loadProfs(); pick(String(p.id));
    } catch (x) { setErr(x.message); }
  }

  return (
    <Shell role="employer">
      <h1>Ish beruvchi paneli</h1>
      <Msg error={err} ok={ok} />
      <section className="card">
        <h2>Nomzodlar</h2>
        <label>Kasb / lavozim
          <select value={pid} onChange={(e) => pick(e.target.value)}>
            <option value="">— tanlang —</option>{profs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
        </label>
        <p className="muted small">Faqat rozilik bergan talabalar va faqat ekspert tasdiqlagan ko‘nikmalar ko‘rinadi.</p>
        {cands && (cands.candidates.length === 0 ? <p className="muted">Mos nomzod topilmadi.</p> : cands.candidates.map((c) => (
          <div className="ev" key={c.id}>
            <div className="ev-head"><b>{c.name}</b> <span className="muted">{c.faculty}</span> <span className="tag verified">Moslik: {c.match}%</span></div>
            <div className="chips">{c.skills.map((s) => <span key={s.name} className="chip">{s.name} <Level value={s.verified} /> / {s.required}</span>)}</div>
          </div>
        )))}
      </section>

      <section className="card">
        <h2>Yangi kasb talabi kiritish</h2>
        <form onSubmit={create}>
          <div className="grid2">
            <label>Kasb nomi<input required minLength={2} value={np.title} onChange={(e) => setNp({ ...np, title: e.target.value })} /></label>
            <label>Tavsif<input value={np.description} onChange={(e) => setNp({ ...np, description: e.target.value })} /></label>
          </div>
          {np.reqs.map((r, i) => (
            <div className="row" key={i}>
              <select required className="grow" value={r.skill_id} onChange={(e) => setReq(i, "skill_id", e.target.value)}>
                <option value="">Kompetensiya…</option>{skills.map((s) => <option key={s.id} value={s.id}>{s.name} ({CATEGORY[s.category]})</option>)}
              </select>
              <label className="inline">Daraja<select value={r.required_level} onChange={(e) => setReq(i, "required_level", e.target.value)}>{[1, 2, 3, 4, 5].map((n) => <option key={n}>{n}</option>)}</select></label>
              <label className="inline">Muhimlik<select value={r.weight} onChange={(e) => setReq(i, "weight", e.target.value)}>{[1, 2, 3].map((n) => <option key={n}>{n}</option>)}</select></label>
              {np.reqs.length > 1 && <button type="button" className="ghost danger" onClick={() => setNp({ ...np, reqs: np.reqs.filter((_, j) => j !== i) })}>×</button>}
            </div>
          ))}
          <div className="row">
            <button type="button" className="ghost" onClick={() => setNp({ ...np, reqs: [...np.reqs, { skill_id: "", required_level: 3, weight: 2 }] })}>+ Kompetensiya</button>
            <button className="btn">Saqlash</button>
          </div>
        </form>
      </section>
    </Shell>
  );
}
