import json
import google.generativeai as genai
from dataclasses import dataclass
from scraper import IPO

@dataclass
class ResearchedIPO:
    name: str
    gmp_percent: float
    issue_price: float
    lot_size: int
    min_investment: float
    estimated_listing: float
    strong_points: list[str]
    weak_points: list[str]
    ai_score: int


def ask_gemini(ipo_name: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6-flash")
    prompt = f"""You are an Indian stock market analyst. Analyze the {ipo_name} IPO.

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "strong_points": ["max 15 words", "point 2", "point 3"],
  "weak_points": ["max 15 words", "point 2"],
  "ai_score": 7
}}"""
    response = model.generate_content(prompt)
    return response.text.strip()


def _fallback(ipo: IPO) -> ResearchedIPO:
    return ResearchedIPO(
        name=ipo.name, gmp_percent=ipo.gmp_percent, issue_price=ipo.issue_price,
        lot_size=ipo.lot_size, min_investment=ipo.min_investment,
        estimated_listing=ipo.estimated_listing,
        strong_points=["Research unavailable"],
        weak_points=["Research unavailable"],
        ai_score=5,
    )


def research_ipos(ipos: list[IPO], gemini_key: str) -> list[ResearchedIPO]:
    results = []
    for ipo in ipos:
        try:
            raw = ask_gemini(ipo.name, gemini_key)
            clean = raw.removeprefix("```json").removesuffix("```").strip()
            data = json.loads(clean)
            results.append(ResearchedIPO(
                name=ipo.name, gmp_percent=ipo.gmp_percent, issue_price=ipo.issue_price,
                lot_size=ipo.lot_size, min_investment=ipo.min_investment,
                estimated_listing=ipo.estimated_listing,
                strong_points=data.get("strong_points", [])[:3],
                weak_points=data.get("weak_points", [])[:2],
                ai_score=int(data.get("ai_score", 5)),
            ))
        except Exception:
            results.append(_fallback(ipo))
    return results
