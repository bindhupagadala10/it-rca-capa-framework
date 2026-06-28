import os
import re
import sys
from datetime import datetime
from html import escape
from io import BytesIO

import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# To switch to real model inference, comment/uncomment the lines below:
#from src.inference.mock_inference import generate_mock_rca as generate_rca, generate_mock_capa as generate_capa
from src.inference.rca_inference import generate_rca, generate_rca_from_incident
from src.inference.capa_inference import generate_capa_from_rca
from src.report.doc_generator import generate_docx
from src.validators.capa_validator import CAPAValidator
from src.validators.input_validator import validate_incident_input
from src.validators.rca_validator import validate_rca


PAGES = ("Incident Intake", "RCA Review", "CAPA Review", "Final Report")
DEFAULTS = {
    "current_page": "Incident Intake",
    "problem_description": "",
    "business_impact": "",
    "timeline": "",
    "incident_text": "",
    "rca_text": "",
    "capa_text": "",
    "rca_editor": "",
    "capa_editor": "",
    "rca_feedback": "",
    "capa_feedback": "",
    "rca_flags": [],
    "capa_flags": [],
    "rca_generated": False,
    "rca_validated": False,
    "rca_approved": False,
    "capa_generated": False,
    "capa_validated": False,
    "capa_approved": False,
    "pending_rca_editor": None,
    "pending_capa_editor": None,
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


def navigate(page: str) -> None:
    st.session_state.current_page = page


def apply_pending_editor_updates() -> None:
    pending_rca = st.session_state.pending_rca_editor
    if pending_rca is not None:
        st.session_state.rca_editor = pending_rca
        st.session_state.rca_text = pending_rca
        st.session_state.pending_rca_editor = None

    pending_capa = st.session_state.pending_capa_editor
    if pending_capa is not None:
        st.session_state.capa_editor = pending_capa
        st.session_state.capa_text = pending_capa
        st.session_state.pending_capa_editor = None


def restore_editor_state() -> None:
    if st.session_state.rca_text and not st.session_state.rca_editor:
        st.session_state.rca_editor = st.session_state.rca_text
    if st.session_state.capa_text and not st.session_state.capa_editor:
        st.session_state.capa_editor = st.session_state.capa_text


def section_text(text: str, heading: str, following_headings: tuple[str, ...]) -> str:

    # Accept headings with optional "Summary" and optional colon.
    heading_pattern = re.escape(heading)

    if heading.lower() == "root cause":
        heading_pattern = r"Root Cause(?: Summary)?"

    if not following_headings:
        match = re.search(
            rf"(?ims)^\s*{heading_pattern}\s*:?\s*$\s*(.*)\Z",
            text,
        )
        return match.group(1).strip() if match else ""

    end_pattern = "|".join(
        re.escape(item).replace(r"\ ", r"\s+") + r"\s*:?"
        for item in following_headings
    )

    match = re.search(
        rf"(?ims)"
        rf"^\s*{heading_pattern}\s*:?\s*$"
        rf"\s*(.*?)"
        rf"(?=^\s*(?:{end_pattern})\s*$|\Z)",
        text,
    )

    if not match:
        return ""

    value = match.group(1).strip()

    # Remove the leading "Answer:" if present.
    value = re.sub(r"(?im)^Answer:\s*", "", value)

    return value.strip()

def format_rca_for_review(generated_text: str) -> str:

    sections = {}

    current = None
    buffer = []

    for line in generated_text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("Why "):
            if current:
                sections[current] = "\n".join(buffer).strip()

            current = line.split(":")[0]  # Why 1, Why 2...
            buffer = []

            # keep the question after the colon
            if ":" in line:
                question = line.split(":", 1)[1].strip()
                if question:
                    buffer.append(question)

            continue

        if line.startswith("Root Cause Summary"):
            if current:
                sections[current] = "\n".join(buffer).strip()

            current = "Root Cause"
            buffer = []
            continue

        if line.startswith("Answer:"):
            line = line.replace("Answer:", "", 1).strip()

        buffer.append(line)

    if current:
        sections[current] = "\n".join(buffer).strip()

    result = []

    result.append(f"Root Cause\n\n{sections.get('Root Cause','')}")

    for i in range(1, 6):
        result.append(f"Why {i}\n\n{sections.get(f'Why {i}','')}")

    return "\n\n".join(result)

def format_capa_for_review(generated_text: str) -> str:

    sections = {}

    current = None
    buffer = []

    for line in generated_text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("Corrective Action"):
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = "Corrective Action"
            buffer = []
            continue

        if line.startswith("Corrective Actions"):
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = "Corrective Action"
            buffer = []
            continue

        if line.startswith("Preventive Action"):
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = "Preventive Action"
            buffer = []
            continue

        if line.startswith("Preventive Actions"):
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = "Preventive Action"
            buffer = []
            continue

        if line.startswith("Lessons Learned"):
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = "Lessons Learned"
            buffer = []
            continue

        buffer.append(line)

    if current:
        sections[current] = "\n".join(buffer).strip()

    return f"""Corrective Action

{sections.get("Corrective Action", "")}

Preventive Action

{sections.get("Preventive Action", "")}

Lessons Learned

{sections.get("Lessons Learned", "")}
""".strip()
def invalidate_rca() -> None:
    st.session_state.rca_validated = False
    st.session_state.rca_approved = False
    st.session_state.rca_flags = []
    st.session_state.capa_text = ""
    st.session_state.capa_editor = ""
    st.session_state.capa_flags = []
    st.session_state.capa_generated = False
    st.session_state.capa_validated = False
    st.session_state.capa_approved = False


def invalidate_capa() -> None:
    st.session_state.capa_validated = False
    st.session_state.capa_approved = False
    st.session_state.capa_flags = []


def sidebar_status(done: bool, completed: str, pending: str) -> None:
    if done:
        st.sidebar.success(completed, icon="✅")
    else:
        st.sidebar.info(pending, icon="⏳")


def render_sidebar() -> None:
    st.sidebar.title("Enterprise RCA-CAPA")
    # Check allowed pages based on workflow progress
    allowed_pages = ["Incident Intake"]
    if st.session_state.rca_generated:
        allowed_pages.append("RCA Review")
    if st.session_state.rca_approved:
        allowed_pages.append("CAPA Review")
    if st.session_state.capa_approved:
        allowed_pages.append("Final Report")

    # Force current page to be within allowed pages
    if st.session_state.current_page not in allowed_pages:
        st.session_state.current_page = allowed_pages[-1]

    # Render radio selector
    selected = st.sidebar.radio(
        "Workflow",
        PAGES,
        index=PAGES.index(st.session_state.current_page),
    )
    
    if selected != st.session_state.current_page:
        if selected in allowed_pages:
            st.session_state.current_page = selected
            st.rerun()
        else:
            st.toast(f"🔒 {selected} is locked. Complete previous steps first.", icon="🔒")
            st.rerun()
    st.sidebar.divider()
    st.sidebar.subheader("Workflow Progress")

    incident_complete = bool(st.session_state.incident_text.strip())
    sidebar_status(
        incident_complete, "Incident Details Completed", "Incident Details Pending"
    )
    sidebar_status(
        st.session_state.rca_generated, "RCA Generated", "RCA Generation Pending"
    )
    sidebar_status(
        st.session_state.rca_validated, "RCA Validated", "RCA Validation Pending"
    )
    sidebar_status(
        st.session_state.rca_approved, "RCA Approved", "RCA Approval Pending"
    )
    sidebar_status(
        st.session_state.capa_generated, "CAPA Generated", "CAPA Generation Pending"
    )
    sidebar_status(
        st.session_state.capa_validated, "CAPA Validated", "CAPA Validation Pending"
    )
    sidebar_status(
        st.session_state.capa_approved, "CAPA Approved", "CAPA Approval Pending"
    )
    sidebar_status(
        st.session_state.rca_approved and st.session_state.capa_approved,
        "Report Ready for DOCX Generation",
        "DOCX Generation Pending",
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="app-header">
          <div class="app-title">IT Incident Report Generator</div>
          <div class="app-subtitle">Enterprise Root Cause Analysis (RCA) and
          Corrective &amp; Preventive Action (CAPA) Automation Framework</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_flags(flags: list[dict], artifact: str) -> None:
    st.subheader("Validation Results")
    if not flags:
        st.success(f"{artifact} validation passed with no findings.", icon="✅")
        return

    st.error(
        f"{artifact} validation returned {len(flags)} finding(s). "
        "Resolve all findings and validate again before approval."
    )
    for flag in flags:
        severity = str(flag.get("severity", "UNKNOWN")).upper()
        css_class = {
            "HIGH": "finding-high",
            "MEDIUM": "finding-medium",
            "LOW": "finding-low",
        }.get(severity, "finding-medium")
        st.markdown(
            f"""
            <div class="finding-card {css_class}">
              <div class="finding-heading">
                {escape(str(flag.get("id", "VALIDATION")))} · {escape(severity)}
              </div>
              <div>{escape(str(flag.get("message", "Validation finding")))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def incident_intake() -> None:
    st.header("Incident Intake")
    st.caption("Capture the verified incident facts used to generate the RCA.")

    if st.session_state.rca_generated:
        st.info("Incident details are locked because RCA generation has started.")
        with st.container(border=True):
            st.text_area(
                "Problem Description",
                value=st.session_state.problem_description,
                height=190,
                disabled=True,
            )
            st.text_area(
                "Business Impact",
                value=st.session_state.business_impact,
                height=130,
                disabled=True,
            )
            st.text_area(
                "Investigation Timeline",
                value=st.session_state.timeline,
                height=180,
                disabled=True,
            )
        if st.button("Continue to RCA Review", type="primary", use_container_width=True):
            navigate("RCA Review")
            st.rerun()
        return

    if "problem_description_input" not in st.session_state:
        st.session_state.problem_description_input = st.session_state.problem_description
    if "business_impact_input" not in st.session_state:
        st.session_state.business_impact_input = st.session_state.business_impact
    if "timeline_input" not in st.session_state:
        st.session_state.timeline_input = st.session_state.timeline

    with st.container(border=True):
        st.subheader("Incident Details")
        left, right = st.columns([2, 1], gap="large")
        with left:
            st.text_area(
                "Problem Description *",
                key="problem_description_input",
                height=190,
                placeholder=(
                    "Describe the technical symptoms, affected service, observed "
                    "behavior, and relevant environmental details."
                ),
            )
        with right:
            st.info(
                "Provide at least 50 characters and eight meaningful words. "
                "Use confirmed incident facts rather than assumptions."
            )
        st.text_area(
            "Business Impact *",
            key="business_impact_input",
            height=130,
            placeholder=(
                "Describe affected users or services, duration, operational impact, "
                "and any SLA or compliance exposure."
            ),
        )
        st.text_area(
            "Investigation Timeline *",
            key="timeline_input",
            height=180,
            placeholder=(
                "09:00 - Alert received\n09:05 - Incident bridge opened\n"
                "09:20 - Technical team engaged\n09:45 - Service restored"
            ),
        )

    if not st.button("Generate RCA", type="primary", use_container_width=True):
        return

    errors = validate_incident_input(
        st.session_state.problem_description_input,
        st.session_state.business_impact_input,
        st.session_state.timeline_input,
    )
    if errors:
        st.error("Correct the following validation errors before continuing:")
        for error in errors:
            st.error(error, icon="⚠️")
        return

    st.session_state.problem_description = (
        st.session_state.problem_description_input.strip()
    )
    st.session_state.business_impact = st.session_state.business_impact_input.strip()
    st.session_state.timeline = st.session_state.timeline_input.strip()

    incident = (
        "Problem Description\n"
        f"{st.session_state.problem_description}\n\n"
        "Business Impact\n"
        f"{st.session_state.business_impact}\n\n"
        "Investigation Timeline\n"
        f"{st.session_state.timeline}"
    )
    from src.inference.rca_inference import generate_rca_from_incident
    rca = format_rca_for_review(
        generate_rca_from_incident(
            problem_description=st.session_state.problem_description,
            business_impact=st.session_state.business_impact,
            timeline=st.session_state.timeline,
        )
    )
    raw_rca = generate_rca_from_incident(
        problem_description=st.session_state.problem_description,
        business_impact=st.session_state.business_impact,
        timeline=st.session_state.timeline,
    )

    print("========== RAW RCA ==========")
    print(raw_rca)
    print("=============================")

    rca = format_rca_for_review(raw_rca)

    st.session_state.incident_text = incident
    st.session_state.rca_text = rca
    st.session_state.rca_editor = rca
    st.session_state.rca_generated = True
    invalidate_rca()
    navigate("RCA Review")
    st.rerun()


def rca_review() -> None:
    st.header("RCA Review")
    st.caption("Review, validate, refine, and approve the Root Cause Analysis.")
    if not st.session_state.rca_generated:
        st.warning("Generate an RCA from Incident Intake before starting RCA review.")
        if st.button("Go to Incident Intake", type="primary"):
            navigate("Incident Intake")
            st.rerun()
        return

    with st.expander("Incident Context"):
        st.text(st.session_state.incident_text)

    if st.session_state.rca_approved:
        st.info("The approved RCA is locked and available for read-only review.")
        st.text_area(
            "Approved Root Cause Analysis",
            value=st.session_state.rca_text,
            height=430,
            disabled=True,
        )
        if st.session_state.rca_validated:
            render_flags(st.session_state.rca_flags, "RCA")
        if st.button("Continue to CAPA Review", type="primary", use_container_width=True):
            navigate("CAPA Review")
            st.rerun()
        return

    st.text_area(
        "Root Cause Analysis",
        key="rca_editor",
        height=430,
        on_change=invalidate_rca,
    )
    st.session_state.rca_text = st.session_state.rca_editor.strip()

    col1, col2, col3 = st.columns(3)
    with col1:
        validate_clicked = st.button("Validate RCA", use_container_width=True)
    with col2:
        regenerate_clicked = st.button("Regenerate RCA", use_container_width=True)
    with col3:
        approve_clicked = st.button(
            "Approve RCA",
            type="primary",
            disabled=not (
                st.session_state.rca_validated
                and bool(st.session_state.rca_text)
            ),
            use_container_width=True,
        )

    if "rca_feedback_input" not in st.session_state:
        st.session_state.rca_feedback_input = st.session_state.rca_feedback
    st.text_area(
        "Reviewer Feedback (Optional)",
        key="rca_feedback_input",
        height=120,
        placeholder="Provide precise guidance for RCA regeneration.",
    )

    if validate_clicked:
        if not st.session_state.rca_text:
            st.error("RCA content cannot be empty.")
        else:
            st.session_state.rca_flags = validate_rca(
                st.session_state.incident_text, st.session_state.rca_text
            )
            st.session_state.rca_validated = True
            st.rerun()

    if regenerate_clicked:
        from src.inference.rca_inference import generate_rca_from_incident
        st.session_state.rca_feedback = st.session_state.rca_feedback_input.strip()
        rca = format_rca_for_review(
            generate_rca_from_incident(
                problem_description=st.session_state.problem_description,
                business_impact=st.session_state.business_impact,
                timeline=st.session_state.timeline,
                feedback=st.session_state.rca_feedback,
            )
        )
        invalidate_rca()
        st.session_state.pending_rca_editor = rca
        st.rerun()

    if approve_clicked:
        st.session_state.rca_approved = True
        capa = format_capa_for_review(
            generate_capa_from_rca(
                st.session_state.rca_text,
            )
        )
        st.session_state.capa_text = capa
        st.session_state.capa_editor = capa
        st.session_state.capa_generated = True
        st.session_state.capa_validated = False
        st.session_state.capa_approved = False
        st.session_state.capa_flags = []
        navigate("CAPA Review")
        st.rerun()

    if st.session_state.rca_validated:
        st.divider()
        render_flags(st.session_state.rca_flags, "RCA")


def capa_review() -> None:
    st.header("CAPA Review")
    st.caption("Review, validate, refine, and approve the action plan.")
    if not st.session_state.rca_approved:
        st.warning("Approve the RCA before starting CAPA review.")
        if st.button("Go to RCA Review", type="primary"):
            navigate("RCA Review")
            st.rerun()
        return
    if not st.session_state.capa_generated:
        st.warning("CAPA content has not been generated.")
        return

    with st.expander("Approved RCA"):
        st.text(st.session_state.rca_text)

    if st.session_state.capa_approved:
        st.info("The approved CAPA is locked and available for read-only review.")
        st.text_area(
            "Approved Corrective and Preventive Action Plan",
            value=st.session_state.capa_text,
            height=430,
            disabled=True,
        )
        if st.session_state.capa_validated:
            render_flags(st.session_state.capa_flags, "CAPA")
        if st.button("Continue to Final Report", type="primary", use_container_width=True):
            navigate("Final Report")
            st.rerun()
        return

    st.text_area(
        "Corrective and Preventive Action Plan",
        key="capa_editor",
        height=430,
        on_change=invalidate_capa,
    )
    st.session_state.capa_text = st.session_state.capa_editor.strip()

    col1, col2, col3 = st.columns(3)
    with col1:
        validate_clicked = st.button("Validate CAPA", use_container_width=True)
    with col2:
        regenerate_clicked = st.button("Regenerate CAPA", use_container_width=True)
    with col3:
        approve_clicked = st.button(
            "Approve CAPA",
            type="primary",
            disabled=not (
                st.session_state.capa_validated
                and bool(st.session_state.capa_text)
            ),
            use_container_width=True,
        )

    if "capa_feedback_input" not in st.session_state:
        st.session_state.capa_feedback_input = st.session_state.capa_feedback
    st.text_area(
        "Reviewer Feedback (Optional)",
        key="capa_feedback_input",
        height=120,
        placeholder="Provide precise guidance for CAPA regeneration.",
    )

    if validate_clicked:
        if not st.session_state.capa_text:
            st.error("CAPA content cannot be empty.")
        else:
            st.session_state.capa_flags = CAPAValidator().validate(
                st.session_state.incident_text, st.session_state.capa_text
            )
            st.session_state.capa_validated = True
            st.rerun()

    if regenerate_clicked:
        st.session_state.capa_feedback = st.session_state.capa_feedback_input.strip()
        capa = format_capa_for_review(
            generate_capa_from_rca(
                st.session_state.rca_text,
                st.session_state.capa_feedback,
            )
        )
        invalidate_capa()
        st.session_state.pending_capa_editor = capa
        st.rerun()

    if approve_clicked:
        st.session_state.capa_approved = True
        navigate("Final Report")
        st.rerun()

    if st.session_state.capa_validated:
        st.divider()
        render_flags(st.session_state.capa_flags, "CAPA")


def final_report() -> None:
    st.header("Final Report")
    st.caption("Review the approved content and generate the controlled DOCX report.")
    if not (st.session_state.rca_approved and st.session_state.capa_approved):
        st.warning("Approve both the RCA and CAPA before generating the final report.")
        return

    for title, content in (
        ("Incident", st.session_state.incident_text),
        ("Approved RCA", st.session_state.rca_text),
        ("Approved CAPA", st.session_state.capa_text),
    ):
        with st.expander(title, expanded=True):
            st.text(content)

    try:
        document = generate_docx(
            incident_text=st.session_state.incident_text,
            rca_text=st.session_state.rca_text,
            capa_text=st.session_state.capa_text,
            problem_description=st.session_state.problem_description,
            business_impact=st.session_state.business_impact,
            investigation_timeline=st.session_state.timeline,
        )
        data = document.getvalue() if isinstance(document, BytesIO) else document
        if not isinstance(data, bytes):
            raise TypeError("DOCX generator returned an unsupported response type.")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "Generate DOCX",
            data=data,
            file_name="Generated_Report.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            type="primary",
            use_container_width=True,
        )
    except Exception as exc:
        st.error(f"DOCX generation is unavailable: {exc}")


st.set_page_config(
    page_title="IT Incident Report Generator",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
      .block-container {max-width: 1280px; padding-top: 1.5rem;}
      .app-header {background: linear-gradient(120deg,#12345b,#176b87);
        border-radius:12px;color:white;margin-bottom:1.75rem;padding:1.6rem 2rem;
        box-shadow:0 8px 24px rgba(18,52,91,.16)}
      .app-title {font-size:2rem;font-weight:700}
      .app-subtitle {font-size:1rem;margin-top:.45rem;opacity:.92}
      .finding-card {border-left:5px solid;border-radius:8px;margin:.75rem 0;
        padding:.9rem 1rem}
      .finding-heading {font-weight:700;margin-bottom:.3rem}
      .finding-high {background:#fff1f2;border-color:#be123c}
      .finding-medium {background:#fff7ed;border-color:#c2410c}
      .finding-low {background:#eff6ff;border-color:#1d4ed8}
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_state()
restore_editor_state()
apply_pending_editor_updates()
render_sidebar()
render_header()

if st.session_state.current_page == "Incident Intake":
    incident_intake()
elif st.session_state.current_page == "RCA Review":
    rca_review()
elif st.session_state.current_page == "CAPA Review":
    capa_review()
else:
    final_report()
