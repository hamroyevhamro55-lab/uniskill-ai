const BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export const getToken = () => (typeof window === "undefined" ? null : localStorage.getItem("token"));
export const getUser = () => {
  try { return JSON.parse(localStorage.getItem("user") || "null"); } catch { return null; }
};
export function saveSession(token, user) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}
export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

export async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const t = getToken();
  if (t) headers.Authorization = `Bearer ${t}`;
  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new Error("Serverga ulanib bo'lmadi. Keyinroq urinib ko'ring.");
  }
  if (res.status === 401 && t) {
    logout();
    window.location.href = "/login";
    throw new Error("Sessiya tugadi");
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = data.detail;
    throw new Error(typeof d === "string" ? d : Array.isArray(d) ? "Kiritilgan ma'lumotlarni tekshiring" : "Xatolik yuz berdi");
  }
  return data;
}

export const HOME = { student: "/student", university: "/university", employer: "/employer" };
export const CATEGORY = { academic: "Akademik", practical: "Amaliy", digital: "Raqamli", personal: "Shaxsiy" };
export const STATUS = { pending: "Tekshiruvda", verified: "Tasdiqlangan", rejected: "Rad etilgan", self: "O'zini baholash" };
export const KIND = { course: "Kurs", project: "Loyiha", mentoring: "Mentorlik", internship: "Stajirovka", reassess: "Qayta baholash" };
