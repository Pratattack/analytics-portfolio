"""Site-only copy changes to hosted report copies; analytical sources stay intact."""
import re

def refine_visitor_text(text):
    rewrites = {
        'CFO Advisory Memo — Working Capital and Liquidity': 'CFO advisory memo on working capital and liquidity',
        'SEC XBRL reconciliation — October 27, 2026': 'SEC XBRL reconciliation dated October 27, 2026',
        'Fifteen-company SEC XBRL benchmark — ten companies added October 27, 2026': 'Fifteen-company SEC XBRL benchmark, expanded October 27, 2026',
        'Executive decision brief — semiconductor equipment inventory': 'Executive decision brief for semiconductor equipment inventory',
        'Executive decision brief — freight rail capital and cash returns': 'Executive decision brief for freight rail capital and cash returns',
        'Texas — automation; North Carolina — automation; Michigan — hardening': 'Automation in Texas and North Carolina; hardening in Michigan',
        'DILIGENCE ONLY — NO BUDGET APPROVAL': 'DILIGENCE ONLY. BUDGET APPROVAL WITHHELD.',
        'No — evidence/data gates not satisfied': 'Not approved. Evidence and data checks are not satisfied.',
        "row.utility_name+' — '+row.state": "row.utility_name+' ('+row.state+')'",
        "row.data_flags?'Review':'—'": "row.data_flags?'Review':'None'",
    }
    for before, after in rewrites.items():
        text = text.replace(before, after)
    # Missing-value markers are labels, not numeric zeroes.
    text = text.replace("'—'", "'Not available'").replace('>—<', '>Not available<')
    text = re.sub(r'\[([A-Z]+) — FY end ', r'[\1: FY end ', text)
    if '—' in text:
        raise ValueError('Unreviewed em dash remains in hosted copy')
    return text
