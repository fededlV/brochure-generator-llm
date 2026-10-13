from typing import List, Dict

LINK_SELECTION_SYSTEM_PROMPT = """You are an expert business researcher and digital analyst.
Your task is to analyze a company's website landing page and a list of internal links found on the site.
You must select the most relevant pages (typically 2 to 4) that would provide essential depth for creating a comprehensive company brochure.

High-priority pages to select:
- About Us / Company / Story / Mission
- Products / Services / Solutions / Platform / Technology
- Pricing / Plans (if relevant)
- Team / Leadership
- Careers / Culture / Values

Pages to STRICTLY IGNORE:
- Login, Sign In, Register, Forgot Password
- Privacy Policy, Terms of Service, Cookie Policy, Legal, Disclaimers
- Documentation search anchors, API references
- External social media profiles (Twitter, LinkedIn, Facebook, Instagram)
- Language switchers, cart, checkout, status pages

Output Requirement:
You MUST respond with valid JSON adhering to this exact schema:
{
  "selected_links": [
    {
      "url": "https://...",
      "reason": "Why this page is vital for the brochure"
    }
  ]
}
If no suitable internal links exist, return an empty list: {"selected_links": []}.
Do not include any explanation or markdown formatting outside of the JSON block.
"""

def build_link_selection_user_prompt(landing_url: str, landing_text: str, candidate_links: List[str], max_selection: int = 4) -> str:
    links_formatted = "\n".join(f"- {link}" for link in candidate_links[:50])
    return f"""Target Company URL: {landing_url}

Landing Page Summary / Content:
---
{landing_text[:2500]}
---

Candidate Links found on website:
---
{links_formatted}
---

Select at most {max_selection} of the most informative links for a company brochure.
Return ONLY valid JSON.
"""


AUDIENCE_DIRECTIVES: Dict[str, str] = {
    "prospects": (
        "Focus on the value proposition, customer pain points solved, product benefits, "
        "differentiating capabilities, and clear calls-to-action for potential clients or buyers."
    ),
    "investors": (
        "Focus on the market opportunity, product-market fit, business model, proprietary technology, "
        "leadership team, traction, scalability, and competitive moat."
    ),
    "candidates": (
        "Focus on the company mission, engineering & workplace culture, leadership vision, "
        "growth opportunities, innovation focus, and why top talent should join."
    ),
    "general": (
        "Provide a balanced, high-impact company profile covering core identity, primary offerings, "
        "key achievements, and mission."
    )
}

TONE_DIRECTIVES: Dict[str, str] = {
    "professional": "Polished, authoritative, credible, and articulate corporate communication.",
    "energetic": "Inspiring, vibrant, modern tech-forward style that evokes excitement and momentum.",
    "minimalist": "Clean, punchy, bullet-driven executive summary with high signal-to-noise ratio."
}


def build_brochure_system_prompt(audience: str = "general", tone: str = "professional") -> str:
    audience_text = AUDIENCE_DIRECTIVES.get(audience, AUDIENCE_DIRECTIVES["general"])
    tone_text = TONE_DIRECTIVES.get(tone, TONE_DIRECTIVES["professional"])

    return f"""You are an elite corporate marketing strategist and copywriter.
Your goal is to synthesize raw scraped content from a company's website into a publication-ready, beautifully structured company brochure.

TARGET AUDIENCE: {audience.upper()}
{audience_text}

TONE & VOICE: {tone.upper()}
{tone_text}

FORMATTING GUIDELINES:
- Output clean, professional GitHub-flavored Markdown.
- Use a compelling `# Company Name: Value Proposition Headline` at the top.
- Include structured sections such as:
  - `## Executive Summary & Mission`
  - `## Core Products & Capabilities`
  - `## Market Advantage & Key Innovations`
  - `## Why Work With Us / Why Choose Us` (adapted to audience)
  - `## Leadership & Culture` (if info available)
  - `## Next Steps / Contact Information`
- Use bullet points, bold key phrases for scanability, and quote callouts (`>`) where impactful.
- Only synthesize information grounded in the provided scraped content; do not invent fictional metrics or unverifiable partnerships.
"""


def build_brochure_user_prompt(company_url: str, landing_content: str, subpages_content: List[Dict[str, str]]) -> str:
    subpages_text_blocks = []
    for idx, page in enumerate(subpages_content, 1):
        subpages_text_blocks.append(
            f"### Subpage {idx}: {page.get('title', 'Untitled')} ({page.get('url', '')})\n"
            f"{page.get('text', '')[:2500]}\n"
        )
    subpages_joined = "\n---\n".join(subpages_text_blocks) if subpages_text_blocks else "No secondary pages crawled."

    return f"""Company Base URL: {company_url}

=== LANDING PAGE CONTENT ===
{landing_content[:3000]}

=== SELECTED SUBPAGES CONTENT ===
{subpages_joined}

Please craft the comprehensive company brochure in Markdown now.
"""
