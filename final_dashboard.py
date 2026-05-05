import streamlit as st
st.set_page_config( 
    page_title="ThreatVision SOC", 
    page_icon="   ", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)
# ui_render.py — Professional ThreatVision UI (imported by main dashboard) 
 
import time 
import pandas as pd 
import plotly.graph_objects as go 
from datetime import datetime 
 
# ============================================= 
# CSS Theme 
# ============================================= 
THEME_CSS = """ 
<style> 
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
); 
 
/* ── Global Reset ── */ 
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif !important; 
} 
.block-container { padding-top: 1.5rem !important; max-width: 1400px; } 
header[data-testid="stHeader"] { background: rgba(10,12,20,0.85); backdrop-filter: blur(12px); 
border-bottom: 1px solid rgba(255,255,255,0.04); } 
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1017 0%, #111827 100%); 
border-right: 1px solid rgba(255,255,255,0.04); } 
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; } 
 
/* ── Brand Header ── */ 
.brand-bar { 
    display: flex; align-items: center; justify-content: space-between; 
    padding: 0.6rem 1.2rem; margin-bottom: 1rem; 
    background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.7)); 
    border: 1px solid rgba(99,102,241,0.15); border-radius: 14px; 
    backdrop-filter: blur(16px); 
} 
.brand-title { 
    font-size: 1.45rem; font-weight: 800; letter-spacing: -0.03em; 
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 40%, #a78bfa 100%); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
} 
.brand-sub { color: #64748b; font-size: 0.78rem; font-weight: 500; letter-spacing: 0.04em; text-
transform: uppercase; } 
.live-dot { 
    width: 8px; height: 8px; background: #22c55e; border-radius: 50%; 
    display: inline-block; margin-right: 6px; box-shadow: 0 0 8px #22c55e; 
    animation: blink 1.6s infinite; 
} 
@keyframes blink { 
    0%,100% { opacity: 1; } 50% { opacity: 0.3; } 
} 
 
/* ── KPI Cards ── */ 
.kpi-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 0.7rem; margin-bottom: 1rem; 
} 
.kpi-card { 
    background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.6)); 
    border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; 
    padding: 1rem 1.1rem; position: relative; overflow: hidden; 
    transition: transform 0.2s, border-color 0.2s; 
} 
.kpi-card:hover { transform: translateY(-2px); border-color: rgba(99,102,241,0.3); } 
.kpi-card::before { 
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; 
    border-radius: 12px 12px 0 0; 
} 
.kpi-accent-indigo::before { background: linear-gradient(90deg, #6366f1, #818cf8); } 
.kpi-accent-red::before    { background: linear-gradient(90deg, #ef4444, #f87171); } 
.kpi-accent-emerald::before{ background: linear-gradient(90deg, #10b981, #34d399); } 
.kpi-accent-amber::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); } 
.kpi-accent-cyan::before   { background: linear-gradient(90deg, #06b6d4, #22d3ee); } 
.kpi-accent-violet::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); } 
.kpi-label  { font-size: 0.68rem; font-weight: 600; color: #64748b; text-transform: uppercase; 
letter-spacing: 0.06em; margin-bottom: 0.35rem; } 
.kpi-value  { font-size: 1.7rem; font-weight: 800; color: #f1f5f9; line-height: 1.1; } 
.kpi-sub    { font-size: 0.72rem; color: #475569; margin-top: 0.2rem; font-weight: 500; } 
.kpi-value.danger { color: #f87171; } 
.kpi-value.success{ color: #34d399; } 
 
/* ── Section Headers ── */ 
.section-hdr { 
    font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; 
    letter-spacing: 0.08em; margin: 0.8rem 0 0.5rem; padding-bottom: 0.3rem; 
    border-bottom: 1px solid rgba(255,255,255,0.04); 
} 
 
/* ── Panel (chart containers) ── */ 
.panel { 
    background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.5)); 
    border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; 
    padding: 1rem; margin-bottom: 0.7rem; 
} 
.panel-title { 
    font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; 
    letter-spacing: 0.06em; margin-bottom: 0.6rem; 
} 
 
/* ── Packet Feed ── */ 
.pkt { 
    display: grid; grid-template-columns: 72px 1fr auto; 
    align-items: center; gap: 0.6rem; 
    padding: 0.45rem 0.7rem; margin: 2px 0; border-radius: 8px; 
    border-left: 3px solid; font-size: 0.78rem; 
    background: rgba(15,23,42,0.7); 
    transition: background 0.15s; 
} 
.pkt:hover { background: rgba(30,41,59,0.9); } 
.pkt-time  { color: #475569; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; } 
.pkt-flow  { color: #cbd5e1; font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; } 
.pkt-meta  { text-align: right; } 
.pkt-proto { font-weight: 700; font-size: 0.7rem; padding: 1px 7px; border-radius: 4px; } 
.pkt-bytes { color: #64748b; font-size: 0.7rem; margin-left: 6px; } 
.proto-tcp  { color: #34d399; border-left-color: #10b981; } 
.proto-udp  { color: #fbbf24; border-left-color: #f59e0b; } 
.proto-http { color: #60a5fa; border-left-color: #3b82f6; } 
.proto-https{ color: #a78bfa; border-left-color: #8b5cf6; } 
.proto-dns  { color: #f472b6; border-left-color: #ec4899; } 
 
/* ── Alert Row ── */ 
.alert-row { 
    display: flex; align-items: center; gap: 0.6rem; 
    padding: 0.55rem 0.8rem; margin: 3px 0; border-radius: 8px; 
    background: linear-gradient(90deg, rgba(239,68,68,0.08), rgba(239,68,68,0.02)); 
    border: 1px solid rgba(239,68,68,0.15); font-size: 0.78rem; 
    animation: alertPulse 3s ease-in-out infinite; 
} 
@keyframes alertPulse { 
    0%,100% { border-color: rgba(239,68,68,0.15); } 50% { border-color: rgba(239,68,68,0.35); } 
} 
.alert-badge { 
    font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; 
    background: linear-gradient(135deg, #ef4444, #dc2626); color: white; 
    text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap; 
} 
.alert-text { color: #fca5a5; flex: 1; } 
.alert-conf { color: #64748b; font-size: 0.72rem; white-space: nowrap; } 
 
/* ── IP Threat Card ── */ 
.ip-threat { 
    display: grid; grid-template-columns: 1fr auto; align-items: center; 
    padding: 0.6rem 0.8rem; margin: 3px 0; border-radius: 8px; 
    border-left: 3px solid; background: rgba(15,23,42,0.7); 
    transition: background 0.15s, transform 0.15s; 
} 
.ip-threat:hover { background: rgba(30,41,59,0.9); transform: translateX(3px); } 
.ip-addr { color: #e2e8f0; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 
0.82rem; } 
.ip-info { color: #64748b; font-size: 0.7rem; margin-top: 1px; } 
.threat-score { 
    font-size: 1.1rem; font-weight: 800; text-align: right; 
} 
.score-high   { color: #f87171; border-left-color: #ef4444; } 
.score-medium { color: #fbbf24; border-left-color: #f59e0b; } 
.score-low    { color: #34d399; border-left-color: #10b981; } 
 
/* ── Sidebar ── */ 
.sidebar-brand { 
    text-align: center; padding: 0.8rem 0 1rem; 
    border-bottom: 1px solid rgba(255,255,255,0.04); margin-bottom: 1rem; 
} 
.sidebar-brand h2 { 
    font-size: 1.2rem; font-weight: 800; margin: 0; 
    background: linear-gradient(135deg, #818cf8, #6366f1); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
} 
.sidebar-brand p { color: #475569; font-size: 0.72rem; margin: 0.2rem 0 0; letter-spacing: 0.04em; 
text-transform: uppercase; } 
.sidebar-stat { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 
1px solid rgba(255,255,255,0.03); } 
.sidebar-stat-label { color: #64748b; font-size: 0.78rem; } 
.sidebar-stat-value { color: #e2e8f0; font-size: 0.78rem; font-weight: 600; } 
</style> 
""" 
 
# ============================================= 
# Helpers 
# ============================================= 
def fmt_bytes(b): 
    for u in ['B','KB','MB']: 
        if b < 1024: return f"{b:.1f} {u}" 
        b /= 1024 
    return f"{b:.1f} GB" 
 
def fmt_time(s): 
    if s < 60: return f"{s:.0f}s" 
    if s < 3600: return f"{int(s//60)}m {int(s%60)}s" 
    return f"{int(s//3600)}h {int((s%3600)//60)}m" 
 
def proto_class(p): 
    return f"proto-{p.lower()}" 
 
# ============================================= 
# Plotly chart builders 
# ============================================= 
_PLOTLY_LAYOUT = dict( 
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
    font=dict(color='#94a3b8', family='Inter', size=11), 
    margin=dict(l=0, r=0, t=8, b=0), hovermode='x unified', showlegend=False, 
) 
 
def build_pps_chart(timestamps, pps_data): 
    fig = go.Figure() 
    fig.add_trace(go.Scatter( 
        x=list(timestamps), y=list(pps_data), mode='lines', 
        line=dict(color='#818cf8', width=2.5, shape='spline'), 
        fill='tozeroy', fillcolor='rgba(99,102,241,0.12)', 
        hovertemplate='<b>%{y}</b> pkt/s<extra></extra>', 
    )) 
    fig.update_layout(**_PLOTLY_LAYOUT, height=220, 
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)', tickformat='%H:%M:%S', showgrid=False), 
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)', title=None), 
    ) 
    return fig 
 
def build_protocol_chart(protocol_counts): 
    protos, vals, colors = [], [], [] 
    color_map =  {'TCP':'#34d399','UDP':'#fbbf24','HTTP':'#60a5fa','HTTPS':'#a78bfa','DNS':'#f472b6'}
    for p, c in protocol_counts.items(): 
        if c > 0: 
            protos.append(p); vals.append(c); colors.append(color_map.get(p,'#94a3b8')) 
    fig = go.Figure(data=[go.Pie( 
        labels=protos, values=vals, hole=0.55, marker_colors=colors, 
        textinfo='percent', textposition='inside', textfont=dict(size=11, color='white'), 
        hovertemplate='<b>%{label}</b><br>%{value:,} packets<br>%{percent}<extra></extra>', 
    )]) 
    fig.update_layout(**_PLOTLY_LAYOUT, height=220) 
    return fig 
 
def build_threat_gauge(malicious_pct): 
    color = '#ef4444' if malicious_pct > 15 else '#f59e0b' if malicious_pct > 5 else '#10b981' 
    fig = go.Figure(go.Indicator( 
        mode="gauge+number", value=malicious_pct, number=dict(suffix='%', font=dict(size=28, 
color='#f1f5f9')), 
        gauge=dict( 
            axis=dict(range=[0,100], tickcolor='#334155', dtick=25), 
            bar=dict(color=color, thickness=0.7), 
            bgcolor='rgba(30,41,59,0.5)', borderwidth=0, 
            steps=[ 
                dict(range=[0,5], color='rgba(16,185,129,0.08)'), 
                dict(range=[5,15], color='rgba(245,158,11,0.08)'), 
                dict(range=[15,100], color='rgba(239,68,68,0.08)'), 
            ], 
        ), 
    )) 
    fig.update_layout(**_PLOTLY_LAYOUT, height=180) 
    return fig 
 
# ============================================= 
# Render functions 
# ============================================= 
def render_sidebar(dashboard, stats): 
    with st.sidebar: 
        st.markdown(""" 
        <div class="sidebar-brand"> 
            <h2>    ThreatVision</h2> 
            <p>Network Defense Platform</p> 
        </div> 
        """, unsafe_allow_html=True) 
 
        st.markdown('<div class="section-hdr">System Status</div>', unsafe_allow_html=True) 
        model_status = "   Active" if stats['model_loaded'] else "  Simulation" 
        pairs = [ 
            ("Engine", "● Running"), ("ML Model", model_status), 
            ("Uptime", fmt_time(stats['uptime'])), ("Refresh", "2s auto"), 
        ] 
        for label, val in pairs: 
            st.markdown(f'<div class="sidebar-stat"><span class="sidebar-stat- label">{label}</span><span class="sidebar-stat-value">{val}</span></div>', unsafe_allow_html=True)
 
        st.markdown('<div class="section-hdr" style="margin-top:1rem">Quick Stats</div>', 
unsafe_allow_html=True) 
        pairs2 = [ 
            ("Packets", f"{stats['total_packets']:,}"), 
            ("Data Volume", fmt_bytes(stats['total_bytes'])), 
            ("Active Flows", str(stats['active_flows'])), 
            ("Completed Flows", str(stats['completed_flows'])), 
            ("Tracked IPs", str(len(stats['all_ip_analyses']))), 
            ("Threats Found", str(stats['threat_stats']['malicious_count'])), 
        ] 
        for label, val in pairs2: 
            st.markdown(f'<div class="sidebar-stat"><span class="sidebar-stat- label">{label}</span><span class="sidebar-stat-value">{val}</span></div>', unsafe_allow_html=True)
 
        st.markdown("---") 
        if st.button("    Reload ML Model", use_container_width=True): 
            if dashboard.threat_detector.load_model(): 
                st.success("Model reloaded!") 
            else: 
                st.error("Failed to reload model") 
 
        st.caption("ThreatVision v3.0 · Inter font · Plotly charts") 
 
 
def render_main(dashboard, stats): 
    threat_stats = stats['threat_stats'] 
 
    # ── Brand Bar ── 
    now_str = datetime.now().strftime('%H:%M:%S') 
    st.markdown(f""" 
    <div class="brand-bar"> 
        <div> 
            <div class="brand-title">    ThreatVision SOC</div> 
            <div class="brand-sub"><span class="live-dot"></span>Live Network Monitoring</div> 
        </div> 
        <div style="text-align:right"> 
            <div style="color:#64748b;font-size:0.72rem;font-weight:500">LOCAL TIME</div> 
            <div style="color:#e2e8f0;font-size:1.1rem;font-weight:700;font-family:'JetBrains  Mono',monospace">{now_str}</div>
        </div> 
    </div> 
    """, unsafe_allow_html=True) 
 
    # ── KPI Row ── 
    mal_count = threat_stats['malicious_count'] 
    mal_pct = threat_stats['malicious_percentage'] 
    risk = "CRITICAL" if mal_pct > 15 else "ELEVATED" if mal_pct > 5 else "NORMAL" 
    risk_cls = "danger" if mal_pct > 15 else "" if mal_pct > 5 else "success" 
 
    st.markdown(f""" 
    <div class="kpi-grid"> 
        <div class="kpi-card kpi-accent-indigo"> 
            <div class="kpi-label">Total Packets</div> 
            <div class="kpi-value">{stats['total_packets']:,}</div> 
            <div class="kpi-sub">{fmt_bytes(stats['total_bytes'])} transferred</div> 
        </div> 
        <div class="kpi-card kpi-accent-cyan"> 
            <div class="kpi-label">Packets / Sec</div> 
            <div class="kpi-value">{stats['current_pps']}</div> 
            <div class="kpi-sub">Avg {stats['avg_pps']:.0f} · Peak {stats['max_pps']}</div> 
        </div> 
        <div class="kpi-card kpi-accent-emerald"> 
            <div class="kpi-label">Active Flows</div> 
            <div class="kpi-value">{stats['active_flows']}</div> 
            <div class="kpi-sub">{stats['completed_flows']} completed</div> 
        </div> 
        <div class="kpi-card kpi-accent-red"> 
            <div class="kpi-label">Threats Detected</div> 
            <div class="kpi-value danger">{mal_count}</div> 
            <div class="kpi-sub">{mal_pct:.1f}% of analyzed flows</div> 
        </div> 
        <div class="kpi-card kpi-accent-amber"> 
            <div class="kpi-label">ML Predictions</div> 
            <div class="kpi-value">{threat_stats['total_predictions']}</div> 
            <div class="kpi-sub">Confidence {threat_stats['avg_confidence']:.0%}</div> 
        </div> 
        <div class="kpi-card kpi-accent-violet"> 
            <div class="kpi-label">Threat Level</div> 
            <div class="kpi-value {risk_cls}">{risk}</div> 
            <div class="kpi-sub">Uptime {fmt_time(stats['uptime'])}</div> 
        </div> 
    </div> 
    """, unsafe_allow_html=True) 
 
    # ── Row 1: PPS Chart + Protocol + Gauge ── 
    c1, c2, c3 = st.columns([5, 2.5, 2.5]) 
    with c1: 
        st.markdown('<div class="panel"><div class="panel-title">    Packets Per Second</div>', 
unsafe_allow_html=True) 
        if dashboard.pps_history and dashboard.timestamps: 
            st.plotly_chart(build_pps_chart(dashboard.timestamps, dashboard.pps_history), 
use_container_width=True, config={'displayModeBar': False}) 
        else: 
            st.info("Collecting data…") 
        st.markdown('</div>', unsafe_allow_html=True) 
    with c2: 
        st.markdown('<div class="panel"><div class="panel-title">      Protocol Mix</div>', 
unsafe_allow_html=True) 
        if any(v > 0 for v in stats['protocol_counts'].values()): 
            st.plotly_chart(build_protocol_chart(stats['protocol_counts']), 
use_container_width=True, config={'displayModeBar': False}) 
        else: 
            st.info("Waiting…") 
        st.markdown('</div>', unsafe_allow_html=True) 
    with c3: 
        st.markdown('<div class="panel"><div class="panel-title">       Threat Rate</div>', 
unsafe_allow_html=True) 
        st.plotly_chart(build_threat_gauge(mal_pct), use_container_width=True, 
config={'displayModeBar': False}) 
        st.markdown('</div>', unsafe_allow_html=True) 
 
    # ── Row 2: Alerts + Packets + Top IPs ── 
    c1, c2, c3 = st.columns([3, 4, 3]) 
    with c1: 
        st.markdown('<div class="panel"><div class="panel-title">       Recent Alerts</div>', 
unsafe_allow_html=True) 
        alerts = stats.get('recent_alerts', []) 
        if alerts: 
            for a in alerts[:6]: 
                ts = a['timestamp'].strftime('%H:%M:%S') 
                pred = a.get('prediction', 'MALICIOUS') 
                conf = a['confidence'] 
                if pred == 'HIGH_PPS': 
                    badge_style = 'background:linear-gradient(135deg,#f59e0b,#d97706)' 
                    badge_text = '  PPS' 
                    pps_val = a.get('features', {}).get('packets_per_sec', 0) 
                    alert_text = f"High traffic spike: {int(pps_val)} pkt/s" 
                else: 
                    badge_style = '' 
                    badge_text = 'threat' 
                    src = f"{a['flow_key'].src_ip}" 
                    dst = f"{a['flow_key'].dst_ip}" 
                    alert_text = f"{src} → {dst}" 
                st.markdown(f""" 
                <div class="alert-row"> 
                    <span class="alert-badge" style="{badge_style}">{badge_text}</span> 
                    <span class="alert-text">{alert_text}</span> 
                    <span class="alert-conf">{ts} · {conf:.0%}</span> 
                </div>""", unsafe_allow_html=True) 
        else: 
            st.markdown('<div style="color:#475569;font-size:0.82rem;padding:1rem;text- align:center">No alerts yet — monitoring…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) 
 
    with c2: 
        st.markdown('<div class="panel"><div class="panel-title">       Live Packet Feed</div>', 
unsafe_allow_html=True) 
        if dashboard.recent_packets: 
            for pkt in list(dashboard.recent_packets)[-8:][::-1]: 
                ts = pkt['timestamp'].strftime('%H:%M:%S') 
                proto = pkt['protocol'] 
                src = f"{pkt['src_ip']}:{pkt['src_port']}" 
                dst = f"{pkt['dst_ip']}:{pkt['dst_port']}" 
                ln = pkt['length'] 
                pc = proto_class(proto) 
                warn = ' <span class=\"alert-badge\" style=\"font-size:0.6rem\">⚠</span>' if pkt.get('is_malicious_pattern') else '' 
                st.markdown(f""" 
                <div class="pkt {pc}"> 
                    <span class="pkt-time">{ts}</span> 
                    <span class="pkt-flow">{src} → {dst}{warn}</span> 
                    <span class="pkt-meta"><span class="pkt-proto">{proto}</span><span class="pkt- bytes">{ln:,}B</span></span>
                </div>""", unsafe_allow_html=True) 
        else: 
            st.info("Capturing…") 
        st.markdown('</div>', unsafe_allow_html=True) 
 
    with c3: 
        st.markdown('<div class="panel"><div class="panel-title">       Top IPs by Threat Score</div>', unsafe_allow_html=True) 
        ip_analyses = stats.get('all_ip_analyses', []) 
        shown = 0 
        for ipa in ip_analyses: 
            if shown >= 7: 
                break 
            score = ipa['threat_score'] 
            if score <= 0 and ipa['total_predictions'] == 0: 
                continue 
            shown += 1 
            sc = "score-high" if score > 70 else "score-medium" if score > 30 else "score-low" 
            ip_type = "Internal" if ipa['ip'].startswith('192.168.') else "External" 
            st.markdown(f""" 
            <div class="ip-threat {sc}"> 
                <div> 
                    <div class="ip-addr">{ipa['ip']}</div> 
                    <div class="ip-info">{ip_type} · {ipa['packet_count']:,} pkts · 
{ipa['status']}</div> 
                </div> 
                <div class="threat-score">{score:.0f}</div> 
            </div>""", unsafe_allow_html=True) 
        if shown == 0: 
            st.markdown('<div style="color:#475569;font-size:0.82rem;padding:1rem;text- align:center">Building IP profiles…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) 
 
    # ── Row 3: Top Source IPs bar + PPS Stats ── 
    c1, c2 = st.columns([6, 4]) 
    with c1: 
        st.markdown('<div class="panel"><div class="panel-title">  Top Source IPs by Volume</div>', unsafe_allow_html=True) 
        if stats['top_source_ips']: 
            ips = [ip for ip, _ in stats['top_source_ips']] 
            counts = [c for _, c in stats['top_source_ips']] 
            colors_bar = ['#6366f1' if ip.startswith('192.168.') else '#f59e0b' for ip in ips] 
            fig = go.Figure(go.Bar(x=counts, y=ips, orientation='h', marker_color=colors_bar, 
                hovertemplate='<b>%{y}</b><br>%{x:,} packets<extra></extra>', 
                text=counts, textposition='auto', textfont=dict(color='white', size=11))) 
            fig.update_layout(**_PLOTLY_LAYOUT, height=180, 
                xaxis=dict(showgrid=False, showticklabels=False), 
                yaxis=dict(autorange='reversed', tickfont=dict(family='JetBrains Mono', size=11))) 
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}) 
        st.markdown('</div>', unsafe_allow_html=True) 
 
    with c2: 
        st.markdown('<div class="panel"><div class="panel-title">           PPS Statistics</div>', 
unsafe_allow_html=True) 
        pps_stats = [ 
            ("Current", str(stats['current_pps']), "#818cf8"), 
            ("Average", f"{stats['avg_pps']:.0f}", "#34d399"), 
            ("Peak", str(stats['max_pps']), "#f87171"), 
            ("Minimum", str(stats['min_pps']), "#fbbf24"), 
            ("Median", f"{stats['median_pps']:.0f}", "#a78bfa"), 
            ("Std Dev", f"{stats['std_dev_pps']:.1f}", "#22d3ee"), 
        ] 
        for label, val, color in pps_stats: 
            st.markdown(f""" 
            <div class="sidebar-stat"> 
                <span class="sidebar-stat-label">{label}</span> 
                <span style="color:{color};font-size:0.85rem;font-weight:700">{val}</span> 
            </div>""", unsafe_allow_html=True) 
        st.markdown('</div>', unsafe_allow_html=True) 
 
  

# threatvision_dashboard.py 
 
import time 
import random 
import threading 
import joblib 
import numpy as np 
import pandas as pd 
from datetime import datetime, timedelta 
from collections import deque, Counter, defaultdict 
from dataclasses import dataclass 
from typing import Dict, List, Tuple, Optional 
import plotly.graph_objects as go 
import plotly.express as px 
import warnings 
warnings.filterwarnings('ignore') 
 
# ============================================= 
# Flow Extraction Module (Embedded) 
# ============================================= 
 
@dataclass 
class FlowKey: 
    """Unique identifier for a network flow (5-tuple)""" 
    src_ip: str 
    dst_ip: str 
    src_port: int 
    dst_port: int 
    protocol: str 
     
    def __hash__(self): 
        return hash((self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol)) 
     
    def __eq__(self, other): 
        return (self.src_ip == other.src_ip and 
                self.dst_ip == other.dst_ip and 
                self.src_port == other.src_port and 
                self.dst_port == other.dst_port and 
                self.protocol == other.protocol) 
 
class FlowStats: 
    """Track statistics for a single flow""" 
    def __init__(self): 
        self.packets = [] 
        self.start_time = None 
        self.end_time = None 
        self.fwd_packets = [] 
        self.bwd_packets = [] 
        self.fwd_lengths = [] 
        self.bwd_lengths = [] 
        self.fwd_timestamps = [] 
        self.bwd_timestamps = [] 
     
    def add_packet(self, packet: dict, is_forward: bool): 
        """Add a packet to the flow statistics""" 
        timestamp = packet['timestamp'] 
         
        if self.start_time is None: 
            self.start_time = timestamp 
         
        self.end_time = timestamp 
        self.packets.append(packet) 
         
        if is_forward: 
            self.fwd_packets.append(packet) 
            self.fwd_lengths.append(packet['length']) 
            self.fwd_timestamps.append(timestamp) 
        else: 
            self.bwd_packets.append(packet) 
            self.bwd_lengths.append(packet['length']) 
            self.bwd_timestamps.append(timestamp) 
     
    def is_complete(self, current_time: datetime, timeout_seconds: float = 60.0) -> bool: 
        """Check if flow is complete (timed out)""" 
        if self.end_time is None: 
            return False 
        return (current_time - self.end_time).total_seconds() > timeout_seconds 
     
    def extract_features(self) -> Dict[str, float]: 
        """Extract flow features for ML model""" 
        if not self.packets: 
            return {} 
         
        # Calculate basic statistics 
        flow_duration = (self.end_time - self.start_time).total_seconds() 
         
        total_fwd_packets = len(self.fwd_packets) 
        total_bwd_packets = len(self.bwd_packets) 
         
        total_fwd_length = sum(self.fwd_lengths) if self.fwd_lengths else 0 
        total_bwd_length = sum(self.bwd_lengths) if self.bwd_lengths else 0 
         
        # Calculate packet length statistics 
        def calculate_stats(values): 
            if not values: 
                return 0, 0, 0, 0 
            values_arr = np.array(values) 
            return ( 
                float(values_arr.max()), 
                float(values_arr.min()), 
                float(values_arr.mean()), 
                float(values_arr.std() if len(values) > 1 else 0) 
            ) 
         
        fwd_max, fwd_min, fwd_mean, fwd_std = calculate_stats(self.fwd_lengths) 
        bwd_max, bwd_min, bwd_mean, bwd_std = calculate_stats(self.bwd_lengths) 
         
        # Calculate IAT (Inter-Arrival Time) statistics 
        all_timestamps = sorted(self.fwd_timestamps + self.bwd_timestamps) 
        iats = [] 
        for i in range(1, len(all_timestamps)): 
            iat = (all_timestamps[i] - all_timestamps[i-1]).total_seconds() 
            iats.append(iat) 
         
        iat_mean = float(np.mean(iats)) if iats else 0 
        iat_std = float(np.std(iats)) if len(iats) > 1 else 0 
        iat_max = float(max(iats)) if iats else 0 
        iat_min = float(min(iats)) if iats else 0 
         
        # Calculate rates 
        flow_bytes_s = (total_fwd_length + total_bwd_length) / flow_duration if flow_duration > 0  else 0
        flow_packets_s = (total_fwd_packets + total_bwd_packets) / flow_duration if flow_duration  > 0 else 0
         
        # Calculate packet length variance 
        all_lengths = self.fwd_lengths + self.bwd_lengths 
        packet_length_variance = float(np.var(all_lengths)) if all_lengths else 0 
         
        # Calculate engineered features 
        fwd_bwd_packet_ratio = total_fwd_packets / (total_bwd_packets + 1) 
        fwd_bwd_bytes_ratio = total_fwd_length / (total_bwd_length + 1) 
         
        return { 
            'Flow_Duration': flow_duration, 
            'Total_Fwd_Packets': total_fwd_packets, 
            'Total_Backward_Packets': total_bwd_packets, 
            'Total_Length_of_Fwd_Packets': total_fwd_length, 
            'Total_Length_of_Bwd_Packets': total_bwd_length, 
            'Fwd_Packet_Length_Max': fwd_max, 
            'Fwd_Packet_Length_Min': fwd_min, 
            'Fwd_Packet_Length_Mean': fwd_mean, 
            'Fwd_Packet_Length_Std': fwd_std, 
            'Bwd_Packet_Length_Max': bwd_max, 
            'Bwd_Packet_Length_Min': bwd_min, 
            'Bwd_Packet_Length_Mean': bwd_mean, 
            'Bwd_Packet_Length_Std': bwd_std, 
            'Flow_Bytes_s': flow_bytes_s, 
            'Flow_Packets_s': flow_packets_s, 
            'Flow_IAT_Mean': iat_mean, 
            'Flow_IAT_Std': iat_std, 
            'Flow_IAT_Max': iat_max, 
            'Flow_IAT_Min': iat_min, 
            'Packet_Length_Variance': packet_length_variance, 
            'Fwd_Bwd_Packet_Ratio': fwd_bwd_packet_ratio, 
            'Fwd_Bwd_Bytes_Ratio': fwd_bwd_bytes_ratio 
        } 
 
class FlowExtractor: 
    """Extract flows from packet stream and generate features""" 
    def __init__(self, flow_timeout: float = 8.0): 
        self.flow_timeout = flow_timeout 
        self.active_flows: Dict[FlowKey, FlowStats] = {} 
        self.completed_flows = [] 
        self.last_cleanup = datetime.now() 
     
    def process_packet(self, packet: dict) -> Optional[Dict[str, float]]: 
        """Process a packet and return flow features if flow is complete""" 
        # Determine flow direction (normalize: smaller IP first) 
        src_ip = packet['src_ip'] 
        dst_ip = packet['dst_ip'] 
         
        if src_ip < dst_ip: 
            flow_key = FlowKey(src_ip, dst_ip, packet['src_port'], packet['dst_port'],  packet['protocol'])
            is_forward = True 
        else: 
            flow_key = FlowKey(dst_ip, src_ip, packet['dst_port'], packet['src_port'],  packet['protocol'])
            is_forward = False 
         
        # Get or create flow stats 
        if flow_key not in self.active_flows: 
            self.active_flows[flow_key] = FlowStats() 
         
        flow_stats = self.active_flows[flow_key] 
        flow_stats.add_packet(packet, is_forward) 
         
        # Check if flow is complete 
        current_time = datetime.now() 
        if flow_stats.is_complete(current_time, self.flow_timeout): 
            # Extract features 
            features = flow_stats.extract_features() 
             
            # Store completed flow 
            self.completed_flows.append({ 
                'flow_key': flow_key, 
                'features': features, 
                'start_time': flow_stats.start_time, 
                'end_time': flow_stats.end_time, 
                'total_packets': len(flow_stats.packets), 
                'total_bytes': sum(p['length'] for p in flow_stats.packets) 
            }) 
             
            # Remove from active flows 
            del self.active_flows[flow_key] 
             
            return [{'flow_key': flow_key, 'features': features}] 
         
        # Cleanup old flows periodically (every 4 seconds) 
        if (current_time - self.last_cleanup).total_seconds() > 4: 
            completed = self._cleanup_old_flows(current_time) 
            self.last_cleanup = current_time 
            if completed: 
                return completed 
         
        return None 
     
    def _cleanup_old_flows(self, current_time: datetime): 
        """Remove timed-out flows and return list of {flow_key, features} dicts""" 
        expired_keys = [] 
        for flow_key, flow_stats in self.active_flows.items(): 
            if flow_stats.is_complete(current_time, self.flow_timeout): 
                expired_keys.append(flow_key) 
         
        completed = [] 
        for key in expired_keys: 
            features = self.active_flows[key].extract_features() 
            self.completed_flows.append({ 
                'flow_key': key, 
                'features': features, 
                'start_time': self.active_flows[key].start_time, 
                'end_time': self.active_flows[key].end_time, 
                'total_packets': len(self.active_flows[key].packets), 
                'total_bytes': sum(p['length'] for p in self.active_flows[key].packets) 
            }) 
            completed.append({'flow_key': key, 'features': features}) 
            del self.active_flows[key] 
         
        return completed 
     
    def get_active_flow_count(self) -> int: 
        """Get number of active flows""" 
        return len(self.active_flows) 
     
    def get_completed_flow_count(self) -> int: 
        """Get number of completed flows""" 
        return len(self.completed_flows) 
     
    def get_recent_flows(self, count: int = 10) -> List[dict]: 
        """Get most recent completed flows""" 
        return self.completed_flows[-count:] if self.completed_flows else [] 
     
    def get_flows_by_ip(self, ip_address: str) -> List[dict]: 
        """Get all flows involving a specific IP address""" 
        ip_flows = [] 
        for flow in self.completed_flows: 
            if flow['flow_key'].src_ip == ip_address or flow['flow_key'].dst_ip == ip_address: 
                ip_flows.append(flow) 
        return ip_flows 
 
# ============================================= 
# IP Threat Tracker (NEW - Links both dashboards) 
# ============================================= 
 
class IPThreatTracker: 
    """Track threat scores and ML predictions per IP address""" 
    def __init__(self): 
        self.ip_threat_scores = defaultdict(float)  # IP -> threat score (0-100) 
        self.ip_predictions = defaultdict(list)     # IP -> list of predictions 
        self.ip_flow_counts = Counter()             # IP -> flow count 
        self.ip_packet_counts = Counter()           # IP -> packet count 
        self.suspicious_ips = set()                 # IPs flagged as suspicious 
        self.malicious_ips = set()                  # IPs confirmed malicious by ML 
        self.benign_ips = set()                     # IPs confirmed benign by ML 
     
    def update_ip_stats(self, packet: dict): 
        """Update IP statistics from a packet""" 
        src_ip = packet['src_ip'] 
        dst_ip = packet['dst_ip'] 
         
        self.ip_packet_counts[src_ip] += 1 
        self.ip_packet_counts[dst_ip] += 1 
         
        # Basic heuristic: high packet rate = suspicious 
        if self.ip_packet_counts[src_ip] > 100:  # Threshold 
            self.suspicious_ips.add(src_ip) 
            self.ip_threat_scores[src_ip] = min(100, self.ip_threat_scores[src_ip] + 5) 
     
    def record_ml_prediction(self, ip_address: str, prediction: str, confidence: float, 
flow_features: dict): 
        """Record ML prediction for an IP""" 
        pred_record = { 
            'timestamp': datetime.now(), 
            'prediction': prediction, 
            'confidence': confidence, 
            'features': flow_features 
        } 
         
        self.ip_predictions[ip_address].append(pred_record) 
         
        # Keep only last 20 predictions per IP 
        if len(self.ip_predictions[ip_address]) > 20: 
            self.ip_predictions[ip_address] = self.ip_predictions[ip_address][-20:] 
         
        # Update IP sets 
        if prediction == "MALICIOUS" and confidence > 0.7: 
            self.malicious_ips.add(ip_address) 
            self.ip_threat_scores[ip_address] = 100  # Max threat score 
            if ip_address in self.benign_ips: 
                self.benign_ips.remove(ip_address) 
        elif prediction == "BENIGN" and confidence > 0.8: 
            self.benign_ips.add(ip_address) 
            self.ip_threat_scores[ip_address] = max(0, self.ip_threat_scores[ip_address] - 20) 
            if ip_address in self.malicious_ips: 
                self.malicious_ips.remove(ip_address) 
         
        # Increment flow count 
        self.ip_flow_counts[ip_address] += 1 
     
    def get_ip_analysis(self, ip_address: str) -> Dict[str, any]: 
        """Get comprehensive analysis for an IP""" 
        predictions = self.ip_predictions.get(ip_address, []) 
         
        if not predictions: 
            return { 
                'ip': ip_address, 
                'threat_score': self.ip_threat_scores.get(ip_address, 0), 
                'total_predictions': 0, 
                'malicious_predictions': 0, 
                'benign_predictions': 0, 
                'avg_confidence': 0, 
                'status': 'UNKNOWN', 
                'packet_count': self.ip_packet_counts.get(ip_address, 0), 
                'flow_count': self.ip_flow_counts.get(ip_address, 0), 
                'is_suspicious': ip_address in self.suspicious_ips, 
                'is_malicious': ip_address in self.malicious_ips, 
                'is_benign': ip_address in self.benign_ips 
            } 
         
        # Calculate statistics 
        total = len(predictions) 
        malicious = sum(1 for p in predictions if p['prediction'] == "MALICIOUS") 
        benign = total - malicious 
        avg_confidence = sum(p['confidence'] for p in predictions) / total if total > 0 else 0 
         
        # Determine status 
        if ip_address in self.malicious_ips: 
            status = "MALICIOUS" 
        elif ip_address in self.benign_ips: 
            status = "BENIGN" 
        elif malicious > benign: 
            status = "SUSPICIOUS" 
        else: 
            status = "NORMAL" 
         
        return { 
            'ip': ip_address, 
            'threat_score': self.ip_threat_scores.get(ip_address, 0), 
            'total_predictions': total, 
            'malicious_predictions': malicious, 
            'benign_predictions': benign, 
            'avg_confidence': avg_confidence, 
            'status': status, 
            'packet_count': self.ip_packet_counts.get(ip_address, 0), 
            'flow_count': self.ip_flow_counts.get(ip_address, 0), 
            'is_suspicious': ip_address in self.suspicious_ips, 
            'is_malicious': ip_address in self.malicious_ips, 
            'is_benign': ip_address in self.benign_ips, 
            'recent_predictions': predictions[-5:]  # Last 5 predictions 
        } 
     
    def get_top_suspicious_ips(self, count: int = 10) -> List[Dict[str, any]]: 
        """Get top suspicious IPs with analysis""" 
        suspicious_ips = [] 
        for ip in list(self.suspicious_ips) + list(self.malicious_ips): 
            analysis = self.get_ip_analysis(ip) 
            if analysis['total_predictions'] > 0:  # Only include IPs with ML predictions 
                suspicious_ips.append(analysis) 
         
        # Sort by threat score (descending) 
        suspicious_ips.sort(key=lambda x: x['threat_score'], reverse=True) 
        return suspicious_ips[:count] 
     
    def get_all_ip_analyses(self) -> List[Dict[str, any]]: 
        """Get analysis for all tracked IPs""" 
        all_ips = set(list(self.ip_predictions.keys()) +  
                     list(self.suspicious_ips) +  
                     list(self.malicious_ips) +  
                     list(self.benign_ips)) 
         
        analyses = [] 
        for ip in all_ips: 
            analyses.append(self.get_ip_analysis(ip)) 
         
        # Sort by threat score (descending) 
        analyses.sort(key=lambda x: x['threat_score'], reverse=True) 
        return analyses 
 
# ============================================= 
# ML Model Utilities (Embedded) 
# ============================================= 
 
def temperature_scale(probs, T=1.5): 
    """Apply temperature scaling to probabilities.""" 
    logits = np.log(np.clip(probs, 1e-12, 1 - 1e-12)) 
    scaled_logits = logits / T 
    return 1 / (1 + np.exp(-scaled_logits)) 
 
class TempScaledModel: 
    """Wraps a scikit-learn or XGBoost classifier with temperature scaling.""" 
    def __init__(self, base_model, T=1.5): 
        self.base_model = base_model 
        self.T = T 
     
    def predict_proba(self, X): 
        base_probs = self.base_model.predict_proba(X) 
        scaled_probs = np.zeros_like(base_probs) 
        for i in range(base_probs.shape[1]): 
            scaled_probs[:, i] = temperature_scale(base_probs[:, i], self.T) 
        scaled_probs /= scaled_probs.sum(axis=1, keepdims=True) 
        return scaled_probs 
     
    def predict(self, X): 
        return np.argmax(self.predict_proba(X), axis=1) 
 
class ThreatDetector: 
    """Real-time threat detection using trained ML model""" 
     
    def __init__(self, model_path: str = "threatvision_realistic_temp.pkl", 
                 encoder_path: str = "label_encoder.pkl"): 
        self.model_path = model_path 
        self.encoder_path = encoder_path 
        self.model = None 
        self.encoder = None 
        self.threshold = 0.7 
        self.predictions_history = [] 
        self.last_load_attempt = None 
         
        # Define feature columns (must match training) 
        self.basic_features = [ 
            "Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets", 
            "Total_Length_of_Fwd_Packets", "Total_Length_of_Bwd_Packets", 
            "Fwd_Packet_Length_Max", "Fwd_Packet_Length_Min", 
            "Fwd_Packet_Length_Mean", "Fwd_Packet_Length_Std", 
            "Bwd_Packet_Length_Max", "Bwd_Packet_Length_Min", 
            "Bwd_Packet_Length_Mean", "Bwd_Packet_Length_Std", 
            "Flow_Bytes_s", "Flow_Packets_s", 
            "Flow_IAT_Mean", "Flow_IAT_Std", "Flow_IAT_Max", "Flow_IAT_Min", 
            "Packet_Length_Variance" 
        ] 
         
        self.extra_features = ["Fwd_Bwd_Packet_Ratio", "Fwd_Bwd_Bytes_Ratio"] 
        self.feature_columns = self.basic_features + self.extra_features 
         
        # Try to load model 
        self.load_model() 
     
    def load_model(self) -> bool: 
        """Load trained model and encoder""" 
        try: 
            self.model = joblib.load(self.model_path) 
            self.encoder = joblib.load(self.encoder_path) 
            self.last_load_attempt = datetime.now() 
            print(f"[OK] ThreatVision model loaded successfully from {self.model_path}") 
            return True 
        except Exception as e: 
            print(f"[ERROR] Failed to load model: {e}") 
            print("Hint: Running in simulation mode. Train model with: python train_model.py") 
            self.model = None 
            self.encoder = None 
            return False 
     
    def is_model_loaded(self) -> bool: 
        """Check if model is loaded""" 
        return self.model is not None and self.encoder is not None 
     
    def predict_flow(self, flow_features: Dict[str, float]) -> Tuple[str, float, Dict[str,  float]]:
        """Predict threat for a single flow""" 
        if not self.is_model_loaded(): 
            # Simulation mode: 10% chance of malicious for demo 
            if random.random() < 0.1: 
                return "MALICIOUS", 0.85, {"BENIGN": 0.15, "MALICIOUS": 0.85} 
            else: 
                return "BENIGN", 0.15, {"BENIGN": 0.85, "MALICIOUS": 0.15} 
         
        try: 
            # Convert features to DataFrame 
            features_df = pd.DataFrame([flow_features]) 
             
            # Ensure all required columns are present 
            for col in self.feature_columns: 
                if col not in features_df.columns: 
                    features_df[col] = 0.0 
             
            # Reorder columns 
            features_df = features_df[self.feature_columns] 
             
            # Clean data 
            features_df.replace([np.inf, -np.inf], np.nan, inplace=True) 
            features_df.fillna(0, inplace=True) 
             
            # Get prediction 
            X = features_df.values 
            pred = self.model.predict(X)[0] 
            probabilities = self.model.predict_proba(X)[0] 
             
            # Get class names 
            if self.encoder and hasattr(self.encoder, 'classes_'): 
                class_names = list(self.encoder.classes_) 
            else: 
                class_names = ["BENIGN", "MALICIOUS"] 
             
            if len(class_names) == 2: 
                predicted_class = class_names[pred] 
                confidence = float(probabilities[pred]) 
                 
                # Create confidence breakdown 
                confidence_dict = { 
                    "BENIGN": float(probabilities[0]), 
                    "MALICIOUS": float(probabilities[1]) if len(probabilities) > 1 else 0.0 
                } 
                 
                return predicted_class, confidence, confidence_dict 
            else: 
                # Multi-class scenario 
                predicted_class = class_names[pred] 
                confidence = float(probabilities[pred]) 
                confidence_dict = {class_names[i]: float(prob) for i, prob in  enumerate(probabilities)}
                return predicted_class, confidence, confidence_dict 
         
        except Exception as e: 
            print(f"[ERROR] Prediction error: {e}") 
            return "ERROR", 0.0, {} 
     
    def record_prediction(self, flow_key: dict, features: dict,  
                         prediction: str, confidence: float,  
                         confidence_dict: dict, timestamp: datetime): 
        """Record a prediction for history""" 
        prediction_record = { 
            'timestamp': timestamp, 
            'flow_key': flow_key, 
            'prediction': prediction, 
            'confidence': confidence, 
            'confidence_breakdown': confidence_dict, 
            'features': features, 
            'is_malicious': prediction == "MALICIOUS" and confidence > self.threshold 
        } 
         
        self.predictions_history.append(prediction_record) 
         
        # Keep only last 1000 predictions 
        if len(self.predictions_history) > 1000: 
            self.predictions_history = self.predictions_history[-1000:] 
         
        return prediction_record 
     
    def get_statistics(self) -> Dict[str, any]: 
        """Get threat detection statistics""" 
        if not self.predictions_history: 
            return { 
                'total_predictions': 0, 
                'malicious_count': 0, 
                'benign_count': 0, 
                'malicious_percentage': 0.0, 
                'avg_confidence': 0.0, 
                'recent_malicious': [] 
            } 
         
        total = len(self.predictions_history) 
        malicious = sum(1 for p in self.predictions_history if p['is_malicious']) 
        benign = total - malicious 
         
        if total > 0: 
            avg_confidence = sum(p['confidence'] for p in self.predictions_history) / total 
        else: 
            avg_confidence = 0.0 
         
        recent_malicious = [ 
            p for p in self.predictions_history[-20:]  
            if p['is_malicious'] 
        ][-5:] 
         
        return { 
            'total_predictions': total, 
            'malicious_count': malicious, 
            'benign_count': benign, 
            'malicious_percentage': (malicious / total * 100) if total > 0 else 0.0, 
            'avg_confidence': avg_confidence, 
            'recent_malicious': recent_malicious 
        } 
 
# ============================================= 
# Dashboard Main Class (Updated with IP Threat Tracker) 
# ============================================= 
 
class EnhancedPacketCaptureDashboard: 
    def __init__(self): 
        self.is_running = True 
        self.packet_count = 0 
        self.start_time = time.time() 
        self.pps_history = deque(maxlen=30) 
        self.timestamps = deque(maxlen=30) 
        self.recent_packets = deque(maxlen=50) 
        self.protocol_counts = {'TCP': 0, 'UDP': 0, 'HTTP': 0, 'HTTPS': 0, 'DNS': 0} 
        self.source_ip_counts = Counter() 
        self.total_bytes = 0 
        self.current_pps = 0 
        self.max_pps = 0 
        self.min_pps = float('inf') 
        self.pps_data = deque(maxlen=100) 
         
        # ML Integration Components 
        self.flow_extractor = FlowExtractor(flow_timeout=8.0) 
        self.threat_detector = ThreatDetector() 
        self.ip_tracker = IPThreatTracker()  # NEW: IP threat tracker 
        self.threat_alerts = deque(maxlen=20) 
        self.prediction_history = deque(maxlen=100) 
         
        # Start capture thread 
        self.capture_thread = threading.Thread(target=self._capture_loop) 
        self.capture_thread.daemon = True 
        self.capture_thread.start() 
         
        print("=" * 60) 
        print("ENHANCED THREAT DETECTION DASHBOARD") 
        print("=" * 60) 
        print("Packet Capture: ACTIVE") 
        print("Threat Detection: " + ("ACTIVE" if self.threat_detector.is_model_loaded() else  "SIMULATION MODE"))
        print("IP Threat Tracking: ACTIVE") 
        print("\nDashboard is now running in your browser!") 
        print("Check terminal for detailed packet output\n") 
     
    def _capture_loop(self): 
        """Main packet capture loop with threat detection""" 
        last_update = time.time() 
        packets_in_interval = 0 
         
        while self.is_running: 
            # Simulate a packet 
            packet = self._simulate_packet() 
             
            self.packet_count += 1 
            packets_in_interval += 1 
            self.total_bytes += packet['length'] 
             
            # Store packet for display 
            self.recent_packets.append(packet) 
             
            # Update protocol counts 
            proto = packet['protocol'] 
            if proto in self.protocol_counts: 
                self.protocol_counts[proto] += 1 
             
            # Update source IP counts 
            self.source_ip_counts[packet['src_ip']] += 1 
             
            # Update IP threat tracker 
            self.ip_tracker.update_ip_stats(packet) 
             
            # Print to terminal 
            self._print_to_terminal(packet) 
             
            # Process packet through flow extractor 
            completed_flows = self.flow_extractor.process_packet(packet) 
             
            # Analyze ALL completed flows through ML 
            if completed_flows: 
                for flow_data in completed_flows: 
                    fk = flow_data['flow_key'] 
                    feats = flow_data['features'] 
                     
                    # Predict threat 
                    prediction, confidence, conf_dict = self.threat_detector.predict_flow(feats) 
                     
                    # Record prediction 
                    pred_record = self.threat_detector.record_prediction( 
                        fk, feats, prediction, confidence, conf_dict, datetime.now() 
                    ) 
                    self.prediction_history.append(pred_record) 
                     
                    # Record ML prediction for both IPs in the flow 
                    self.ip_tracker.record_ml_prediction(fk.src_ip, prediction, confidence, feats) 
                    self.ip_tracker.record_ml_prediction(fk.dst_ip, prediction, confidence, feats) 
                     
                    # If malicious with high confidence, create alert 
                    if prediction == "MALICIOUS" and confidence > 0.7: 
                        alert = { 
                            'timestamp': datetime.now(), 
                            'flow_key': fk, 
                            'prediction': prediction, 
                            'confidence': confidence, 
                            'features': feats, 
                            'src_ip': fk.src_ip, 
                            'dst_ip': fk.dst_ip, 
                            'protocol': fk.protocol 
                        } 
                        self.threat_alerts.append(alert) 
                        self._print_threat_alert(alert) 
             
            # Update PPS every second 
            current_time = time.time() 
            if current_time - last_update >= 1.0: 
                self.current_pps = packets_in_interval 
                self.pps_history.append(packets_in_interval) 
                self.pps_data.append(packets_in_interval) 
                self.timestamps.append(datetime.now()) 
                 
                # Update min/max PPS 
                if packets_in_interval > self.max_pps: 
                    self.max_pps = packets_in_interval 
                if packets_in_interval < self.min_pps: 
                    self.min_pps = packets_in_interval 
                 
                # HIGH PPS ALERT: flag when packet rate is unusually high 
                if packets_in_interval > 95: 
                    pps_alert = { 
                        'timestamp': datetime.now(), 
                        'flow_key': FlowKey('SYSTEM', 'MONITOR', 0, 0, 'PPS'), 
                        'prediction': 'HIGH_PPS', 
                        'confidence': min(packets_in_interval / 200.0, 1.0), 
                        'features': {'packets_per_sec': packets_in_interval}, 
                        'src_ip': 'SYSTEM', 
                        'dst_ip': 'MONITOR', 
                        'protocol': 'PPS_SPIKE' 
                    } 
                    self.threat_alerts.append(pps_alert) 
                    print(f"\n\033[93m[!] HIGH PPS ALERT: {packets_in_interval}  packets/sec\033[0m")
                 
                packets_in_interval = 0 
                last_update = current_time 
             
            # Small delay to control speed 
            time.sleep(0.01)  # ~100 packets/sec 
     
    def _simulate_packet(self): 
        """Simulate a network packet with occasional malicious patterns""" 
        protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'DNS'] 
        protocol_weights = [40, 25, 15, 15, 5] 
         
        # Realistic IP ranges 
        local_ips = [f"192.168.1.{i}" for i in range(1, 255)] 
        external_ips = [ 
            "8.8.8.8", "8.8.4.4",  # Google DNS 
            "1.1.1.1", "1.0.0.1",  # Cloudflare 
            "142.250.70.46",  # Google 
            "104.16.249.249",  # Cloudflare 
            "20.205.243.166",  # GitHub 
            "13.107.42.14",  # Microsoft 
            "52.114.128.66",  # Microsoft Teams 
            "54.239.28.85",  # Amazon 
            "185.159.82.48",  # Suspicious IP (for demo) 
            "45.129.33.21",   # Suspicious IP (for demo) 
        ] 
         
        # Random protocol based on weights 
        proto = random.choices(protocols, weights=protocol_weights, k=1)[0] 
         
        # Occasionally simulate malicious patterns (5% chance) 
        is_malicious_pattern = random.random() < 0.05 
         
        if is_malicious_pattern: 
            # Malicious pattern: very short duration, many small packets 
            dst_port = random.choice([4444, 31337, 6667, 23])  # Common malicious ports 
            length = random.randint(20, 100)  # Small packets 
            src_ip = random.choice(["185.159.82.48", "45.129.33.21", "192.168.1.100"]) 
            dst_ip = random.choice(local_ips if src_ip.startswith("192.168.1.") else external_ips) 
        else: 
            # Normal traffic 
            if proto == 'HTTP': 
                dst_port = 80 
                length = random.randint(500, 1500) 
            elif proto == 'HTTPS': 
                dst_port = 443 
                length = random.randint(800, 1600) 
            elif proto == 'DNS': 
                dst_port = 53 
                length = random.randint(60, 512) 
            elif proto == 'TCP': 
                dst_port = random.choice([22, 25, 80, 443, 3389, 8080]) 
                length = random.randint(40, 1500) 
            else:  # UDP 
                dst_port = random.choice([53, 67, 68, 123, 161, 162, 443]) 
                length = random.randint(28, 1472) 
             
            # Direction: 70% outgoing, 30% incoming 
            if random.random() < 0.7: 
                src_ip = random.choice(local_ips) 
                dst_ip = random.choice(external_ips) 
            else: 
                src_ip = random.choice(external_ips) 
                dst_ip = random.choice(local_ips) 
         
        # Source port (ephemeral) 
        src_port = random.randint(49152, 65535) 
         
        return { 
            'timestamp': datetime.now(), 
            'src_ip': src_ip, 
            'dst_ip': dst_ip, 
            'src_port': src_port, 
            'dst_port': dst_port, 
            'protocol': proto, 
            'length': length, 
            'is_malicious_pattern': is_malicious_pattern 
        } 
     
    def _print_to_terminal(self, packet): 
        """Print packet info to terminal with colors""" 
        timestamp = packet['timestamp'].strftime('%H:%M:%S.%f')[:-3] 
        src = f"{packet['src_ip']}:{packet['src_port']}" 
        dst = f"{packet['dst_ip']}:{packet['dst_port']}" 
        proto = packet['protocol'] 
        length = packet['length'] 
         
        # Color coding 
        if proto == 'TCP': 
            color = '\033[92m'  # Green 
        elif proto == 'UDP': 
            color = '\033[93m'  # Yellow 
        elif proto == 'HTTP': 
            color = '\033[94m'  # Blue 
        elif proto == 'HTTPS': 
            color = '\033[95m'  # Magenta 
        else: 
            color = '\033[96m'  # Cyan 
         
        # Add warning for malicious patterns 
        warning = "" 
        if packet.get('is_malicious_pattern', False): 
            warning = "\033[91m [!]\033[0m" 
 
        print(f"\033[90m{timestamp}\033[0m " 
              f"\033[97m{src:>25} -> {dst:<25}\033[0m " 
              f"{color}[{proto:5}]\033[0m " 
              f"\033[97m{length:>5} bytes\033[0m{warning}") 
     
    def _print_threat_alert(self, alert): 
        """Print threat alert to terminal""" 
        timestamp = alert['timestamp'].strftime('%H:%M:%S.%f')[:-3] 
        src = f"{alert['flow_key'].src_ip}:{alert['flow_key'].src_port}" 
        dst = f"{alert['flow_key'].dst_ip}:{alert['flow_key'].dst_port}" 
         
        print(f"\n\033[91m[!] THREAT ALERT [{timestamp}]\033[0m") 
        print(f"\033[91m   Source: {src} -> Destination: {dst}\033[0m") 
        print(f"\033[91m   Protocol: {alert['flow_key'].protocol}\033[0m") 
        print(f"\033[91m   Prediction: {alert['prediction']} (Confidence:  {alert['confidence']:.1%})\033[0m")
        print(f"\033[91m   Top Suspicious Features:\033[0m") 
         
        # Show top 3 features by value 
        features = alert['features'] 
        top_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)[:3] 
        for feat, val in top_features: 
            print(f"\033[91m     {feat}: {val:.2f}\033[0m") 
        print() 
     
    def get_statistics(self): 
        """Get current statistics""" 
        uptime = time.time() - self.start_time 
         
        avg_pps = 0 
        if self.pps_history: 
            avg_pps = sum(self.pps_history) / len(self.pps_history) 
         
        # Calculate more detailed PPS statistics 
        if self.pps_data: 
            pps_list = list(self.pps_data) 
            sorted_pps = sorted(pps_list) 
            mid = len(sorted_pps) // 2 
            median_pps = (sorted_pps[mid] + sorted_pps[-mid-1]) / 2 if len(sorted_pps) % 2 == 0  else sorted_pps[mid]
             
            variance = sum((x - avg_pps) ** 2 for x in pps_list) / len(pps_list) if len(pps_list)  > 1 else 0
            std_dev_pps = variance ** 0.5 
        else: 
            median_pps = 0 
            std_dev_pps = 0 
         
        # Get top 5 source IPs 
        top_source_ips = self.source_ip_counts.most_common(5) 
         
        # Get threat detection statistics 
        threat_stats = self.threat_detector.get_statistics() 
         
        # Get IP threat analyses 
        top_suspicious_ips = self.ip_tracker.get_top_suspicious_ips(5) 
        all_ip_analyses = self.ip_tracker.get_all_ip_analyses() 
         
        return { 
            'total_packets': self.packet_count, 
            'current_pps': self.current_pps, 
            'avg_pps': avg_pps, 
            'median_pps': median_pps, 
            'max_pps': self.max_pps if self.max_pps > 0 else 0, 
            'min_pps': self.min_pps if self.min_pps != float('inf') else 0, 
            'std_dev_pps': std_dev_pps, 
            'total_bytes': self.total_bytes, 
            'uptime': uptime, 
            'protocol_counts': self.protocol_counts.copy(), 
            'top_source_ips': top_source_ips, 
            'threat_stats': threat_stats, 
            'active_flows': self.flow_extractor.get_active_flow_count(), 
            'completed_flows': self.flow_extractor.get_completed_flow_count(), 
            'model_loaded': self.threat_detector.is_model_loaded(), 
            'recent_alerts': list(self.threat_alerts)[-5:][::-1], 
            'top_suspicious_ips': top_suspicious_ips,  # NEW 
            'all_ip_analyses': all_ip_analyses,        # NEW 
            'ip_tracker': self.ip_tracker              # NEW 
        } 
 
# ============================================= 
# Dashboard UI — Professional Unified SOC View 
# ============================================= 
 
 
# Page configuration 
 
 
# Inject professional theme 
st.markdown(THEME_CSS, unsafe_allow_html=True) 
 
def main(): 
    """Main application — single unified SOC dashboard""" 
    # Initialize dashboard engine 
    if 'dashboard' not in st.session_state: 
        st.session_state.dashboard = EnhancedPacketCaptureDashboard() 
 
    dashboard = st.session_state.dashboard 
    stats = dashboard.get_statistics() 
 
    # Render sidebar & main content 
    render_sidebar(dashboard, stats) 
    render_main(dashboard, stats) 
 
    # Auto-refresh every 2 seconds 
    time.sleep(2) 
    st.rerun() 
 
if __name__ == "__main__": 
    main() 
  