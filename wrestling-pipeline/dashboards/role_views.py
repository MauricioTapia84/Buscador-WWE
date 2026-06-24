from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from data_client import search_catalog

ADMIN_SECRET = "K#9vLp$2mQx@7nRf!4Zd"


def hide_native_page_nav():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_session_state():
    if "admin_unlocked" not in st.session_state:
        st.session_state["admin_unlocked"] = False
    if "selected_role" not in st.session_state:
        st.session_state["selected_role"] = "Fanático"


def available_roles():
    roles = ["Fanático", "Periodista"]
    if st.session_state.get("admin_unlocked"):
        roles.append("Desarrollador / Analista")
    return roles


def apply_secret(search_term: str):
    if search_term.strip() == ADMIN_SECRET:
        st.session_state["admin_unlocked"] = True
        return True
    return False


def render_role_selector():
    roles = available_roles()
    current = st.session_state.get("selected_role", roles[0])
    if current not in roles:
        current = roles[0]
    index = roles.index(current)
    st.session_state["selected_role"] = st.radio(
        "Perfil",
        roles,
        index=index,
        horizontal=True,
    )
    return st.session_state["selected_role"]


def _search_results(search_term: str, wrestlers: list[dict]):
    if not search_term.strip() or search_term.strip() == ADMIN_SECRET:
        return wrestlers, None
    payload, error = search_catalog(search_term)
    if payload and payload.get("wrestlers"):
        return payload["wrestlers"], error

    lowered = search_term.lower().strip()
    local = [
        wrestler
        for wrestler in wrestlers
        if lowered in str(wrestler.get("artist_name") or wrestler.get("name") or "").lower()
    ]
    return local, error


def _format_value(value, fallback="No disponible"):
    if value is None:
        return fallback
    if isinstance(value, float) and pd.isna(value):
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _render_analytics_card(wrestler: dict, analytics: dict):
    title_count = wrestler.get("titles_won") or 0
    wins = analytics.get("wins", 0)
    losses = analytics.get("losses", 0)
    total_matches = analytics.get("total_matches", 0)
    win_rate = analytics.get("win_rate", 0.0)
    most_common_match_type = analytics.get("most_common_match_type")
    source = analytics.get("source") or "N/A"
    reason = analytics.get("reason") or "Sin información adicional"
    years_active = analytics.get("active_years") or analytics.get("career_years") or "N/D"

    avatar = wrestler.get("artist_name") or wrestler.get("name") or "WWE"
    initials = "".join([part[0] for part in str(avatar).split() if part])[:2].upper() or "WW"
    height = wrestler.get("height") or "N/D"
    weight = wrestler.get("weight") or "N/D"

    st.markdown(
        """
        <style>
        .result-card {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(15, 23, 42, 0.16);
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 24px;
            color: #0f172a;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
        }
        .result-card-header {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            align-items: flex-start;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .wrestler-info {
            display: flex;
            gap: 18px;
            align-items: center;
        }
        .avatar-placeholder {
            width: 72px;
            height: 72px;
            border-radius: 22px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, #ef4444, #7f1d1d);
            color: #fff;
            font-size: 28px;
            font-weight: 700;
        }
        .wrestler-name {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 6px;
        }
        .wrestler-name small {
            display: block;
            color: #475569;
            font-size: 14px;
            font-weight: 500;
            margin-top: 4px;
        }
        .wrestler-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            color: #475569;
            font-size: 14px;
        }
        .badge-title {
            display: inline-flex;
            align-items: center;
            padding: 10px 16px;
            border-radius: 999px;
            background: #f8fafc;
            color: #0f172a;
            font-weight: 700;
            border: 1px solid rgba(15, 23, 42, 0.08);
        }
        .result-card-body {
            display: grid;
            gap: 24px;
            grid-template-columns: 1.4fr 1fr;
        }
        .section-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
            color: #0f172a;
        }
        .stats-grid {
            display: grid;
            gap: 14px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .stat-chip {
            padding: 16px;
            border-radius: 18px;
            background: #f8fafc;
            border: 1px solid rgba(15, 23, 42, 0.08);
        }
        .stat-chip .number {
            font-size: 24px;
            font-weight: 800;
            display: block;
            color: #0f172a;
            margin-bottom: 6px;
        }
        .stat-chip .label {
            font-size: 13px;
            color: #475569;
        }
        .notice-box {
            padding: 14px 16px;
            border-radius: 18px;
            background: #eef2ff;
            border: 1px solid #c7d2fe;
            color: #3730a3;
            font-size: 14px;
            line-height: 1.6;
        }
        .result-list {
            display: grid;
            gap: 12px;
        }
        .result-item {
            padding: 14px 16px;
            border-radius: 16px;
            background: #fff;
            border: 1px solid rgba(15, 23, 42, 0.06);
        }
        .result-item strong {
            display: block;
            font-size: 14px;
            margin-bottom: 4px;
            color: #0f172a;
        }
        .result-item span {
            color: #475569;
            font-size: 13px;
        }
        @media (max-width: 900px) {
            .result-card-body {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-card-header">
                <div class="wrestler-info">
                    <div class="avatar-placeholder">{initials}</div>
                    <div>
                        <div class="wrestler-name">{wrestler.get('artist_name') or wrestler.get('name') or 'Sin nombre'}</div>
                        <div class="wrestler-meta">
                            <span>📏 {height}</span>
                            <span>⚖️ {weight}</span>
                            <span>🏛️ WWE</span>
                            <span>📅 {years_active}</span>
                        </div>
                    </div>
                </div>
                <div>
                    <span class="badge-title">🏆 {title_count}× Campeón</span>
                </div>
            </div>

            <div class="result-card-body">
                <div>
                    <div class="section-title">🏅 Palmarés y logros</div>
                    <div class="result-list">
                        <div class="result-item">
                            <strong>Total de combates</strong>
                            <span>{total_matches if total_matches else 'N/D'}</span>
                        </div>
                        <div class="result-item">
                            <strong>Victorias</strong>
                            <span>{wins if wins else 'N/D'}</span>
                        </div>
                        <div class="result-item">
                            <strong>Derrotas</strong>
                            <span>{losses if losses else 'N/D'}</span>
                        </div>
                        <div class="result-item">
                            <strong>Tipo de combate más común</strong>
                            <span>{_format_value(most_common_match_type)}</span>
                        </div>
                    </div>

                    <div style="margin-top: 20px;">
                        <div class="section-title">🔥 Contexto de la métrica</div>
                        <div class="notice-box">
                            Fuente: {source}<br>
                            {reason}
                        </div>
                    </div>
                </div>
                <div>
                    <div class="section-title">📊 Estadísticas clave</div>
                    <div class="stats-grid">
                        <div class="stat-chip"><span class="number">{total_matches if total_matches else 'N/D'}</span><span class="label">Combates</span></div>
                        <div class="stat-chip"><span class="number">{(win_rate * 100):.0f}%</span><span class="label">Win-Rate</span></div>
                        <div class="stat-chip"><span class="number">{wins if wins else 'N/D'}</span><span class="label">Victorias</span></div>
                        <div class="stat-chip"><span class="number">{losses if losses else 'N/D'}</span><span class="label">Derrotas</span></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _pick_wrestler(search_term: str, wrestlers: list[dict], label: str):
    filtered, error = _search_results(search_term, wrestlers)
    options = filtered or wrestlers
    options = sorted(
        options,
        key=lambda wrestler: (
            -int(bool(wrestler.get("image_url") or wrestler.get("image_large"))),
            -int(bool(wrestler.get("biography") or wrestler.get("description") or wrestler.get("extract"))),
            -int(bool(wrestler.get("birth_date") or wrestler.get("date_born") or wrestler.get("real_name"))),
            -int(wrestler.get("titles_won", 0) or 0),
            str(wrestler.get("artist_name") or wrestler.get("name") or ""),
        ),
    )
    if not options:
        return None, error

    labels = [w.get("artist_name") or w.get("canonical_name") or w.get("name") or "Sin nombre" for w in options]
    index = 0
    if search_term.strip() and search_term.strip() != ADMIN_SECRET:
        for idx, text in enumerate(labels):
            if search_term.lower() in text.lower():
                index = idx
                break

    selected_label = st.selectbox(label, labels, index=index)
    selected = next((item for item, name in zip(options, labels) if name == selected_label), options[0])
    return selected, error


def render_fanatico_view(search_term: str, wrestlers: list[dict], titles: list[dict]):
    st.subheader("Perfil Fanático")
    st.caption("Ficha visual, biografía y datos curiosos del personaje.")

    wrestler, error = _pick_wrestler(search_term, wrestlers, "Selecciona un luchador")
    if error:
        st.warning(f"La búsqueda remota devolvió un problema: {error}")
    if not wrestler:
        st.info("No hay luchadores disponibles todavía.")
        return

    left, right = st.columns([0.75, 1.25])
    with left:
        image_url = wrestler.get("image_url") or wrestler.get("image_large") or wrestler.get("image_path")
        if image_url:
            st.image(image_url)
        else:
            placeholder_file = Path(__file__).parent.joinpath("placeholder.png")
            if placeholder_file.exists():
                st.image(str(placeholder_file))
            else:
                st.markdown(
                    """
                    <div style="height:320px;border-radius:18px;background:linear-gradient(135deg,#1f2937,#7f1d1d);display:flex;align-items:center;justify-content:center;color:#fef2f2;font-size:28px;font-weight:700;">
                        WWE
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with right:
        st.markdown(f"## {_format_value(wrestler.get('artist_name') or wrestler.get('name'))}")
        st.markdown(f"**Fecha de nacimiento:** {_format_value(wrestler.get('birth_date') or wrestler.get('date_born'))}")

        facts_a, facts_b = st.columns(2)
        facts_a.metric("Altura", _format_value(wrestler.get("height")))
        facts_b.metric("Peso", _format_value(wrestler.get("weight")))

        st.markdown("### Biografía")
        st.write(_format_value(wrestler.get("biography") or wrestler.get("description") or wrestler.get("extract")))

        history = wrestler.get("title_history") or []
        st.markdown("### Curiosidades")
        c1, c2 = st.columns(2)
        c1.metric("Reinados visibles", len(history))
        c2.metric("Títulos referenciados", len({item.get("title") for item in history if item.get("title")}))


def render_periodista_view(search_term: str, wrestlers: list[dict], titles: list[dict]):
    st.subheader("Perfil Periodista")
    st.caption("Cronología de reinados y eventos exactos asociados al luchador.")

    wrestler, error = _pick_wrestler(search_term, wrestlers, "Selecciona un luchador para revisar su historial")
    if error:
        st.warning(f"La búsqueda remota devolvió un problema: {error}")
    if not wrestler:
        st.info("No hay luchadores disponibles todavía.")
        return

    history = wrestler.get("title_history") or []
    if not history:
        st.warning("Este luchador no tiene reinados enlazados en los datos actuales.")
        return

    history_df = pd.DataFrame(history)
    for column in ["start_date", "end_date", "won_date", "event_date"]:
        if column in history_df.columns:
            history_df[column] = pd.to_datetime(history_df[column], errors="coerce")
    if "days_recognized" in history_df.columns:
        history_df["days_recognized"] = pd.to_numeric(history_df["days_recognized"], errors="coerce")
    if "reign_days" in history_df.columns:
        history_df["reign_days"] = pd.to_numeric(history_df["reign_days"], errors="coerce")

    top_a, top_b, top_c, top_d = st.columns(4)
    top_a.metric("Reinados registrados", len(history_df))
    top_b.metric("Primer reinado", _format_value(history_df["start_date"].min().date().isoformat() if history_df["start_date"].notna().any() else None))
    top_c.metric("Último evento", _format_value(history_df["event_name"].dropna().iloc[-1] if history_df["event_name"].notna().any() else None))
    total_days = history_df["days_recognized"].dropna().sum() if "days_recognized" in history_df.columns else 0
    if not total_days and "reign_days" in history_df.columns:
        total_days = history_df["reign_days"].dropna().sum()
    top_d.metric("Días reconocidos", int(total_days) if pd.notna(total_days) else 0)

    eras = []
    if "era" in history_df.columns:
        eras = sorted({str(value).strip() for value in history_df["era"].dropna() if str(value).strip()})
    if eras:
        st.markdown(f"**Eras cubiertas:** {', '.join(eras)}")

    st.markdown("### Momentos clave")
    card_columns = st.columns(2)
    for idx, reign in enumerate(history_df.to_dict(orient="records")):
        start_date = reign.get("start_date")
        end_date = reign.get("end_date")
        period_parts = []
        if pd.notna(start_date):
            period_parts.append(start_date.date().isoformat())
        if pd.notna(end_date):
            period_parts.append(end_date.date().isoformat())
        period = " a ".join(period_parts) if period_parts else "Fecha no disponible"
        location = _format_value(reign.get("location"))
        event_name = _format_value(reign.get("event_name"))
        previous_champion = _format_value(reign.get("defeated_for_title"))
        lost_title_to = _format_value(reign.get("lost_title_to"))
        era = _format_value(reign.get("era"))
        notes = _format_value(reign.get("notes"))
        days_value = reign.get("days_recognized") if reign.get("days_recognized") not in [None, ""] else reign.get("reign_days")

        with card_columns[idx % 2]:
            st.markdown(
                f"""
                <div style="padding:18px;border-radius:20px;background:#ffffff;border:1px solid rgba(15,23,42,0.08);box-shadow:0 12px 32px rgba(15,23,42,0.06);margin-bottom:16px;">
                    <div style="font-size:13px;color:#64748b;font-weight:700;">Reinado #{idx + 1}</div>
                    <div style="font-size:20px;font-weight:800;color:#111827;margin:4px 0 8px;">{_format_value(reign.get("title"))}</div>
                    <div style="font-size:14px;color:#334155;line-height:1.65;">
                        <strong>Periodo:</strong> {period}<br/>
                        <strong>Evento:</strong> {event_name}<br/>
                        <strong>Ubicación:</strong> {location}<br/>
                        <strong>Venció a:</strong> {previous_champion}<br/>
                        <strong>Lo perdió ante:</strong> {lost_title_to}<br/>
                        <strong>Era:</strong> {era}<br/>
                        <strong>Días:</strong> {_format_value(days_value, 'No disponible')}<br/>
                        <strong>Notas:</strong> {notes}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Cronología")
    timeline = history_df.copy()
    for column in ["start_date", "end_date", "won_date", "event_date"]:
        if column in timeline.columns:
            timeline[column] = pd.to_datetime(timeline[column], errors="coerce")
            if pd.api.types.is_datetime64_any_dtype(timeline[column]):
                timeline[column] = timeline[column].dt.strftime("%Y-%m-%d")
            else:
                timeline[column] = timeline[column].astype(str)
    keep = [
        column
        for column in [
            "title",
            "overall_reign",
            "champion_reign_number",
            "start_date",
            "end_date",
            "end_date_inferred",
            "event_name",
            "location",
            "reign_days",
            "days_recognized",
            "era",
            "defeated_for_title",
            "lost_title_to",
            "notes",
        ]
        if column in timeline.columns
    ]
    st.dataframe(timeline[keep], use_container_width=True, hide_index=True)

    counts = history_df["title"].fillna("Sin título").value_counts().reset_index()
    counts.columns = ["title", "reigns"]
    fig = px.bar(counts, x="title", y="reigns", color="title", title="Reinados por campeonato")
    fig.update_layout(showlegend=False, height=360)
    st.plotly_chart(fig, use_container_width=True)


def render_developer_view(search_term: str, wrestlers: list[dict], titles: list[dict]):
    st.subheader("Perfil Desarrollador / Analista")
    st.caption("KPIs calculados desde `matches_normalized` y agregados sobre la entidad unificada.")

    if not st.session_state.get("admin_unlocked"):
        st.error("Acceso restringido. Ingresa la clave de administrador en el buscador para habilitar esta vista.")
        return

    wrestler, error = _pick_wrestler(search_term, wrestlers, "Selecciona un luchador para revisar métricas")
    if error:
        st.warning(f"La búsqueda remota devolvió un problema: {error}")
    if not wrestler:
        st.info("No hay luchadores disponibles todavía.")
        return

    analytics = wrestler.get("analytics") or {}
    analytics_available = bool(analytics.get("data_available"))
    total_matches = analytics.get("total_matches", 0)
    wins = analytics.get("wins", 0)
    losses = analytics.get("losses", 0)
    win_rate = analytics.get("win_rate", 0.0)
    common_type = analytics.get("most_common_match_type")

    if not analytics_available and analytics.get("reason"):
        st.warning(analytics["reason"])

    a, b, c, d = st.columns(4)
    a.metric("Luchas registradas", total_matches if analytics_available else "N/D")
    b.metric("Win-Rate %", f"{win_rate:.2f}" if analytics_available else "N/D")
    c.metric("Victorias", wins if analytics_available else "N/D")
    d.metric("Derrotas", losses if analytics_available else "N/D")

    st.markdown(f"**Estipulación más común:** {_format_value(common_type) if analytics_available else 'No disponible'}")

    chart_data = pd.DataFrame(
        [
            {"metric": "Victorias", "value": wins},
            {"metric": "Derrotas", "value": losses},
        ]
    )
    if analytics_available:
        fig = px.bar(chart_data, x="metric", y="value", color="metric", title="Balance competitivo")
        fig.update_layout(showlegend=False, height=320)
        st.plotly_chart(fig, use_container_width=True)

    history = pd.DataFrame(wrestler.get("title_history") or [])
    if not history.empty and "title" in history.columns:
        counts = history["title"].fillna("Sin título").value_counts().reset_index()
        counts.columns = ["title", "count"]
        pie = px.pie(counts, names="title", values="count", title="Distribución de títulos visibles")
        pie.update_layout(height=320)
        st.plotly_chart(pie, use_container_width=True)

    st.markdown("### Payload analítico")
    _render_analytics_card(wrestler, analytics)
