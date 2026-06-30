import re

def extract_words(text):
    """
    Extract normalized words from text.
    """
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]+\b", text.lower())
    return set(words)


def find_new_terms(source_text, generated_text):
    """
    Find words appearing in generated output but not source.
    """
    source_words = extract_words(source_text)
    generated_words = extract_words(generated_text)

    ignore = {
        "corrective",
        "preventive",
        "actions",
        "lessons",
        "learned",
        "root",
        "cause",
        "analysis",
        "monitoring",
        "review",
        "system",
        "service",
    }

    return sorted(
        list(
            generated_words -
            source_words -
            ignore
        )
    )


def normalize_rca(text: str) -> str:
    """
    Normalize RCA text headings to canonical format:
    - Root Cause
    - Why 1 ... Why 5
    Ensures headings are on their own lines and properly spaced.
    """
    if not text:
        return ""
    
    lines = text.splitlines()
    processed_lines = []
    
    rc_pattern = re.compile(r'^\s*#*\s*\*?\*?\s*(Root\s+Cause\s+Summary|Root\s+Causes?)\s*\*?\*?\s*:?\s*\*?\*?\s*$', re.I)
    why_pattern = re.compile(r'^\s*#*\s*\*?\*?\s*Why\s+([1-5])\s*\*?\*?\s*(?:[:\-\.\s]\s*\*?\*?(.*))?$', re.I)
    
    allowed_section_active = False
    disallowed_pattern = re.compile(
        r'^\s*#*\s*\*?\*?\s*(Problem\s+Description|Business\s+Impact|Investigation\s+Timeline|Incident|Reviewer\s+Feedback)\s*\*?\*?\s*:?\s*\*?\*?\s*$',
        re.I
    )

    for line in lines:
        line_str = line.strip()
        
        # Check Root Cause
        if rc_pattern.match(line_str):
            processed_lines.append("Root Cause")
            allowed_section_active = True
            continue
            
        # Check Why 1-5
        why_match = why_pattern.match(line_str)
        if why_match:
            why_num = why_match.group(1)
            remaining = why_match.group(2)
            processed_lines.append(f"Why {why_num}")
            allowed_section_active = True
            if remaining and remaining.strip():
                processed_lines.append(remaining.strip())
            continue
            
        if disallowed_pattern.match(line_str):
            allowed_section_active = False
            continue
            
        if allowed_section_active:
            processed_lines.append(line)
        
    result = "\n".join(processed_lines)
    
    # Normalize spacing only
    result = re.sub(r'\n{3,}', '\n\n', result)

    # Ensure headings start on a new line
    for i in range(1, 6):
        result = re.sub(
            rf'\s*Why {i}\s*',
            f'\n\nWhy {i}\n',
            result,
        )

    result = re.sub(
        r'(?m)^\s*Root Cause\s*$',
        '\n\nRoot Cause\n',
        result,
    )

    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def normalize_capa(text: str) -> str:
    """
    Normalize CAPA text headings to canonical format:
    - Corrective Action
    - Preventive Action
    - Lessons Learned
    Ensures headings are on their own lines and properly spaced.
    """
    if not text:
        return ""
        
    lines = text.splitlines()
    processed_lines = []
    
    ca_pattern = re.compile(r'^\s*#*\s*\*?\*?\s*(Corrective\s+Actions?)\s*(?:[:\-\.\s]\s*\*?\*?(.*))?$', re.I)
    pa_pattern = re.compile(r'^\s*#*\s*\*?\*?\s*(Preventive\s+Actions?)\s*(?:[:\-\.\s]\s*\*?\*?(.*))?$', re.I)
    ll_pattern = re.compile(r'^\s*#*\s*\*?\*?\s*(Lessons?\s+Learned)\s*(?:[:\-\.\s]\s*\*?\*?(.*))?$', re.I)
    
    for line in lines:
        line_str = line.strip()
        
        # Check Corrective Action
        ca_match = ca_pattern.match(line_str)
        if ca_match:
            remaining = ca_match.group(2)
            processed_lines.append("Corrective Action")
            if remaining and remaining.strip():
                processed_lines.append(remaining.strip())
            continue
            
        # Check Preventive Action
        pa_match = pa_pattern.match(line_str)
        if pa_match:
            remaining = pa_match.group(2)
            processed_lines.append("Preventive Action")
            if remaining and remaining.strip():
                processed_lines.append(remaining.strip())
            continue
            
        # Check Lessons Learned
        ll_match = ll_pattern.match(line_str)
        if ll_match:
            remaining = ll_match.group(2)
            processed_lines.append("Lessons Learned")
            if remaining and remaining.strip():
                processed_lines.append(remaining.strip())
            continue
            
        processed_lines.append(line)
        
    result = "\n".join(processed_lines)
    
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()
