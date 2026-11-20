"use client";
import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken, getUser, HOME } from "../lib/api";

export default function Landing() {
  const router = useRouter();
  useEffect(() => {
    const u = getUser();
    if (getToken() && u) router.replace(HOME[u.role]);
  }, [router]);
  return (
    <div className="hero">
      <div className="brand big">UniSkill <span>AI</span></div>
      <h1>Bilimdan amaliy ko‘nikmaga, ta’limdan kasbiy muvaffaqiyatga</h1>
      <p>Talabaning kompetensiyasini aniqlang, rivojlantiring va dalillar asosida tasdiqlang.</p>
      <div className="steps">
        <div><b>1</b> Aniqlash</div><div><b>2</b> Rivojlantirish</div><div><b>3</b> Tasdiqlash</div>
      </div>
      <div className="row center-row">
        <Link className="btn" href="/login">Kirish</Link>
        <Link className="btn secondary" href="/register">Ro‘yxatdan o‘tish</Link>
      </div>
    </div>
  );
}
