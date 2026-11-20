"""AI tahlil. ANTHROPIC_API_KEY bo'lsa Claude ishlatiladi, bo'lmasa oddiy qoidalar asosidagi zaxira.

AI faqat dastlabki baho va tavsiya beradi; yakuniy tasdiqni ekspert (universitet) qiladi.
"""
import json
import re

from .config import AI_MODEL, ANTHROPIC_API_KEY

_client = None


def _get_client():
    global _client
    if _client is None and ANTHROPIC_API_KEY:
        import anthropic

        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, timeout=30.0)
    return _client


def _fallback(skill: str, etype: str, title: str, description: str, url: str | None, claimed: int) -> dict:
    score = 1
    text = f"{title} {description}"
    if len(text) > 120:
        score += 1
    if url:
        score += 1
    if etype in ("project", "assignment"):
        score += 1
    if etype == "certificate":
        score += 1
    level = max(1, min(score, claimed, 5))
    tips = []
    if not url:
        tips.append("Dalil havolasini (GitHub, sertifikat, taqdimot) qo'shing")
    if len(description) < 80:
        tips.append("Nima qilganingizni va natijani batafsilroq yozing")
    if etype == "self":
        tips.append("O'zini baholash tasdiq hisoblanmaydi: amaliy topshiriq yoki loyiha qo'shing")
    return {
        "level": level,
        "feedback": "Dastlabki (qoidalarga asoslangan) baho. " + ("; ".join(tips) + "." if tips else "Dalil yetarli ko'rinadi, ekspert tekshiradi."),
        "source": "rules",
    }


def analyze_evidence(skill: str, etype: str, title: str, description: str, url: str | None, claimed: int) -> dict:
    client = _get_client()
    if not client:
        return _fallback(skill, etype, title, description, url, claimed)
    prompt = (
        "Sen universitet talabasi kompetensiyasini dastlabki baholovchi yordamchisan. "
        "Quyidagi dalilni 1-5 shkala bo'yicha baholab, o'zbek tilida qisqa tavsiya ber. "
        "Faqat dalilda ko'ringan narsaga tayan; taxmin qilma. Yakuniy qarorni ekspert qiladi.\n\n"
        f"Kompetensiya: {skill}\nDalil turi: {etype}\nSarlavha: {title}\nTavsif: {description}\n"
        f"Havola: {url or 'yo`q'}\nTalaba da'vo qilgan daraja: {claimed}\n\n"
        'Faqat JSON qaytar: {"level": 1-5 butun son, "feedback": "2-3 gap"}'
    )
    try:
        msg = client.messages.create(
            model=AI_MODEL, max_tokens=400, messages=[{"role": "user", "content": prompt}]
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        m = re.search(r"\{.*\}", text, re.S)
        data = json.loads(m.group(0))
        level = max(1, min(int(data["level"]), 5))
        return {"level": level, "feedback": str(data["feedback"])[:1500], "source": "claude"}
    except Exception:
        return _fallback(skill, etype, title, description, url, claimed)
