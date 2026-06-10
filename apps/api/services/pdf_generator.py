import io
import datetime
from xhtml2pdf import pisa

def format_date(iso_str: str) -> str:
    try:
        # Standard ISO timestamp like "2026-06-10T12:15:00.000Z"
        dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except Exception:
        return iso_str

def generate_report_pdf(report_data: dict) -> bytes:
    product = report_data.get("product", "Thermal Packaging")
    region = report_data.get("region", "Target Region")
    generated_at = format_date(report_data.get("generated_at", ""))
    
    executive_summary = report_data.get("executive_summary", "")
    fit_score = report_data.get("product_regional_fit", {}).get("fit_score", 0)
    fit_rationale = report_data.get("product_regional_fit", {}).get("fit_rationale", "")
    
    attractiveness_score = report_data.get("market_attractiveness_score", 0)
    breakdown = report_data.get("market_attractiveness_breakdown", {})
    
    # Build HTML with inline CSS matching professional corporate PDF layouts
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: letter;
    margin: 2cm 1.5cm 2cm 1.5cm;
}}
body {{
    font-family: 'Helvetica', 'Arial', sans-serif;
    color: #2D3748;
    line-height: 1.4;
    font-size: 9pt;
}}
h1, h2, h3, h4 {{
    color: #0A0F1E;
    font-family: 'Helvetica', 'Arial', sans-serif;
}}
.cover-page {{
    text-align: center;
    padding-top: 4cm;
}}
.cover-title {{
    font-size: 26pt;
    font-weight: bold;
    color: #0A0F1E;
    margin-bottom: 15px;
    line-height: 1.2;
}}
.cover-subtitle {{
    font-size: 13pt;
    color: #2D7DD2;
    margin-bottom: 50px;
    font-weight: bold;
    text-transform: uppercase;
}}
.cover-meta {{
    margin-top: 4cm;
    font-size: 10pt;
    color: #718096;
    line-height: 1.8;
}}
.section {{
    margin-bottom: 25px;
}}
.section-title {{
    font-size: 12pt;
    font-weight: bold;
    color: #0A0F1E;
    border-bottom: 1.5px solid #2D7DD2;
    padding-bottom: 4px;
    margin-bottom: 12px;
    text-transform: uppercase;
}}
.summary-box {{
    background-color: #F8FAFC;
    border-left: 4px solid #2D7DD2;
    padding: 10px 12px;
    margin-bottom: 15px;
    font-size: 9.5pt;
    color: #334155;
    line-height: 1.4;
}}
.fit-box {{
    background-color: #F0F7FF;
    border-left: 4px solid #3B82F6;
    padding: 10px 12px;
    margin-bottom: 15px;
    font-size: 9pt;
    color: #1E3A8A;
    line-height: 1.4;
}}
.score-card {{
    background-color: #0A0F1E;
    color: #FFFFFF;
    padding: 12px;
    text-align: center;
    border-radius: 6px;
}}
.score-val {{
    font-size: 24pt;
    font-weight: bold;
    color: #38BDF8;
}}
.score-label {{
    font-size: 8pt;
    font-weight: bold;
    color: #94A3B8;
    text-transform: uppercase;
}}
.table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 15px;
}}
.table th {{
    background-color: #0A0F1E;
    color: #FFFFFF;
    font-weight: bold;
    text-align: left;
    padding: 6px 8px;
    font-size: 8pt;
    border: 1px solid #1E293B;
}}
.table td {{
    padding: 6px 8px;
    border: 1px solid #E2E8F0;
    font-size: 8pt;
    color: #334155;
    vertical-align: top;
}}
.table tr:nth-child(even) td {{
    background-color: #F8FAFC;
}}
.badge {{
    padding: 2px 4px;
    font-size: 7pt;
    font-weight: bold;
    border-radius: 3px;
    text-align: center;
}}
.badge-high {{
    background-color: #FEE2E2;
    color: #991B1B;
}}
.badge-medium {{
    background-color: #FEF3C7;
    color: #92400E;
}}
.badge-low {{
    background-color: #D1FAE5;
    color: #065F46;
}}
.comp-column {{
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    padding: 10px;
    border-radius: 5px;
}}
.comp-title {{
    font-weight: bold;
    font-size: 8.5pt;
    color: #0A0F1E;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 4px;
    margin-bottom: 8px;
    text-transform: uppercase;
}}
.recommendation-card {{
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 10px 12px;
    margin-bottom: 10px;
}}
.rec-header {{
    margin-bottom: 6px;
}}
.rec-priority {{
    font-weight: bold;
    font-size: 8.5pt;
    color: #E53E3E;
    text-transform: uppercase;
}}
.rec-priority-2 {{
    color: #D97706;
}}
.rec-priority-3 {{
    color: #2563EB;
}}
.rec-timeline {{
    font-size: 8pt;
    color: #718096;
}}
.rec-action {{
    font-weight: bold;
    font-size: 9.5pt;
    color: #0A0F1E;
    margin-bottom: 4px;
}}
.rec-outcome {{
    font-size: 8.5pt;
    color: #4A5568;
    margin-top: 4px;
}}
.page-break {{
    page-break-before: always;
}}
.bullet-list {{
    margin-top: 5px;
    margin-bottom: 5px;
    padding-left: 20px;
}}
.bullet-list li {{
    margin-bottom: 4px;
    font-size: 8.5pt;
}}
.company-cell {{
    font-weight: bold;
    color: #0A0F1E;
}}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <div style="font-size: 10pt; font-weight: bold; color: #718096; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 2cm;">
        Market Intelligence Brief
    </div>
    <div class="cover-title">
        {product}
    </div>
    <div class="cover-subtitle">
        Export Feasibility & Client Discovery Report: {region}
    </div>
    <div style="width: 3cm; height: 3px; background-color: #2D7DD2; margin: 0 auto 2cm auto;"></div>
    
    <div class="cover-meta">
        <strong>Prepared For:</strong> Thermal Packaging Sales & Trade Operations<br/>
        <strong>Export Market:</strong> {region}<br/>
        <strong>Date of Synthesis:</strong> {generated_at}<br/>
        <strong>Platform:</strong> ExportIntel Platform
    </div>
</div>

<div class="page-break"></div>

<!-- EXECUTIVE SUMMARY & KEY STATS -->
<div class="section">
    <div class="section-title">Executive Summary</div>
    <div class="summary-box">
        {executive_summary}
    </div>
    
    <table style="width: 100%; border: 0; margin-top: 15px;">
        <tr>
            <td style="width: 48%; border: 0; padding-right: 8px;">
                <div class="score-card">
                    <div class="score-val">{attractiveness_score}/100</div>
                    <div class="score-label">Market Attractiveness</div>
                </div>
                <div style="margin-top: 10px; font-size: 8pt; color: #718096; text-align: center;">
                    Size: {breakdown.get('market_size', 0)}/20 | 
                    Growth: {breakdown.get('growth_trajectory', 0)}/25 | 
                    Competitors: {breakdown.get('competitive_intensity', 0)}/20 | 
                    Events: {breakdown.get('event_driven_demand', 0)}/35
                </div>
            </td>
            <td style="width: 48%; border: 0; padding-left: 8px;">
                <div class="score-card" style="background-color: #2D7DD2;">
                    <div class="score-val">{fit_score}/100</div>
                    <div class="score-label">Product-Regional Fit</div>
                </div>
                <div style="margin-top: 10px; font-size: 8pt; color: #718096; text-align: center;">
                    Evaluated against regional regulatory requirements & standard product certifications.
                </div>
            </td>
        </tr>
    </table>
</div>

<div class="section" style="margin-top: 15px;">
    <div class="section-title">Product Fit & Regulatory Rationale</div>
    <div class="fit-box">
        {fit_rationale}
    </div>
</div>

<div class="page-break"></div>

<!-- SECTOR DEMAND ANALYSIS -->
<div class="section">
    <div class="section-title">Sector Demand Analysis</div>
    <p style="font-size: 8.5pt; color: #718096; margin-bottom: 12px; margin-top: 0;">
        Primary target sectors ranked by local cold chain validation criteria.
    </p>
    
    <table class="table">
        <thead>
            <tr>
                <th style="width: 8%;">Rank</th>
                <th style="width: 30%;">Sector</th>
                <th style="width: 12%;">Demand</th>
                <th style="width: 15%;">Difficulty</th>
                <th style="width: 35%;">Key Drivers</th>
            </tr>
        </thead>
        <tbody>
"""

    top_sectors = report_data.get("top_sectors", [])
    try:
        top_sectors = sorted(top_sectors, key=lambda x: x.get("rank", 99))
    except Exception:
        pass
        
    for s in top_sectors:
        drivers = ", ".join(s.get("key_drivers", []))
        diff = s.get("entry_difficulty", "Medium")
        diff_class = "badge-medium"
        if diff.lower() == "high":
            diff_class = "badge-high"
        elif diff.lower() == "low":
            diff_class = "badge-low"
            
        html_content += f"""
            <tr>
                <td style="text-align: center; font-weight: bold;">{s.get('rank', 1)}</td>
                <td style="font-weight: bold; color: #0A0F1E;">{s.get('sector_name', '')}</td>
                <td style="text-align: center; font-weight: bold;">{s.get('demand_score', 0)}/10</td>
                <td><div class="badge {diff_class}">{diff}</div></td>
                <td>{drivers}</td>
            </tr>
        """
        
    html_content += """
        </tbody>
    </table>
</div>

<!-- TOP COMPANIES PER SECTOR -->
<div class="section">
    <div class="section-title">Sector Top Prospects & Needs</div>
    <p style="font-size: 8.5pt; color: #718096; margin-bottom: 12px; margin-top: 0;">
        Identified organizations within each sector and their target packaging requirements.
    </p>
"""

    for s in top_sectors:
        html_content += f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 6px; margin-bottom: 15px;">
        <div style="font-weight: bold; font-size: 9.5pt; color: #0A0F1E; margin-bottom: 8px; border-bottom: 1px solid #E2E8F0; padding-bottom: 3px;">
            Sector: {s.get('sector_name', '')} (Rank #{s.get('rank', 1)})
        </div>
        <table style="width: 100%; border: 0; font-size: 8pt;">
        """
        for c in s.get("top_companies", []):
            html_content += f"""
            <tr style="border-bottom: 1px solid #E2E8F0;">
                <td style="width: 25%; font-weight: bold; color: #2D7DD2; padding: 4px 0;">{c.get('company', '')}</td>
                <td style="width: 18%; font-style: italic; color: #10B981; padding: 4px 0;">Need: {c.get('estimated_need', '')}</td>
                <td style="width: 57%; color: #4A5568; padding: 4px 0;">{c.get('rationale', '')}</td>
            </tr>
            """
        html_content += """
        </table>
    </div>
        """

    html_content += """
</div>

<div class="page-break"></div>

<!-- POTENTIAL CLIENTS DISCOVERY TABLE -->
<div class="section">
    <div class="section-title">Top 10 Target Clients Discovery</div>
    <p style="font-size: 8.5pt; color: #718096; margin-bottom: 12px; margin-top: 0;">
        Qualified clients with high thermal management payloads. Handpicked based on trade footprint and pipeline volume.
    </p>
    
    <table class="table">
        <thead>
            <tr>
                <th style="width: 25%;">Company Name</th>
                <th style="width: 20%;">Sector</th>
                <th style="width: 15%;">Annual Need</th>
                <th style="width: 40%;">Strategy & Rationale</th>
            </tr>
        </thead>
        <tbody>
"""

    potential_clients = report_data.get("potential_clients", [])
    for c in potential_clients[:10]:
        html_content += f"""
            <tr>
                <td class="company-cell">{c.get('company_name', '')}<br/><span style="font-size: 7.5pt; font-weight: normal; color: #718096;">{c.get('region_country', '')}</span></td>
                <td>{c.get('sector', '')}</td>
                <td style="color: #10B981; font-weight: bold;">{c.get('estimated_annual_need', '')}</td>
                <td>
                    <strong>Rationale:</strong> {c.get('relevance_rationale', '')}<br/>
                    <strong style="color: #2D7DD2;">Approach:</strong> {c.get('contact_strategy', '')}
                </td>
            </tr>
        """

    html_content += """
        </tbody>
    </table>
</div>

<div class="page-break"></div>

<!-- EVENT WINDOWS TIMELINE & PROCUREMENT WINDOWS -->
<div class="section">
    <div class="section-title">12-Month Procurement Windows & Events</div>
    <p style="font-size: 8.5pt; color: #718096; margin-bottom: 12px; margin-top: 0;">
        Target events mapped by regional procurement runup windows. Engage clients 90 days prior to event date.
    </p>
    
    <table class="table">
        <thead>
            <tr>
                <th style="width: 25%;">Event Name</th>
                <th style="width: 15%;">Event Date</th>
                <th style="width: 20%;">Procurement Window</th>
                <th style="width: 15%;">Sector</th>
                <th style="width: 25%;">Outreach Strategy</th>
            </tr>
        </thead>
        <tbody>
"""

    events = report_data.get("event_procurement_windows", [])
    for e in events:
        p_start = format_date(e.get("procurement_start", ""))
        html_content += f"""
            <tr>
                <td class="company-cell">{e.get('event', '')}<br/><span class="badge badge-medium" style="margin-top: 3px;">Spike Index: {e.get('demand_spike_score', 0)}/10</span></td>
                <td>{e.get('date_window', '')}</td>
                <td style="font-weight: bold; color: #D97706;">Starts: {p_start}</td>
                <td>{e.get('sector', '')}</td>
                <td style="font-size: 7.5pt; color: #4A5568;">{e.get('outreach_recommendation', '')}</td>
            </tr>
        """

    html_content += """
        </tbody>
    </table>
</div>

<!-- COMPETITIVE LANDSCAPE -->
<div class="section" style="margin-top: 20px;">
    <div class="section-title">Competitive Landscape & Gaps</div>
    
    <table style="width: 100%; border: 0; margin-top: 10px;">
        <tr>
            <td style="width: 32%; border: 0; padding-right: 8px;">
                <div class="comp-column" style="min-height: 4.5cm;">
                    <div class="comp-title" style="color: #DC2626;">Main Competitors</div>
                    <ul class="bullet-list" style="margin: 0; padding-left: 12px; list-style-type: square; color: #4B5563;">
"""
    comp_landscape = report_data.get("competitive_landscape", {})
    for competitor in comp_landscape.get("main_competitors", []):
        html_content += f"                        <li style='font-weight: bold; color: #1F2937;'>{competitor}</li>"
        
    html_content += """
                    </ul>
                </div>
            </td>
            <td style="width: 32%; border: 0; padding-left: 4px; padding-right: 4px;">
                <div class="comp-column" style="min-height: 4.5cm;">
                    <div class="comp-title" style="color: #2563EB;">Advantages to Emphasize</div>
                    <ul class="bullet-list" style="margin: 0; padding-left: 12px; list-style-type: check; color: #4B5563;">
"""
    for adv in comp_landscape.get("competitive_advantages_to_emphasize", []):
        html_content += f"                        <li>{adv}</li>"
        
    html_content += """
                    </ul>
                </div>
            </td>
            <td style="width: 32%; border: 0; padding-left: 8px;">
                <div class="comp-column" style="min-height: 4.5cm;">
                    <div class="comp-title" style="color: #059669;">Market Gaps</div>
                    <ul class="bullet-list" style="margin: 0; padding-left: 12px; list-style-type: circle; color: #4B5563;">
"""
    for gap in comp_landscape.get("market_gaps", []):
        html_content += f"                        <li style='font-weight: bold; color: #047857;'>{gap}</li>"
        
    html_content += """
                    </ul>
                </div>
            </td>
        </tr>
    </table>
</div>

<div class="page-break"></div>

<!-- STRATEGIC RECOMMENDATIONS -->
<div class="section">
    <div class="section-title">Strategic Action Recommendations</div>
    <p style="font-size: 8.5pt; color: #718096; margin-bottom: 12px; margin-top: 0;">
        Recommended immediate, mid-term, and long-term actions for successful regional export setup.
    </p>
"""

    recommendations = report_data.get("strategic_recommendations", [])
    try:
        recommendations = sorted(recommendations, key=lambda x: x.get("priority", 99))
    except Exception:
        pass
        
    for rec in recommendations:
        priority = rec.get("priority", 1)
        priority_label = f"Priority {priority} (Immediate)"
        priority_class = "rec-priority"
        if priority == 2:
            priority_label = f"Priority {priority} (Mid-term)"
            priority_class = "rec-priority rec-priority-2"
        elif priority == 3:
            priority_label = f"Priority {priority} (Long-term)"
            priority_class = "rec-priority rec-priority-3"
            
        html_content += f"""
    <div class="recommendation-card">
        <table style="width: 100%; border: 0; margin-bottom: 4px;">
            <tr>
                <td style="border: 0; padding: 0;"><span class="{priority_class}">{priority_label}</span></td>
                <td style="border: 0; padding: 0; text-align: right;"><span class="rec-timeline">Timeline: {rec.get('timeline', '')}</span></td>
            </tr>
        </table>
        <div class="rec-action">{rec.get('action', '')}</div>
        <div class="rec-outcome"><strong>Expected Outcome:</strong> {rec.get('expected_outcome', '')}</div>
    </div>
        """

    html_content += """
</div>

</body>
</html>
"""

    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if pisa_status.err:
        raise Exception(f"xhtml2pdf error: {pisa_status.err}")
        
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
