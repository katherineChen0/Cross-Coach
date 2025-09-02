import asyncio
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import SessionLocal
from ..models import LogEntry, CorrelationInsight
from ..core.config import settings
import numpy as np
import httpx


async def generate_summary(text: str) -> str:
	if not settings.openai_api_key:
		return "No API key configured; summary unavailable."
	headers = {
		"Authorization": f"Bearer {settings.openai_api_key}",
		"Content-Type": "application/json",
	}
	payload = {
		"model": settings.openai_model,
		"messages": [
			{"role": "system", "content": "You are an assistant summarizing journal entries into concise weekly insights."},
			{"role": "user", "content": f"Summarize these entries:\n{text}"},
		],
	}
	async with httpx.AsyncClient(base_url=settings.openai_api_base, timeout=60) as client:
		resp = await client.post("/chat/completions", headers=headers, json=payload)
		resp.raise_for_status()
		data = resp.json()
		return data["choices"][0]["message"]["content"].strip()


def compute_correlations(pairs: list[tuple[float, float]]) -> float | None:
	if len(pairs) < 3:
		return None
	x = np.array([p[0] for p in pairs], dtype=float)
	y = np.array([p[1] for p in pairs], dtype=float)
	if np.std(x) == 0 or np.std(y) == 0:
		return None
	r = float(np.corrcoef(x, y)[0, 1])
	return r


def run_once():
	db: Session = SessionLocal()
	try:
		# For each user-week compute correlations across domains
		users_dates = db.execute(select(LogEntry.user_id, LogEntry.date)).all()
		user_ids = list({u for u, _ in users_dates})
		for user_id in user_ids:
			# Determine last 7 days window
			end = date.today()
			start = end - timedelta(days=6)
			logs = db.execute(
				select(LogEntry).where(LogEntry.user_id == user_id, LogEntry.date >= start, LogEntry.date <= end)
			).scalars().all()
			# Build domain -> date -> value mapping
			domain_to_values: dict[str, dict[date, float]] = {}
			for log in logs:
				if log.value is None:
					continue
				domain_to_values.setdefault(log.domain.value, {})[log.date] = float(log.value)
			# Compute pairwise correlations
			domains = list(domain_to_values.keys())
			correlations: dict[str, float] = {}
			for i in range(len(domains)):
				for j in range(i + 1, len(domains)):
					d1, d2 = domains[i], domains[j]
					pairs = []
					for d in (start + timedelta(days=k) for k in range(7)):
						if d in domain_to_values[d1] and d in domain_to_values[d2]:
							pairs.append((domain_to_values[d1][d], domain_to_values[d2][d]))
					r = compute_correlations(pairs)
					if r is not None:
						correlations[f"{d1}~{d2}"] = r
			# Summarize journal entries
			journals = [l.notes for l in logs if l.domain.value == "reflection" and l.notes]
			summary_text = "\n\n".join(journals)
			if summary_text:
				try:
					summary = asyncio.run(generate_summary(summary_text))
				except Exception:
					summary = None
			else:
				summary = None
			# Create correlation insight
			if correlations:
				for correlation_key, correlation_score in correlations.items():
					description = f"Correlation between {correlation_key.replace('~', ' and ')}: {correlation_score:.3f}"
					insight = CorrelationInsight(
						user_id=user_id,
						description=description,
						correlation_score=correlation_score
					)
					db.add(insight)
			db.commit()
	finally:
		db.close()


if __name__ == "__main__":
	run_once() 