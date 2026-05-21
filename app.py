"""
Main Streamlit UI for the RAG Chatbot.
"""

import streamlit as st
import logging
import time
from datetime import datetime

# ── page config (must be first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="assets/favicon.png" if __import__("os").path.exists("assets/favicon.png") else "💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from rag_pipeline import RAGPipeline
from web_scraper import WebScraper
from export_utils import export_as_txt, export_as_csv, export_as_json, export_as_pdf
from evaluation import batch_evaluate
from llm_provider import GROQ_MODELS
import styles  # injects CSS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════ #
#  Session State                                                       #
# ═══════════════════════════════════════════════════════════════════ #

def init_state():
    defaults = {
        "pipeline": None,
        "messages": [],           # [{role, content, timestamp, eval, sources, chunks}]
        "api_key": "",
        "llm_ready": False,
        "scraper": WebScraper(),
        "active_tab": "chat",
        "eval_history": [],
        "search_mode": "hybrid",
        "chunk_size": 512,
        "chunk_overlap": 64,
        "top_k": 5,
        "multilingual": True,
        "eval_enabled": True,
        "doc_metadata": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ═══════════════════════════════════════════════════════════════════ #
#  Pipeline helpers                                                    #
# ═══════════════════════════════════════════════════════════════════ #

def get_pipeline() -> RAGPipeline:
    if st.session_state.pipeline is None:
        st.session_state.pipeline = RAGPipeline()
    return st.session_state.pipeline


def try_init_llm(provider, model, api_key):
    pipeline = get_pipeline()
    try:
        pipeline.llm.initialize(provider=provider, model_name=model, api_key=api_key)
        pipeline.multilingual.enabled = st.session_state.multilingual
        st.session_state.llm_ready = True
        return True, None
    except Exception as e:
        st.session_state.llm_ready = False
        return False, str(e)


# ═══════════════════════════════════════════════════════════════════ #
#  Sidebar                                                             #
# ═══════════════════════════════════════════════════════════════════ #

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">RAG Chatbot</div>', unsafe_allow_html=True)
        st.markdown("---")

        # ── LLM Settings ──────────────────────────────────────────
        st.markdown("### LLM Configuration")
        provider = st.selectbox(
            "Provider", ["groq", "huggingface"], key="llm_provider",
            help="Groq is recommended — fast and free."
        )
        if provider == "groq":
            model = st.selectbox("Model", GROQ_MODELS, key="llm_model")
        else:
            model = st.text_input(
                "HuggingFace Model ID",
                value="mistralai/Mistral-7B-Instruct-v0.2",
                key="llm_model_hf",
            )

        api_key = st.text_input(
            "API Key", type="password",
            placeholder="Paste your API key here...",
            key="api_key_input",
        )

        if st.button("Connect LLM", key="btn_connect_llm", use_container_width=True):
            if not api_key.strip():
                st.error("API key is required.")
            else:
                with st.spinner("Connecting..."):
                    ok, err = try_init_llm(provider, model, api_key.strip())
                if ok:
                    st.success("LLM connected successfully.")
                else:
                    st.error(f"Failed: {err}")

        # Status badge
        if st.session_state.llm_ready:
            st.markdown('<span class="badge badge-green">LLM Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-red">LLM Not Connected</span>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Retrieval Settings ───────────────────────────────────
        st.markdown("### Retrieval Settings")
        st.session_state.search_mode = st.radio(
            "Search Mode",
            ["hybrid", "dense", "sparse"],
            key="search_mode_radio",
            horizontal=True,
        )
        st.session_state.top_k = st.slider("Top-K Chunks", 1, 15, 5, key="top_k_slider")
        st.session_state.eval_enabled = st.toggle("Enable Evaluation", value=True)
        st.session_state.multilingual = st.toggle("Multilingual Mode", value=True)

        st.markdown("---")

        # ── Chunking Settings ────────────────────────────────────
        with st.expander("Chunking Settings"):
            chunk_size = st.slider("Chunk Size", 128, 2048, 512, step=64)
            chunk_overlap = st.slider("Chunk Overlap", 0, 256, 64, step=16)
            strategy = st.selectbox("Strategy", ["recursive", "character", "token"])
            if st.button("Apply Chunking Settings", key="btn_apply_chunk"):
                p = get_pipeline()
                p.chunker.update_settings(chunk_size, chunk_overlap, strategy)
                st.success("Chunking settings updated.")

        st.markdown("---")

        # ── Quick Actions ────────────────────────────────────────
        st.markdown("### Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat", key="btn_clear_chat", use_container_width=True):
                st.session_state.messages = []
                get_pipeline().reset_conversation()
                st.rerun()
        with col2:
            if st.button("Reset All", key="btn_reset_all", use_container_width=True):
                st.session_state.messages = []
                st.session_state.eval_history = []
                st.session_state.doc_metadata = []
                get_pipeline().reset_all()
                st.rerun()

        # ── Status panel ─────────────────────────────────────────
        st.markdown("---")
        st.markdown("### System Status")
        p = get_pipeline()
        status = p.status
        st.metric("Indexed Chunks", status["documents_indexed"])
        st.metric("Chat Turns", status["conversation_turns"])
        if status["sources"]:
            with st.expander("Indexed Sources"):
                for s in status["sources"]:
                    st.markdown(f"- `{s}`")

        st.markdown("---")
        st.caption("Built with LangChain · FAISS · RAGAS · Groq")


# ═══════════════════════════════════════════════════════════════════ #
#  Tab: Documents                                                      #
# ═══════════════════════════════════════════════════════════════════ #

def render_documents_tab():
    st.markdown("## Document Management")
    col_upload, col_web = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown("### Upload Files")
        st.markdown("Supported: PDF, DOCX, TXT, MD")
        uploaded = st.file_uploader(
            "Drop files here",
            type=["pdf", "docx", "doc", "txt", "md"],
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed",
        )
        if uploaded:
            if st.button("Process Files", key="btn_process_files", use_container_width=True):
                with st.spinner("Loading and indexing..."):
                    result = get_pipeline().ingest_files(uploaded)
                if result["success"]:
                    st.success(
                        f"Indexed {result['chunks_added']} chunks from "
                        f"{len(uploaded)} file(s). Total: {result['total_chunks']} chunks."
                    )
                    for f in uploaded:
                        st.session_state.doc_metadata.append({
                            "name": f.name,
                            "size_kb": round(f.size / 1024, 1),
                            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                    if result["errors"]:
                        st.warning("Some files had errors: " + "; ".join(result["errors"]))
                else:
                    st.error(result["message"])

    with col_web:
        st.markdown("### Web Scraping Mode")
        urls_input = st.text_area(
            "Enter URLs (one per line)",
            placeholder="https://example.com\nhttps://docs.example.com/guide",
            height=120,
            key="urls_input",
        )
        follow_links = st.checkbox("Follow internal links", value=False)
        max_pages = st.number_input("Max pages to scrape", 1, 20, 5)

        if st.button("Scrape & Index", key="btn_scrape", use_container_width=True):
            urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()]
            if not urls:
                st.warning("Please enter at least one URL.")
            else:
                with st.spinner(f"Scraping {len(urls)} URL(s)..."):
                    scraper = st.session_state.scraper
                    web_docs = scraper.scrape_multiple(
                        urls, follow_links=follow_links, max_pages=max_pages
                    )
                if not web_docs:
                    st.error("No content could be scraped from the provided URLs.")
                else:
                    result = get_pipeline().ingest_web_documents(web_docs)
                    if result["success"]:
                        st.success(
                            f"Scraped {len(web_docs)} page(s), indexed {result['chunks_added']} chunks."
                        )
                    else:
                        st.error(result["message"])

    # ── Document table ───────────────────────────────────────────────
    if st.session_state.doc_metadata:
        st.markdown("---")
        st.markdown("### Indexed Documents")
        import pandas as pd
        df = pd.DataFrame(st.session_state.doc_metadata)
        st.dataframe(df, use_container_width=True, hide_index=True)

        if st.button("Clear All Documents", key="btn_clear_docs"):
            st.session_state.doc_metadata = []
            get_pipeline().reset_all()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════ #
#  Tab: Chat                                                           #
# ═══════════════════════════════════════════════════════════════════ #

def render_chat_tab():
    st.markdown("## Chat")

    # Readiness warnings
    p = get_pipeline()
    if not p.llm.is_ready:
        st.warning("Connect the LLM from the sidebar to start chatting.")
    if not p.vector_store.is_ready:
        st.info("No documents indexed yet. Go to the Documents tab to add knowledge.")

    # ── Message history ──────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            role = msg["role"]
            with st.chat_message(role):
                st.markdown(msg["content"])
                # Meta row
                meta_parts = []
                if msg.get("timestamp"):
                    meta_parts.append(msg["timestamp"])
                if msg.get("sources"):
                    meta_parts.append("Sources: " + ", ".join(
                        [s.split("/")[-1] for s in msg["sources"]]
                    ))
                if msg.get("retrieval_mode"):
                    meta_parts.append(f"Mode: {msg['retrieval_mode']}")
                if meta_parts:
                    st.caption("  |  ".join(meta_parts))

                # Evaluation badge
                ev = msg.get("eval")
                if ev:
                    with st.expander("Evaluation Scores"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Faithfulness", f"{ev.faithfulness:.2f}")
                        c2.metric("Relevancy", f"{ev.answer_relevancy:.2f}")
                        c3.metric("Precision", f"{ev.context_precision:.2f}")
                        c4.metric("Overall", f"{ev.overall_score:.2f}")

                # Retrieved chunks
                if msg.get("chunks") and role == "assistant":
                    with st.expander(f"Retrieved Chunks ({len(msg['chunks'])})"):
                        for i, chunk in enumerate(msg["chunks"]):
                            src = chunk.get("metadata", {}).get("source", "Unknown")
                            pg = chunk.get("metadata", {}).get("page", "")
                            pg_str = f" · Page {pg}" if pg else ""
                            st.markdown(
                                f'<div class="chunk-card">'
                                f'<span class="chunk-source">[{i+1}] {src}{pg_str}</span>'
                                f'<p class="chunk-text">{chunk["page_content"][:400]}...</p>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

    # ── Input ────────────────────────────────────────────────────────
    user_input = st.chat_input(
        "Ask a question about your documents...",
        key="chat_input",
        disabled=not (p.llm.is_ready and p.vector_store.is_ready),
    )

    if user_input:
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": ts,
        })

        with st.spinner("Retrieving and generating..."):
            result = p.query(
                question=user_input,
                top_k=st.session_state.top_k,
                search_mode=st.session_state.search_mode,
                evaluate=st.session_state.eval_enabled,
            )

        ev = result.get("evaluation")
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "sources": result.get("sources", []),
            "chunks": result.get("chunks", []),
            "eval": ev,
            "retrieval_mode": result.get("retrieval_mode", ""),
        })

        if ev:
            st.session_state.eval_history.append({
                "question": user_input,
                "answer": result["answer"],
                "faithfulness": ev.faithfulness,
                "answer_relevancy": ev.answer_relevancy,
                "context_precision": ev.context_precision,
                "overall_score": ev.overall_score,
                "timestamp": ts,
            })

        st.rerun()


# ═══════════════════════════════════════════════════════════════════ #
#  Tab: Evaluation                                                     #
# ═══════════════════════════════════════════════════════════════════ #

def render_evaluation_tab():
    st.markdown("## Evaluation Dashboard")
    st.markdown(
        "Metrics are computed using the **RAGAS** framework "
        "(with heuristic fallback). Scores range from 0 to 1."
    )

    if not st.session_state.eval_history:
        st.info("No evaluation data yet. Start chatting to collect metrics.")
        return

    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    df = pd.DataFrame(st.session_state.eval_history)

    # ── Summary cards ────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Faithfulness",    f"{df['faithfulness'].mean():.3f}")
    c2.metric("Avg Answer Relevancy", f"{df['answer_relevancy'].mean():.3f}")
    c3.metric("Avg Context Precision", f"{df['context_precision'].mean():.3f}")
    c4.metric("Avg Overall Score",   f"{df['overall_score'].mean():.3f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Score Trends")
        fig = px.line(
            df.reset_index(),
            x="index",
            y=["faithfulness", "answer_relevancy", "context_precision", "overall_score"],
            labels={"index": "Query #", "value": "Score", "variable": "Metric"},
            color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B", "#6366F1"],
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_family="Inter",
            legend_title_text="Metric",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### Metric Distribution")
        fig2 = go.Figure()
        for col, color in zip(
            ["faithfulness", "answer_relevancy", "context_precision"],
            ["#2563EB", "#10B981", "#F59E0B"],
        ):
            fig2.add_trace(go.Box(
                y=df[col], name=col.replace("_", " ").title(),
                marker_color=color, boxpoints="all",
            ))
        fig2.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_family="Inter",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Query-Level Scores")
    display_df = df[["timestamp", "question", "faithfulness",
                      "answer_relevancy", "context_precision", "overall_score"]].copy()
    display_df["question"] = display_df["question"].str[:80] + "..."
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    if st.button("Clear Evaluation History", key="btn_clear_eval"):
        st.session_state.eval_history = []
        st.rerun()


# ═══════════════════════════════════════════════════════════════════ #
#  Tab: Export                                                         #
# ═══════════════════════════════════════════════════════════════════ #

def render_export_tab():
    st.markdown("## Export Chat")

    if not st.session_state.messages:
        st.info("No messages to export. Start a conversation first.")
        return

    col1, col2 = st.columns(2)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    msgs = st.session_state.messages

    with col1:
        st.markdown("### Download Chat History")
        fmt = st.selectbox("Format", ["TXT", "CSV", "JSON", "PDF"], key="export_fmt")
        if st.button("Generate Export", key="btn_export", use_container_width=True):
            if fmt == "TXT":
                data = export_as_txt(msgs, "RAG Chatbot Export")
                mime, ext = "text/plain", "txt"
            elif fmt == "CSV":
                data = export_as_csv(msgs)
                mime, ext = "text/csv", "csv"
            elif fmt == "JSON":
                data = export_as_json(msgs)
                mime, ext = "application/json", "json"
            else:
                data = export_as_pdf(msgs, "RAG Chatbot Export")
                mime, ext = "application/pdf", "pdf"

            st.download_button(
                label=f"Download .{ext}",
                data=data,
                file_name=f"rag_chat_{ts}.{ext}",
                mime=mime,
                key=f"dl_{ext}",
            )

    with col2:
        st.markdown("### Export Evaluation Report")
        if st.session_state.eval_history:
            import pandas as pd
            df = pd.DataFrame(st.session_state.eval_history)
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Evaluation CSV",
                data=csv_bytes,
                file_name=f"rag_eval_{ts}.csv",
                mime="text/csv",
                key="dl_eval_csv",
                use_container_width=True,
            )
        else:
            st.info("No evaluation data to export.")


# ═══════════════════════════════════════════════════════════════════ #
#  Main Layout                                                         #
# ═══════════════════════════════════════════════════════════════════ #

def main():
    render_sidebar()

    st.markdown('<h1 class="main-title">RAG Chatbot</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="main-subtitle">Retrieval-Augmented Generation with evaluation, '
        'hybrid search, and multilingual support.</p>',
        unsafe_allow_html=True,
    )

    tab_chat, tab_docs, tab_eval, tab_export = st.tabs(
        ["Chat", "Documents", "Evaluation", "Export"]
    )

    with tab_chat:
        render_chat_tab()
    with tab_docs:
        render_documents_tab()
    with tab_eval:
        render_evaluation_tab()
    with tab_export:
        render_export_tab()


if __name__ == "__main__":
    main()
