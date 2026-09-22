from researcher import ResearchedIPO


def _score(ipo: ResearchedIPO) -> float:
    return (ipo.gmp_percent * 0.5) + (ipo.ai_score * 0.5)


def pick_top_3(ipos: list[ResearchedIPO]) -> list[ResearchedIPO]:
    return sorted(ipos, key=_score, reverse=True)[:3]
