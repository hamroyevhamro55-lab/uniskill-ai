"use client";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, saveSession, HOME } from "../../lib/api";
import { Msg } from "../../components/Shell";

export default function Login() {
  const router = useRouter();
  const [f, setF] = useState({ email: "", password: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setErr(""); setBusy(true);
    try {
      const r = await api("/auth/login", { method: "POST", body: f });
      saveSession(r.token, r.user);
      router.push(HOME[r.user.role]);
    } catch (x) { setErr(x.message); } finally { setBusy(false); }
  }
  const demo = (email) => setF({ email, password: "demo1234" });

  return (
    <div className="auth">
      <div className="brand">UniSkill <span>AI</span></div>
      <h2>Kirish</h2>
      <form onSubmit={submit}>
        <label>Email<input type="email" required value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></label>
        <label>Parol<input type="password" required value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></label>
        <Msg error={err} />
        <button className="btn" disabled={busy}>{busy ? "Kirilmoqda…" : "Kirish"}</button>
      </form>
      <p className="muted">Akkaunt yo‘qmi? <Link href="/register">Ro‘yxatdan o‘ting</Link></p>
      <div className="demo">
        <span className="muted">Demo kirish:</span>
        <button className="ghost" onClick={() => demo("student@demo.uz")}>Talaba</button>
        <button className="ghost" onClick={() => demo("uni@demo.uz")}>Universitet</button>
        <button className="ghost" onClick={() => demo("hr@demo.uz")}>Ish beruvchi</button>
      </div>
    </div>
  );
}
