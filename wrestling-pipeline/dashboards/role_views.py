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
            st.image(image_url, use_container_width=True)
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
        st.markdown(f"**Nombre real:** {_format_value(wrestler.get('real_name'))}")
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
    if "start_date" in history_df.columns:
        history_df["start_date"] = pd.to_datetime(history_df["start_date"], errors="coerce")
    if "end_date" in history_df.columns:
        history_df["end_date"] = pd.to_datetime(history_df["end_date"], errors="coerce")

    top_a, top_b, top_c = st.columns(3)
    top_a.metric("Reinados registrados", len(history_df))
    top_b.metric("Primer reinado", _format_value(history_df["start_date"].min().date().isoformat() if history_df["start_date"].notna().any() else None))
    top_c.metric("Último evento", _format_value(history_df["event_name"].dropna().iloc[-1] if history_df["event_name"].notna().any() else None))

    st.markdown("### Cronología")
    timeline = history_df.copy()
    for column in ["start_date", "end_date", "won_date"]:
        if column in timeline.columns:
            timeline[column] = pd.to_datetime(timeline[column], errors="coerce")
            if pd.api.types.is_datetime64_any_dtype(timeline[column]):
                timeline[column] = timeline[column].dt.strftime("%Y-%m-%d")
            else:
                timeline[column] = timeline[column].astype(str)
    keep = [column for column in ["title", "start_date", "end_date", "event_name", "won_date", "reign_days"] if column in timeline.columns]
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
    st.json(
        {
            "artist_name": wrestler.get("artist_name"),
            "name_slug": wrestler.get("name_slug"),
            "analytics": analytics,
            "titles_won": wrestler.get("titles_won"),
        }
    )
