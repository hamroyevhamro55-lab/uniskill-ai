"use client";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, saveSession, HOME } from "../../lib/api";
import { Msg } from "../../components/Shell";

export default function Register() {
  const router = useRouter();
  const [f, setF] = useState({ name: "", email: "", password: "", role: "student", faculty: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setErr(""); setBusy(true);
    try {
      const body = { ...f, faculty: f.role === "student" ? f.faculty || null : null };
      const r = await api("/auth/register", { method: "POST", body });
      saveSession(r.token, r.user);
      router.push(HOME[r.user.role]);
    } catch (x) { setErr(x.message); } finally { setBusy(false); }
  }

  return (
    <div className="auth">
      <div className="brand">UniSkill <span>AI</span></div>
      <h2>Ro‘yxatdan o‘tish</h2>
      <form onSubmit={submit}>
        <label>Rol
          <select value={f.role} onChange={set("role")}>
            <option value="student">Talaba</option>
            <option value="employer">Ish beruvchi</option>
          </select>
        </label>
        <label>Ism-familiya<input required minLength={2} value={f.name} onChange={set("name")} /></label>
        <label>Email<input type="email" required value={f.email} onChange={set("email")} /></label>
        {f.role === "student" && <label>Fakultet / yo‘nalish<input value={f.faculty} onChange={set("faculty")} placeholder="Masalan: Dasturiy injiniring" /></label>}
        <label>Parol (kamida 8 belgi)<input type="password" required minLength={8} maxLength={72} value={f.password} onChange={set("password")} /></label>
        <Msg error={err} />
        <button className="btn" disabled={busy}>{busy ? "Yuborilmoqda…" : "Ro‘yxatdan o‘tish"}</button>
      </form>
      <p className="muted">Allaqachon akkaunt bormi? <Link href="/login">Kirish</Link></p>
      <p className="muted small">Universitet (ekspert) akkauntlari administrator tomonidan yaratiladi.</p>
    </div>
  );
}
