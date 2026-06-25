import re

KNOWN_TECH = {
    "kafka",
    "terraform",
    "prometheus",
    "grafana",
    "splunk",
    "datadog",
    "kubernetes",
    "ansible",
    "jenkins",
    "sonarqube",
    "rabbitmq",
    "redis",
    "nginx",
    "apache",
    "oauth",
    "jwt",
    "ldap",
    "oracle",
    "mysql",
    "postgresql",
    "mongodb",
    "nexus",
    "npm",
    "docker",
    "ci/cd",
}

def extract_technologies(text):

    text = text.lower()

    found = set()

    for tech in KNOWN_TECH:
        if tech.lower() in text:
            found.add(tech)

    return found


def find_introduced_technologies(
    source_text,
    generated_text
):

    source = extract_technologies(source_text)

    generated = extract_technologies(
        generated_text
    )

    return sorted(
        list(generated - source)
    )