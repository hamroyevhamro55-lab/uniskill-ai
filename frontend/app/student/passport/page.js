"use client";
import { useEffect, useState } from "react";
import Shell, { Level, Msg } from "../../../components/Shell";
import { api, CATEGORY } from "../../../lib/api";

export default function Passport() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => { api("/passport").then(setData).catch((x) => setErr(x.message)); }, []);

  return (
    <Shell role="student">
      <h1>Raqamli ko‘nikmalar pasporti</h1>
      <Msg error={err} />
      {data && (
        <>
          <p className="muted">{data.student.name}{data.student.faculty ? ` · ${data.student.faculty}` : ""}. Pasportga faqat ekspert tasdiqlagan, dalili bor ko‘nikmalar kiradi.</p>
          {data.skills.length === 0 && <section className="card muted">Hali tasdiqlangan ko‘nikma yo‘q. Dalil qo‘shing va ekspert tekshiruvini kuting.</section>}
          {data.skills.map((s) => (
            <section className="card" key={s.skill.id}>
              <div className="ev-head"><b>{s.skill.name}</b> <span className="muted">· {CATEGORY[s.skill.category]}</span> <Level value={s.level} /></div>
              <ul className="plain">
                {s.evidence.map((e) => (
                  <li key={e.id} className="small">{e.title} — daraja {e.level}{e.verified_at ? `, ${new Date(e.verified_at).toLocaleDateString("uz-UZ")}` : ""}{e.url ? <> · <a href={e.url} target="_blank" rel="noopener noreferrer">havola</a></> : null}</li>
                ))}
              </ul>
            </section>
          ))}
        </>
      )}
    </Shell>
  );
}
