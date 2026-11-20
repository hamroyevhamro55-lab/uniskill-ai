"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getToken, getUser, logout, HOME } from "../lib/api";

const NAV = {
  student: [["/student", "Bosh sahifa"], ["/student/evidence", "Dalillar"], ["/student/roadmap", "Roadmap"], ["/student/passport", "Pasport"]],
  university: [["/university", "Tahlil va tekshiruv"]],
  employer: [["/employer", "Nomzodlar"]],
};

export default function Shell({ role, children }) {
  const router = useRouter();
  const path = usePathname();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const u = getUser();
    if (!getToken() || !u) return router.replace("/login");
    if (u.role !== role) return router.replace(HOME[u.role]);
    setUser(u);
  }, [role, router]);

  if (!user) return <div className="center muted">Yuklanmoqda…</div>;
  return (
    <>
      <header className="top">
        <div className="brand">UniSkill <span>AI</span></div>
        <nav>
          {NAV[role].map(([href, label]) => (
            <Link key={href} href={href} className={path === href ? "active" : ""}>{label}</Link>
          ))}
        </nav>
        <div className="who">
          <span>{user.name}</span>
          <button className="ghost" onClick={() => { logout(); router.push("/login"); }}>Chiqish</button>
        </div>
      </header>
      <main className="wrap">{children}</main>
    </>
  );
}

export function Msg({ error, ok }) {
  if (!error && !ok) return null;
  return <div className={error ? "alert err" : "alert ok"} role="alert">{error || ok}</div>;
}

export function Level({ value, max = 5 }) {
  return (
    <span className="dots" aria-label={`${value} / ${max}`}>
      {Array.from({ length: max }, (_, i) => <i key={i} className={i < value ? "on" : ""} />)}
    </span>
  );
}
