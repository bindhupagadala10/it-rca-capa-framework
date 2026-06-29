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
from src.inference.mock_inference import generate_mock_rca as generate_rca, generate_mock_capa as generate_capa
# from src.inference.rca_inference import generate_rca; from src.inference.capa_inference import generate_capa
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
    
    # In-progress/state-update flags
    "rca_generating": False,
    "rca_regenerating": False,
    "rca_validating": False,
    "capa_generating": False,
    "capa_regenerating": False,
    "capa_validating": False,
    "capa_approved_clicked": False,
    
    # Debug/Demo metrics
    "rca_generation_time": None,
    "rca_validation_time": None,
    "capa_generation_time": None,
    "capa_validation_time": None,
    "current_loaded_model": "None (GPU Free)",
    
    # Caching
    "docx_data": None,
}


def check_is_mock() -> bool:
    return generate_rca.__module__.endswith("mock_inference")


def load_rca_model_wrapper() -> None:
    if check_is_mock():
        st.session_state.current_loaded_model = "Mock Inference Engine"
    else:
        st.session_state.current_loaded_model = "Qwen2.5-3B-Instruct (RCA)"
        try:
            from src.inference.qwen_inference import load_qwen
            load_qwen()
        except Exception as e:
            print(f"Error loading Qwen: {e}")


def unload_rca_model_wrapper() -> None:
    if check_is_mock():
        st.session_state.current_loaded_model = "Mock Inference Engine"
    else:
        st.session_state.current_loaded_model = "None (GPU Free)"
        try:
            from src.inference.qwen_inference import unload_qwen
            unload_qwen()
        except Exception as e:
            print(f"Error unloading Qwen: {e}")


def load_capa_model_wrapper() -> None:
    if check_is_mock():
        st.session_state.current_loaded_model = "Mock Inference Engine"
    else:
        st.session_state.current_loaded_model = "Mistral-7B-Instruct (CAPA)"
        try:
            from src.inference.mistral_inference import load_mistral
            load_mistral()
        except Exception as e:
            print(f"Error loading Mistral: {e}")


def unload_capa_model_wrapper() -> None:
    if check_is_mock():
        st.session_state.current_loaded_model = "Mock Inference Engine"
    else:
        st.session_state.current_loaded_model = "None (GPU Free)"
        try:
            from src.inference.mistral_inference import unload_mistral
            unload_mistral()
        except Exception as e:
            print(f"Error unloading Mistral: {e}")


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value
    
    if check_is_mock():
        st.session_state.current_loaded_model = "Mock Inference Engine"


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
    if not following_headings:
        match = re.search(
            rf"(?ims)^\s*{re.escape(heading)}\s*$\s*(.*)\Z",
            text,
        )
        return match.group(1).strip() if match else ""

    end_pattern = "|".join(re.escape(item) for item in following_headings)
    match = re.search(
        rf"(?ims)^\s*{re.escape(heading)}\s*$\s*(.*?)"
        rf"(?=^\s*(?:{end_pattern})\s*$|\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def format_rca_for_review(generated_text: str) -> str:
    headings = tuple([f"Why {index}" for index in range(1, 6)])
    root_cause = section_text(generated_text, "Root Cause", headings)
    sections = [f"Root Cause\n\n{root_cause}"]

    for index in range(1, 6):
        heading = f"Why {index}"
        following = tuple(f"Why {item}" for item in range(index + 1, 6))
        value = section_text(generated_text, heading, following)
        sections.append(f"{heading}\n\n{value}")

    return "\n\n".join(sections).strip()


def format_capa_for_review(generated_text: str) -> str:
    headings = (
        "Corrective Action",
        "Preventive Action",
        "Ownership",
        "Monitoring",
        "Lessons Learned",
        "Reviewer Feedback",
    )
    sections = []
    for index, heading in enumerate(headings[:-1]):
        value = section_text(generated_text, heading, headings[index + 1 :])
        if heading == "Lessons Learned" or value:
            sections.append(f"{heading}\n\n{value}")
    return "\n\n".join(sections).strip()


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
    st.session_state.docx_data = None


def invalidate_capa() -> None:
    st.session_state.capa_validated = False
    st.session_state.capa_approved = False
    st.session_state.capa_flags = []
    st.session_state.docx_data = None


def render_stage_status(stage_name: str, status: str) -> None:
    if status == "Completed":
        st.sidebar.success(f"{stage_name}: Completed", icon="✅")
    elif status == "Generating":
        st.sidebar.warning(f"{stage_name}: Generating...", icon="🔄")
    else:
        st.sidebar.info(f"{stage_name}: Pending", icon="⏳")


def render_sidebar(is_busy: bool) -> None:
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
        disabled=is_busy,
    )
    
    if selected != st.session_state.current_page:
        if selected in allowed_pages:
            st.session_state.current_page = selected
            st.rerun()
        else:
            st.toast(f"🔒 {selected} is locked. Complete previous steps first.", icon="🔒")
            st.rerun()
            
    st.sidebar.divider()
    
    # Validation Rules Reference
    with st.sidebar.expander("Validation Rules Reference"):
        st.markdown("""
        **RCA Validation Rules:**
        * **RCA001**: No unsupported technology references.
        * **RCA002**: Avoid generic root cause phrases.
        * **RCA003**: Length must be at least 50 words.
        * **RCA004**: Must contain a "Root Cause" section.
        * **RCA005**: Must contain all 5 "Why" levels.
        * **RCA006**: Strong keyword overlap with incident context.
        
        **CAPA Validation Rules:**
        * **CAPA001**: No unsupported technology references.
        * **CAPA002**: Must contain monitoring/detection improvements.
        * **CAPA003**: Must specify an owner or responsible team.
        * **CAPA004**: Avoid non-actionable statements.
        * **CAPA005**: Avoid potential boilerplate language.
        """)
        
    st.sidebar.divider()
    st.sidebar.subheader("Workflow Progress")

    # 1. Incident Details status
    incident_status = "Completed" if bool(st.session_state.incident_text.strip()) else "Pending"
    render_stage_status("Incident Details", incident_status)
    
    # 2. RCA status
    if st.session_state.rca_approved:
        rca_status = "Completed"
    elif st.session_state.rca_generating or st.session_state.rca_regenerating or st.session_state.rca_validating:
        rca_status = "Generating"
    else:
        rca_status = "Pending"
    render_stage_status("RCA", rca_status)
    
    # 3. CAPA status
    if st.session_state.capa_approved:
        capa_status = "Completed"
    elif st.session_state.capa_generating or st.session_state.capa_regenerating or st.session_state.capa_validating or st.session_state.capa_approved_clicked:
        capa_status = "Generating"
    else:
        capa_status = "Pending"
    render_stage_status("CAPA", capa_status)
    
    # 4. Report status
    report_status = "Completed" if (st.session_state.rca_approved and st.session_state.capa_approved) else "Pending"
    render_stage_status("Report", report_status)

    # System Metrics Display
    st.sidebar.divider()
    st.sidebar.subheader("System Metrics")
    st.sidebar.markdown(f"**Loaded Model:** `{st.session_state.current_loaded_model}`")
    
    if st.session_state.rca_generation_time is not None:
        st.sidebar.markdown(f"⏱️ RCA Gen: `{st.session_state.rca_generation_time:.2f}s`")
    if st.session_state.rca_validation_time is not None:
        st.sidebar.markdown(f"⏱️ RCA Val: `{st.session_state.rca_validation_time:.2f}s`")
    if st.session_state.capa_generation_time is not None:
        st.sidebar.markdown(f"⏱️ CAPA Gen: `{st.session_state.capa_generation_time:.2f}s`")
    if st.session_state.capa_validation_time is not None:
        st.sidebar.markdown(f"⏱️ CAPA Val: `{st.session_state.capa_validation_time:.2f}s`")

    # Start New Incident (Session Reset)
    st.sidebar.divider()
    if st.sidebar.button("Start New Incident", type="secondary", use_container_width=True, disabled=is_busy):
        unload_rca_model_wrapper()
        unload_capa_model_wrapper()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_state()
        st.rerun()


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


def render_validation_summary(flags: list[dict], total_rules: int) -> None:
    critical_count = sum(1 for f in flags if str(f.get("severity", "")).upper() == "HIGH")
    warning_count = sum(1 for f in flags if str(f.get("severity", "")).upper() in ("MEDIUM", "LOW"))
    passed_count = total_rules - (critical_count + warning_count)
    
    st.markdown("#### Validation Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rules Checked", total_rules)
    col2.metric("Passed", passed_count)
    col3.metric("Warnings", warning_count)
    col4.metric("Critical", critical_count)


def render_flags(flags: list[dict], artifact: str) -> None:
    total_rules = 6 if artifact == "RCA" else 5
    st.markdown("---")
    render_validation_summary(flags, total_rules)
    st.markdown("---")
    
    st.subheader("Detailed Findings")
    if not flags:
        st.markdown("### 🟢 PASS")
        st.success(f"{artifact} validation passed with no findings.", icon="✅")
        return

    st.error(
        f"{artifact} validation returned {len(flags)} finding(s). "
        "Resolve findings and validate again before approval."
    )
    for flag in flags:
        severity = str(flag.get("severity", "UNKNOWN")).upper()
        badge = {
            "HIGH": "🔴 HIGH",
            "MEDIUM": "🟠 MEDIUM",
            "LOW": "🟡 LOW",
        }.get(severity, f"⚪ {severity}")
        
        css_class = {
            "HIGH": "finding-high",
            "MEDIUM": "finding-medium",
            "LOW": "finding-low",
        }.get(severity, "finding-medium")
        
        st.markdown(
            f"""
            <div class="finding-card {css_class}">
              <div class="finding-heading" style="display: flex; justify-content: space-between;">
                <span>{escape(str(flag.get("id", "VALIDATION")))}</span>
                <span style="font-weight: bold;">{badge}</span>
              </div>
              <div style="margin-top: 5px;">{escape(str(flag.get("message", "Validation finding")))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def incident_intake(is_busy: bool) -> None:
    st.header("Incident Intake")
    st.caption("Capture the verified incident facts used to generate the RCA.")

    if st.session_state.get("rca_generating", False):
        st.info("Generating Root Cause Analysis... Please wait.")
        with st.spinner("Generating RCA using Qwen model..."):
            incident = (
                "Problem Description\n"
                f"{st.session_state.problem_description_input.strip()}\n\n"
                "Business Impact\n"
                f"{st.session_state.business_impact_input.strip()}\n\n"
                "Investigation Timeline\n"
                f"{st.session_state.timeline_input.strip()}"
            )
            st.session_state.problem_description = st.session_state.problem_description_input.strip()
            st.session_state.business_impact = st.session_state.business_impact_input.strip()
            st.session_state.timeline = st.session_state.timeline_input.strip()
            st.session_state.incident_text = incident
            
            # Record generation time and load info
            load_rca_model_wrapper()
            start_time = datetime.now()
            rca = format_rca_for_review(generate_rca(incident))
            st.session_state.rca_generation_time = (datetime.now() - start_time).total_seconds()
            
            st.session_state.rca_text = rca
            st.session_state.rca_editor = rca
            st.session_state.rca_generated = True
            st.session_state.rca_generating = False
            invalidate_rca()
            navigate("RCA Review")
        st.rerun()

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
        if st.button("Continue to RCA Review", type="primary", use_container_width=True, disabled=is_busy):
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
                disabled=is_busy,
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
            disabled=is_busy,
        )
        st.text_area(
            "Investigation Timeline *",
            key="timeline_input",
            height=180,
            placeholder=(
                "09:00 - Alert received\n09:05 - Incident bridge opened\n"
                "09:20 - Technical team engaged\n09:45 - Service restored"
            ),
            disabled=is_busy,
        )

    if st.button("Generate RCA", type="primary", use_container_width=True, disabled=is_busy):
        errors = validate_incident_input(
            st.session_state.problem_description_input,
            st.session_state.business_impact_input,
            st.session_state.timeline_input,
        )
        if errors:
            st.error("Correct the following validation errors before continuing:")
            for error in errors:
                st.error(error, icon="⚠️")
        else:
            # Immediate status update before generation begins
            st.session_state.rca_generating = True
            st.rerun()


def rca_review(is_busy: bool) -> None:
    st.header("RCA Review")
    st.caption("Review, validate, refine, and approve the Root Cause Analysis.")
    if not st.session_state.rca_generated:
        st.warning("Generate an RCA from Incident Intake before starting RCA review.")
        if st.button("Go to Incident Intake", type="primary", disabled=is_busy):
            navigate("Incident Intake")
            st.rerun()
        return

    # Execution Blocks for Spinner / State update
    if st.session_state.get("rca_regenerating", False):
        st.info("Regenerating Root Cause Analysis... Please wait.")
        with st.spinner("Regenerating RCA using Qwen model..."):
            feedback_val = st.session_state.get("rca_feedback", "").strip()
            start_time = datetime.now()
            rca = format_rca_for_review(
                generate_rca(
                    st.session_state.incident_text,
                    feedback_val,
                )
            )
            st.session_state.rca_generation_time = (datetime.now() - start_time).total_seconds()
            invalidate_rca()
            st.session_state.pending_rca_editor = rca
            st.session_state.rca_regenerating = False
        st.rerun()

    if st.session_state.get("rca_validating", False):
        st.info("Validating Root Cause Analysis... Please wait.")
        with st.spinner("Validating RCA..."):
            start_time = datetime.now()
            st.session_state.rca_flags = validate_rca(
                st.session_state.incident_text, st.session_state.rca_text
            )
            st.session_state.rca_validation_time = (datetime.now() - start_time).total_seconds()
            st.session_state.rca_validated = True
            st.session_state.rca_validating = False
        st.rerun()

    if st.session_state.get("capa_generating", False):
        st.info("Unloading Qwen and generating CAPA... Please wait.")
        with st.spinner("Switching AI models..."):
            unload_rca_model_wrapper()
            load_capa_model_wrapper()

        with st.spinner("Generating CAPA using Mistral model..."):
            start_time = datetime.now()
            capa = format_capa_for_review(
                generate_capa(
                    st.session_state.incident_text,
                    st.session_state.rca_text,
                )
            )
            st.session_state.capa_generation_time = (datetime.now() - start_time).total_seconds()
            st.session_state.capa_text = capa
            st.session_state.capa_editor = capa
            st.session_state.capa_generated = True
            st.session_state.capa_validated = False
            st.session_state.capa_approved = False
            st.session_state.capa_flags = []
            st.session_state.capa_generating = False
            navigate("CAPA Review")
        st.rerun()

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
        if st.button("Continue to CAPA Review", type="primary", use_container_width=True, disabled=is_busy):
            navigate("CAPA Review")
            st.rerun()
        return

    st.text_area(
        "Root Cause Analysis",
        key="rca_editor",
        height=430,
        on_change=invalidate_rca,
        disabled=is_busy,
    )
    st.session_state.rca_text = st.session_state.rca_editor.strip()

    col1, col2, col3 = st.columns(3)
    with col1:
        validate_clicked = st.button("Validate RCA", use_container_width=True, disabled=is_busy)
    with col2:
        regenerate_clicked = st.button("Regenerate RCA", use_container_width=True, disabled=is_busy)
    with col3:
        approve_clicked = st.button(
            "Approve RCA",
            type="primary",
            disabled=not (
                st.session_state.rca_validated
                and bool(st.session_state.rca_text)
            ) or is_busy,
            use_container_width=True,
        )

    st.text_area(
        "Reviewer Feedback (Optional)",
        key="rca_feedback",
        height=120,
        placeholder="Provide precise guidance for RCA regeneration.",
        disabled=is_busy,
    )

    if validate_clicked:
        if not st.session_state.rca_text:
            st.error("RCA content cannot be empty.")
        else:
            st.session_state.rca_validating = True
            st.rerun()

    if regenerate_clicked:
        st.session_state.rca_regenerating = True
        st.rerun()
    if approve_clicked:

        st.session_state.rca_text = st.session_state.rca_editor.strip()

        st.session_state.rca_approved = True
        st.session_state.capa_generating = True

        st.rerun()

    if st.session_state.rca_validated:
        render_flags(st.session_state.rca_flags, "RCA")


def capa_review(is_busy: bool) -> None:
    st.header("CAPA Review")
    st.caption("Review, validate, refine, and approve the action plan.")
    if not st.session_state.rca_approved:
        st.warning("Approve the RCA before starting CAPA review.")
        if st.button("Go to RCA Review", type="primary", disabled=is_busy):
            navigate("RCA Review")
            st.rerun()
        return
    if not st.session_state.capa_generated:
        st.warning("CAPA content has not been generated.")
        return

    # Execution Blocks for Spinner / State update
    if st.session_state.get("capa_regenerating", False):
        st.info("Regenerating CAPA... Please wait.")
        with st.spinner("Regenerating CAPA using Mistral model..."):
            feedback_val = st.session_state.get("capa_feedback", "").strip()
            start_time = datetime.now()
            capa = format_capa_for_review(
                generate_capa(
                    st.session_state.incident_text,
                    st.session_state.rca_text,
                    feedback_val,
                )
            )
            st.session_state.capa_generation_time = (datetime.now() - start_time).total_seconds()
            invalidate_capa()
            st.session_state.pending_capa_editor = capa
            st.session_state.capa_regenerating = False
        st.rerun()

    if st.session_state.get("capa_validating", False):
        st.info("Validating CAPA... Please wait.")
        with st.spinner("Validating CAPA..."):
            start_time = datetime.now()
            st.session_state.capa_flags = CAPAValidator().validate(
                st.session_state.incident_text, st.session_state.capa_text
            )
            st.session_state.capa_validation_time = (datetime.now() - start_time).total_seconds()
            st.session_state.capa_validated = True
            st.session_state.capa_validating = False
        st.rerun()

    if st.session_state.get("capa_approved_clicked", False):
        st.info("Unloading Mistral model... Please wait.")
        with st.spinner("Unloading Mistral model from GPU..."):
            unload_capa_model_wrapper()
            st.session_state.capa_approved = True
            st.session_state.capa_approved_clicked = False
            navigate("Final Report")
        st.rerun()

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
        if st.button("Continue to Final Report", type="primary", use_container_width=True, disabled=is_busy):
            navigate("Final Report")
            st.rerun()
        return

    st.text_area(
        "Corrective and Preventive Action Plan",
        key="capa_editor",
        height=430,
        on_change=invalidate_capa,
        disabled=is_busy,
    )
    st.session_state.capa_text = st.session_state.capa_editor.strip()

    col1, col2, col3 = st.columns(3)
    with col1:
        validate_clicked = st.button("Validate CAPA", use_container_width=True, disabled=is_busy)
    with col2:
        regenerate_clicked = st.button("Regenerate CAPA", use_container_width=True, disabled=is_busy)
    with col3:
        approve_clicked = st.button(
            "Approve CAPA",
            type="primary",
            disabled=not (
                st.session_state.capa_validated
                and bool(st.session_state.capa_text)
            ) or is_busy,
            use_container_width=True,
        )

    st.text_area(
        "Reviewer Feedback (Optional)",
        key="capa_feedback",
        height=120,
        placeholder="Provide precise guidance for CAPA regeneration.",
        disabled=is_busy,
    )

    if validate_clicked:
        if not st.session_state.capa_text:
            st.error("CAPA content cannot be empty.")
        else:
            st.session_state.capa_validating = True
            st.rerun()

    if regenerate_clicked:
        st.session_state.capa_regenerating = True
        st.rerun()

    if approve_clicked:

        st.session_state.capa_text = st.session_state.capa_editor.strip()

        st.session_state.capa_approved_clicked = True

        st.rerun()    

    if st.session_state.capa_validated:
        render_flags(st.session_state.capa_flags, "CAPA")


def final_report(is_busy: bool) -> None:
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

    # 11. DOCX Generation with Spinner
    if "docx_data" not in st.session_state or st.session_state.docx_data is None:
        with st.spinner("Generating DOCX report from template..."):
            try:
                document = generate_docx(
                    incident_text=st.session_state.incident_text,
                    rca_text=st.session_state.rca_text,
                    capa_text=st.session_state.capa_text,
                    problem_description=st.session_state.problem_description,
                    business_impact=st.session_state.business_impact,
                    investigation_timeline=st.session_state.timeline,
                )
                st.session_state.docx_data = document.getvalue() if isinstance(document, BytesIO) else document
            except Exception as exc:
                st.error(f"DOCX generation failed: {exc}")
                st.session_state.docx_data = None

    if st.session_state.docx_data is not None:
        st.download_button(
            "Generate DOCX",
            data=st.session_state.docx_data,
            file_name="Generated_Report.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            type="primary",
            use_container_width=True,
            disabled=is_busy,
        )


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

# Define overall busy status
is_busy = (
    st.session_state.get("rca_generating", False)
    or st.session_state.get("rca_regenerating", False)
    or st.session_state.get("rca_validating", False)
    or st.session_state.get("capa_generating", False)
    or st.session_state.get("capa_regenerating", False)
    or st.session_state.get("capa_validating", False)
    or st.session_state.get("capa_approved_clicked", False)
)

render_sidebar(is_busy)
render_header()

if st.session_state.current_page == "Incident Intake":
    incident_intake(is_busy)
elif st.session_state.current_page == "RCA Review":
    rca_review(is_busy)
elif st.session_state.current_page == "CAPA Review":
    capa_review(is_busy)
else:
    final_report(is_busy)
