from curl_cffi import AsyncSession

from config import API_KEY


async def analize_toxicity(text: str) -> float:
    async with AsyncSession(impersonate='chrome110') as s:
        analyze_request = {
            'comment': {'text': text},
            'requestedAttributes': {'TOXICITY': {}},
            'languages': ['ru', 'en']
        }
        link = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={API_KEY}'
        resp = await s.post(link, json=analyze_request)
        return resp.json()['attributeScores']['TOXICITY']['summaryScore']['value']
