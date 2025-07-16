from curl_cffi import AsyncSession

from config import settings


async def analize_toxicity(text: str) -> float:
    async with AsyncSession(impersonate='chrome110') as s:
        analyze_request = {
            'comment': {'text': text},
            'requestedAttributes': {'TOXICITY': {}},
            'languages': ['ru', 'en']
        }
        link = f'{settings.toxic.api_url}?key={settings.toxic.api_key.get_secret_value()}'
        resp = await s.post(link, json=analyze_request)
        return resp.json()['attributeScores']['TOXICITY']['summaryScore']['value']
