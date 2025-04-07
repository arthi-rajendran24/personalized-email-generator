import streamlit as st
import pandas as pd
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import re
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    filename='user_access.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize Ollama LLM
if 'llm' not in st.session_state:
    st.session_state.llm = Ollama(
        base_url="http://localhost:11434",
        model="llama3.2:3b",
        verbose=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )

# Define product info
ITOM = {
    "description": """ManageEngine Product Suite for IT Operations Management: A Briefing
This document reviews the main themes and key features of ManageEngine's IT operations management product suite based on excerpts from their website. It focuses on five key products: Applications Manager, OpUtils, OpManager Plus, NetFlow Analyzer, and Network Configuration Manager.

Overarching Themes:

Full-Stack Observability: A consistent theme across the product suite is the emphasis on providing full-stack observability. This means enabling IT teams to monitor and manage all layers of the IT infrastructure, from applications down to the network and hardware, in a unified manner.
AIOps: ManageEngine leverages AI and ML capabilities across its products to offer intelligent insights, anomaly detection, and proactive problem resolution.
Unified Platform: The suite promotes a unified platform approach, allowing seamless integration between different products to streamline IT operations and break down silos.
Meeting Compliance Standards: Several products highlight compliance features, especially for critical standards like PCI, SOX, HIPAA, and FIPS 140-2, crucial for organizations in regulated industries.
Addressing Diverse Needs: The suite caters to various stakeholders within IT operations, including NetOps, SecOps, ITOps, DevOps, SREs, and business leaders, with features designed to address their specific needs and pain points.
Scalability and Flexibility: ManageEngine offers different editions of its products, catering to organizations of varying sizes and resource requirements, from small businesses to large enterprises with distributed IT environments.
Product Deep Dive:

1. Applications Manager:

Focus: Application performance monitoring and observability.
Key Features:Monitors 150+ technologies, including Java, .NET, Node.js, and cloud platforms like AWS, Azure, and GCP.
Offers code-level insights, distributed transaction tracing, and application service maps.
Includes real user monitoring (RUM) and synthetic transaction monitoring.
Provides AI-assisted smart alerts and advanced analytics for proactive issue resolution.
Value Proposition:"Enables IT operations teams to proactively detect issues and troubleshoot faster with accurate root cause analysis."
"Helps DevOps/SRE teams correlate performance changes with code commits and builds."
2. OpUtils:

Focus: IP address and switch port management.
Key Features:Enables advanced IP scanning for IPv4 and IPv6 subnets.
Offers switch port mapping, rogue device detection, and bandwidth monitoring.
Provides tools for Cisco configuration file management and SNMP device monitoring.
Includes diagnostic tools for checking system availability, route, and health.
Value Proposition:"Managing switch ports and IP addresses have never been so easy!"
Complements existing management tools by offering real-time monitoring and troubleshooting capabilities.
3. OpManager Plus:

Focus: Unified IT operations platform for full-stack observability.
Key Features:Combines network, server, application, bandwidth, configuration, and firewall management into a single platform.
Offers in-depth monitoring for 10,000+ devices and supports 2000+ metrics.
Includes advanced capabilities like network traffic analysis, configuration compliance auditing, and security threat detection.
Leverages AI/ML for predictive analytics, anomaly detection, and automated remediation workflows.
Value Proposition:"Ensures the availability of business-critical network devices and applications and empowers NetOps, DevOps, SRE's and IT leaders by turning raw data into actionable insights."
"Bridges IT teams together - the observability way" by enabling collaboration and shared visibility across different teams.
4. NetFlow Analyzer:

Focus: Network traffic analysis and bandwidth monitoring.
Key Features:Supports major flow technologies like NetFlow, sFlow, IPFIX, J-Flow, and AppFlow.
Provides real-time bandwidth monitoring with detailed traffic analysis.
Offers network forensics and security analysis to detect threats and anomalies.
Enables app-centric monitoring and traffic shaping to optimize bandwidth usage.
Includes capacity planning and billing features.
Value Proposition:"A complete traffic analytics tool, that leverages flow technologies to provide real time visibility into the network bandwidth performance."
"Future-proof your ever-evolving IT network with NetFlow Analyzer and keep bandwidth issues at bay, anyday."
5. Network Configuration Manager:

Focus: Automated network configuration and change management (NCCM).
Key Features:Automates configuration backups, change tracking, and compliance auditing.
Enables real-time change management with instant notifications and rollback capabilities.
Offers firmware vulnerability management and remote firmware upgrade.
Provides distributed configuration management for large networks.
Value Proposition:"Helps automate and take total control of the entire life cycle of device configuration management."
"Make your network disaster-proof with improved visibility into your network infrastructure."
Conclusion:

ManageEngine's product suite presents a comprehensive solution for organizations seeking to gain control over their IT operations. By emphasizing full-stack observability, leveraging AI/ML capabilities, and offering a unified platform, ManageEngine empowers IT teams to optimize performance, enhance security, and ensure business continuity in today's complex and evolving IT landscapes.""",
    "features": [
        "Network monitoring",
        "NetFlow analysis",
        "NetPath analysis",
        "Configuration and change management",
        "IP address and switch-port mapping",
        "Hybrid network monitoring",
        "Enterprise server management",
        "Virtual server monitoring",
        "Data center management",
        "Application performance monitoring",
        "Cloud monitoring"
    ]
}

# Define CTA options
CTA_OPTIONS = {
    "Demo Request": "Would you be open to a quick demo this week to see how OpManager Plus can streamline your endpoint management?",
    "Discovery Call": "Would you have 15 minutes this week to discuss how we can help strengthen your endpoint security?",
    "Free Trial": "I'd be happy to set you up with a free trial of OpManager Plus so you can see the benefits firsthand.",
    "Resource Share": "I can share some relevant case studies showing how similar organizations have transformed their endpoint management.",
    "Quick Chat": "Are you available for a brief chat to explore how we can help address your endpoint management needs?"
}


# Email verification functions
def validate_zoho_email(email):
    """Validate if the email is a valid zohocorp.com email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@zohocorp\.com$'
    return bool(re.match(pattern, email))


def log_user_access(email):
    """Log user access with timestamp and email"""
    logging.info(f"Tool accessed by: {email}")


def initialize_session_state():
    """Initialize session state variables"""
    if 'email_verified' not in st.session_state:
        st.session_state.email_verified = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'template' not in st.session_state:
        st.session_state.template = """You are an expert B2B email writer with extensive experience in crafting highly personalized, engaging emails.
Generate exactly three paragraphs of body text (no greeting, no subject line, no extra lines, no signature, no placeholder text for CTA, etc.), and ensure the text directly addresses the recipient using second-person pronouns like you, your, yourself.

Do not write in third person.

Incorporate this custom context: {custom_text}

Generate for:
First Name: {first_name}
Last Name: {last_name}
Company: {company}
Role: {role}
Industry: {industry}
Country: {country}

Product Information:
Name: OpManager Plus
Description: {product_description}
Features: {product_features}

Selected CTA: {cta}

Follow these guidelines:

Write naturally as if you're a human sales professional
Speak directly to the recipient, emphasizing their perspective and experience
Reference their specific role, industry, and location meaningfully
Avoid generic statements and obvious templated language
Make relevant industry-specific observations or pain points
Keep the tone professional but conversational
Do not mention AI or automated generation
Seamlessly incorporate the custom context provided
End with the provided CTA, but make it feel natural
Generate exactly three paragraphs:

Establish a personal connection and relate to their role, industry, or specific challenges (incorporate custom text if relevant).
Present the value proposition of OpManager Plus by addressing their specific needs or industry pain points (incorporate custom text if relevant).
Demonstrate how OpManager Plus can benefit their role and organization, concluding with the CTA (incorporate custom text if relevant).
    """
        st.session_state.prompt = PromptTemplate(
            input_variables=["first_name", "last_name", "company", "role", "industry",
                             "country", "product_description", "product_features", "cta", "custom_text"],
            template=st.session_state.template,
        )


def email_verification_form():
    """Display email verification form"""
    st.sidebar.markdown("### User Verification")
    email = st.sidebar.text_input("Enter your Zoho email:",
                                  value=st.session_state.user_email,
                                  placeholder="username@zohocorp.com")

    if email:
        if validate_zoho_email(email):
            if not st.session_state.email_verified or email != st.session_state.user_email:
                st.session_state.email_verified = True
                st.session_state.user_email = email
                log_user_access(email)
                st.sidebar.success("Email verified!")
            return True
        else:
            st.sidebar.error("Please enter a valid zohocorp.com email")
            st.session_state.email_verified = False
            return False
    return False


def parse_email_paragraphs(email_content):
    """Split email content into three paragraphs."""
    paragraphs = email_content.strip().split('\n\n')
    while len(paragraphs) < 3:
        paragraphs.append("")
    return paragraphs[:3]


def generate_bulk_emails(df, cta_text, custom_text):
    """Generate personalized emails for multiple recipients and add paragraphs as new columns."""
    df = df.copy()
    df['Paragraph1'] = ""
    df['Paragraph2'] = ""
    df['Paragraph3'] = ""

    progress_bar = st.progress(0)
    total_rows = len(df)

    for idx, row in df.iterrows():
        prompt = st.session_state.prompt.format(
            first_name=row['First Name'],
            last_name=row['Last Name'],
            company=row['Company'],
            role=row['Role'],
            industry=row['Industry'],
            country=row['Country'],
            product_description=ITOM['description'],
            product_features=", ".join(ITOM['features']),
            cta=cta_text,
            custom_text=custom_text
        )

        try:
            response = st.session_state.llm(prompt)
            paragraphs = parse_email_paragraphs(response)
            df.at[idx, 'Paragraph1'] = paragraphs[0]
            df.at[idx, 'Paragraph2'] = paragraphs[1]
            df.at[idx, 'Paragraph3'] = paragraphs[2]
        except Exception as e:
            st.error(f"Error generating email for {row['First Name']} {row['Last Name']}: {str(e)}")
            df.at[idx, 'Paragraph1'] = f"Error: {str(e)}"

        progress_bar.progress((idx + 1) / total_rows)

    return df


def main():
    initialize_session_state()

    # Email verification before showing the main content
    if not email_verification_form():
        st.warning("Please enter your zohocorp.com email to access the tool")
        return

    st.title("Hyper-Personalized B2B Email Generator")

    # Documentation section
    with st.expander("📚 How to Use & Personalization Features"):
        st.markdown("""
        ### Personalization Capabilities
        This tool creates highly personalized emails by leveraging:
        1. **Industry-Specific Context**: Tailors content to industry challenges and opportunities
        2. **Role-Based Relevance**: Adapts messaging based on recipient's position
        3. **Geographic Customization**: Incorporates country-specific context
        4. **Company Context**: References company-specific information
        5. **Custom Context**: Integrates your custom text naturally into the email

        ### Sample CSV Format
        Download the sample template from the left sidebar.

        ### Requirements
        - Use exact column names (case-sensitive)
        - Fill all fields for each lead
        - Use standard CSV format with comma separators
        - Avoid special characters in headers
        """)

    # Sidebar configuration
    st.sidebar.header("Email Configuration")

    # Download sample CSV template
    sample_csv = """First Name,Last Name,Company,Role,Industry,Country
John,Smith,TechCorp Inc,IT Director,Healthcare,United States
Sarah,Johnson,GlobalSys Ltd,CTO,Manufacturing,United Kingdom
Michael,Chen,DataFlow Systems,System Administrator,Finance,Singapore
Emma,Garcia,InnovateTech,IT Manager,Education,Canada
David,Kumar,SecureNet Solutions,Infrastructure Lead,Banking,Australia"""

    st.sidebar.download_button(
        label="📥 Download Sample CSV Template",
        data=sample_csv,
        file_name="sample_leads_template.csv",
        mime="text/csv",
    )

    # CTA Selection
    cta_type = st.sidebar.radio("Choose CTA Type", ["Predefined CTA", "Custom CTA"])

    if cta_type == "Predefined CTA":
        selected_cta = st.sidebar.selectbox("Select Call-to-Action", list(CTA_OPTIONS.keys()))
        cta_text = CTA_OPTIONS[selected_cta]
    else:
        cta_text = st.sidebar.text_area(
            "Enter Custom CTA",
            help="Write your own call-to-action message",
            placeholder="E.g., Would you be interested in joining our exclusive partner program?"
        )

    # Custom Context
    custom_text = st.sidebar.text_area(
        "Custom Context",
        help="Enter any specific context, pain points, or messaging you'd like to incorporate into the emails",
        placeholder="E.g., Recent security breaches in the industry, specific compliance requirements, or current market challenges..."
    )

    # File upload
    st.header("Upload Contact List")
    uploaded_file = st.file_uploader("Upload CSV file with contacts", type=['csv'])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['First Name', 'Last Name', 'Company', 'Role', 'Industry', 'Country']
            if not all(col in df.columns for col in required_columns):
                st.error(f"CSV must contain these columns: {', '.join(required_columns)}")
                return

            st.write("### Preview of uploaded data")
            st.dataframe(df.head())

            # Generate Emails Button
            if st.button("Generate Personalized Emails"):
                with st.spinner("Generating personalized emails..."):
                    result_df = generate_bulk_emails(df, cta_text, custom_text)

                    # Show preview of results
                    st.write("### Preview of generated emails")
                    st.dataframe(result_df.head())

                    # Download button
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        label="Download Generated Emails CSV",
                        data=csv,
                        file_name="personalized_emails.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


if __name__ == "__main__":
    main()
