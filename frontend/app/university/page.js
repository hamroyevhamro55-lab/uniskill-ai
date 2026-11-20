"use client";
import { useCallback, useEffect, useState } from "react";
import Shell, { Level, Msg } from "../../components/Shell";
import { api } from "../../lib/api";

export default function University() {
  const [an, setAn] = useState(null);
  const [queue, setQueue] = useState([]);
  const [notes, setNotes] = useState({});
  const [levels, setLevels] = useState({});
  const [err, setErr] = useState("");

  const load = useCallback(async () => {
    try { const [a, q] = await Promise.all([api("/university/analytics"), api("/review/queue")]); setAn(a); setQueue(q); } catch (x) { setErr(x.message); }
  }, []);
  useEffect(() => { load(); }, [load]);

  async function decide(e, approve) {
    setErr("");
    try {
      await api(`/review/${e.id}`, { method: "POST", body: { approve, verified_level: approve ? Number(levels[e.id] ?? e.claimed_level) : null, note: notes[e.id] || "" } });
      load();
    } catch (x) { setErr(x.message); }
  }

  return (
    <Shell role="university">
      <h1>Universitet paneli</h1>
      <Msg error={err} />
      {an && (
        <>
          <div className="stats">
            <div className="card stat"><div className="big-num">{an.students_total}</div>talaba</div>
            <div className="card stat"><div className="big-num">{an.avg_readiness}%</div>o‘rtacha tayyorlik</div>
            <div className="card stat"><div className="big-num">{an.evidence.pending}</div>tekshiruvda</div>
            <div className="card stat"><div className="big-num">{an.evidence.verified}</div>tasdiqlangan</div>
          </div>
          <section className="card">
            <h2>Eng katta kompetensiya tafovutlari</h2>
            <p className="muted small">Umumlashtirilgan va anonim natijalar.</p>
            {an.top_gaps.length === 0 ? <p className="muted">Ma’lumot yo‘q.</p> : (
              <table><thead><tr><th>Kompetensiya</th><th>Talabalar</th><th>Tafovut bor</th><th>O‘rtacha tafovut</th></tr></thead>
                <tbody>{an.top_gaps.map((g) => <tr key={g.skill}><td>{g.skill}</td><td>{g.students}</td><td>{g.with_gap}</td><td>{g.avg_gap}</td></tr>)}</tbody></table>
            )}
          </section>
          <section className="card">
            <h2>Yo‘nalishlar kesimida</h2>
            {an.by_faculty.length === 0 ? <p className="muted">Ma’lumot yo‘q.</p> : (
              <table><thead><tr><th>Fakultet / yo‘nalish</th><th>Talabalar</th><th>O‘rtacha tayyorlik</th></tr></thead>
                <tbody>{an.by_faculty.map((f) => <tr key={f.faculty}><td>{f.faculty}</td><td>{f.students}</td><td>{f.avg_readiness}%</td></tr>)}</tbody></table>
            )}
          </section>
        </>
      )}
      <section className="card">
        <h2>Ekspert tekshiruvi ({queue.length})</h2>
        {queue.length === 0 && <p className="muted">Tekshiruvga kutayotgan dalil yo‘q.</p>}
        {queue.map((e) => (
          <div className="ev" key={e.id}>
            <div className="ev-head"><b>{e.title}</b> <span className="muted">· {e.skill.name} · {e.student_name}{e.student_faculty ? ` (${e.student_faculty})` : ""}</span></div>
            <div className="small">Talaba da’vosi: <Level value={e.claimed_level} />{e.ai_level ? <> &nbsp; AI dastlabki: {e.ai_level}/5</> : null}</div>
            {e.description && <p className="small">{e.description}</p>}
            {e.url && <a className="small" href={e.url} target="_blank" rel="noopener noreferrer">{e.url}</a>}
            {e.ai_feedback && <div className="ai small">{e.ai_feedback}</div>}
            <div className="row">
              <label className="inline">Daraja
                <select value={levels[e.id] ?? e.claimed_level} onChange={(ev) => setLevels({ ...levels, [e.id]: ev.target.value })}>{[1, 2, 3, 4, 5].map((n) => <option key={n}>{n}</option>)}</select>
              </label>
              <input className="grow" placeholder="Izoh (ixtiyoriy)" value={notes[e.id] || ""} onChange={(ev) => setNotes({ ...notes, [e.id]: ev.target.value })} />
              <button className="btn" onClick={() => decide(e, true)}>Tasdiqlash</button>
              <button className="ghost danger" onClick={() => decide(e, false)}>Rad etish</button>
            </div>
          </div>
        ))}
      </section>
    </Shell>
  );
}
