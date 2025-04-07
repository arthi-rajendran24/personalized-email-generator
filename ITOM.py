import streamlit as st
import pandas as pd
import google.generativeai as genai
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
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'genai_initialized' not in st.session_state:
        st.session_state.genai_initialized = False
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


def initialize_gemini(api_key):
    """Initialize Gemini model with provided API key"""
    try:
        genai.configure(api_key=api_key)
        # Configure default generation config
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 60000,
        }

        # Initialize Gemini Pro model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-pro-exp-03-25",
            generation_config=generation_config
        )

        st.session_state.model = model
        st.session_state.genai_initialized = True
        return True
    except Exception as e:
        st.error(f"Error initializing Gemini API: {str(e)}")
        st.session_state.genai_initialized = False
        return False


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


def api_key_form():
    """Display API key input form"""
    st.sidebar.markdown("### Gemini API Configuration")
    api_key = st.sidebar.text_input(
        "Enter your Gemini API Key",
        type="password",
        help="Enter your Google AI Studio API key for Gemini"
    )

    if api_key:
        if api_key != st.session_state.api_key or not st.session_state.genai_initialized:
            st.session_state.api_key = api_key
            if initialize_gemini(api_key):
                st.sidebar.success("Gemini API initialized successfully!")
                return True
            else:
                return False
        return True
    return False


def parse_email_paragraphs(email_content):
    """Split email content into three paragraphs."""
    paragraphs = email_content.strip().split('\n\n')
    clean_paragraphs = []

    for p in paragraphs:
        # Skip empty paragraphs or those that might be formatting elements
        if p and not p.startswith('---') and not p.startswith('#'):
            clean_paragraphs.append(p)

    while len(clean_paragraphs) < 3:
        clean_paragraphs.append("")

    return clean_paragraphs[:3]


import time


def generate_email_content(prompt):
    """Generate email content using Gemini model with rate limit handling."""
    retry_count = 0
    max_retries = 5
    delay = 60  # start with 60 seconds

    while retry_count < max_retries:
        try:
            response = st.session_state.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "quota" in error_message.lower():
                st.warning(f"Rate limit hit. Waiting for {delay} seconds before retrying...")
                time.sleep(delay)
                retry_count += 1
                delay *= 2  # exponential backoff
            else:
                st.error(f"Error generating content: {error_message}")
                return f"Error: {error_message}"

    st.error("Max retries exceeded due to rate limits.")
    return "Error: Too many requests. Please try again later or check your quota."


def generate_bulk_emails(df, cta_text, custom_text):
    """Generate personalized emails for multiple recipients and add paragraphs as new columns."""
    df = df.copy()
    df['Paragraph1'] = ""
    df['Paragraph2'] = ""
    df['Paragraph3'] = ""

    progress_bar = st.progress(0)
    total_rows = len(df)

    for idx, row in df.iterrows():
        prompt = st.session_state.template.format(
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
            response = generate_email_content(prompt)
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

    st.title("Hyper-Personalized B2B Email Generator")

    # Email verification before showing the main content
    if not email_verification_form():
        st.warning("Please enter your zohocorp.com email to access the tool")
        return

    # API key verification
    if not api_key_form():
        st.warning("Please enter a valid Gemini API key to use the tool")
        return

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

    # Model parameters (optional)
    with st.sidebar.expander("Advanced Model Settings"):
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                                help="Higher values make output more random, lower values more deterministic")
        if temperature != 0.7 and st.session_state.genai_initialized:
            st.session_state.model.generation_config["temperature"] = temperature

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

            # Generate single example
            if st.button("Generate Sample Email"):
                with st.spinner("Generating sample email..."):
                    # Use the first row for the sample
                    first_row = df.iloc[0]
                    prompt = st.session_state.template.format(
                        first_name=first_row['First Name'],
                        last_name=first_row['Last Name'],
                        company=first_row['Company'],
                        role=first_row['Role'],
                        industry=first_row['Industry'],
                        country=first_row['Country'],
                        product_description=ITOM['description'],
                        product_features=", ".join(ITOM['features']),
                        cta=cta_text,
                        custom_text=custom_text
                    )

                    sample_email = generate_email_content(prompt)
                    st.subheader(f"Sample Email for {first_row['First Name']} {first_row['Last Name']}")
                    paragraphs = parse_email_paragraphs(sample_email)

                    for i, paragraph in enumerate(paragraphs, 1):
                        st.markdown(f"**Paragraph {i}:**\n\n{paragraph}")

            # Generate Emails Button
            if st.button("Generate Personalized Emails for All Contacts"):
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
