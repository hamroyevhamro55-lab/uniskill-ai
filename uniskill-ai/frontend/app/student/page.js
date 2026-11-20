"use client";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Shell, { Level, Msg } from "../../components/Shell";
import { api, CATEGORY } from "../../lib/api";

const STATUS_LABEL = { ok: "Yetarli", gap: "Yetishmaydi", unverified: "Tasdiqlanmagan" };

export default function StudentHome() {
  const [profs, setProfs] = useState([]);
  const [me, setMe] = useState(null);
  const [gap, setGap] = useState(null);
  const [err, setErr] = useState("");

  const load = useCallback(async () => {
    try {
      const [p, m, g] = await Promise.all([api("/professions"), api("/me"), api("/skill-gap")]);
      setProfs(p); setMe(m); setGap(g);
    } catch (x) { setErr(x.message); }
  }, []);
  useEffect(() => { load(); }, [load]);

  async function patch(body) {
    setErr("");
    try { setMe(await api("/me", { method: "PATCH", body })); setGap(await api("/skill-gap")); } catch (x) { setErr(x.message); }
  }

  return (
    <Shell role="student">
      <h1>Kompetensiya profilim</h1>
      <Msg error={err} />
      <section className="card">
        <label>Kasbiy maqsad
          <select value={me?.profession_id ?? ""} onChange={(e) => patch({ profession_id: e.target.value ? Number(e.target.value) : null })}>
            <option value="">— tanlang —</option>
            {profs.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
        </label>
        <label className="check">
          <input type="checkbox" checked={!!me?.consent_employers} onChange={(e) => patch({ consent_employers: e.target.checked })} />
          Ish beruvchilar tasdiqlangan profilimni ko‘rishiga roziman
        </label>
      </section>

      {gap?.profession ? (
        <>
          <section className="card ready">
            <div className="big-num">{gap.readiness}%</div>
            <div><b>{gap.profession.title}</b> uchun tayyorlik<div className="muted small">Faqat ekspert tasdiqlagan ko‘nikmalar hisoblanadi</div></div>
            <Link className="btn secondary" href="/student/roadmap">Roadmap →</Link>
          </section>
          <section className="card">
            <h2>Skill Gap</h2>
            <table>
              <thead><tr><th>Kompetensiya</th><th>Turi</th><th>Kerakli</th><th>Tasdiqlangan</th><th>Holat</th></tr></thead>
              <tbody>
                {gap.items.map((i) => (
                  <tr key={i.skill.id}>
                    <td>{i.skill.name}</td>
                    <td className="muted">{CATEGORY[i.skill.category]}</td>
                    <td><Level value={i.required} /></td>
                    <td><Level value={i.verified} /></td>
                    <td><span className={`tag ${i.status}`}>{STATUS_LABEL[i.status]}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="muted small">“Tasdiqlanmagan” — siz yetarli daraja da’vo qilgansiz, lekin ekspert hali tasdiqlamagan. <Link href="/student/evidence">Dalil qo‘shing</Link>.</p>
          </section>
        </>
      ) : (
        <section className="card muted">Skill Gap natijasini ko‘rish uchun kasbiy maqsadni tanlang.</section>
      )}
    </Shell>
  );
}
