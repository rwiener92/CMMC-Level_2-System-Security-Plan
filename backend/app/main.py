from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from sqlmodel import SQLModel, Field, Session, create_engine, select
import os, shutil, datetime
from collections import Counter

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/data/uploads")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI(title="CertManager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

class Control(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: str = Field(index=True, unique=True)
    domain: str
    title: str
    statement: str
    discussion: Optional[str] = None
    further_discussion: Optional[str] = None
    key_references: Optional[str] = None
    assessment_objectives: Optional[str] = None
    assessment_methods: Optional[str] = None
    c3pao_finding: Optional[str] = Field(default=None, index=True)
    self_impl_status: Optional[str] = Field(default=None, index=True)

class TextLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: str = Field(index=True)
    kind: str = Field(index=True)
    text: str
    ts: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class Evidence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: str = Field(index=True)
    filename: str
    size: int
    ts: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    path: str

SQLModel.metadata.create_all(engine)
SEED = [
{
    "requirement_id": "AC.L2-3.1.1",
    "title": "Authorized Access Control [CUI Data]",
    "domain": "Access Control (AC)",
    "statement": "Limit system access to authorized users, processes acting on behalf of authorized users, and devices (including other systems).",
    "assessment_objectives": "[a] Authorized users identified;\n[b] Processes identified;\n[c] Devices identified;\n[d] Access limited to users;\n[e] Access limited to processes;\n[f] Access limited to devices.",
    "assessment_methods": "Examine: access control policy, account lists, audit logs;\n\nInterview: admins, security staff;\n\nTest: account management mechanisms.",
    "discussion": "Access control policies enforce access between users, processes, and devices.",
    "further_discussion": "Maintain list of authorized users/devices; associate automated processes with initiating user; restrict devices until approved.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to resources on the network are managed by Microsoft Active Directory Security Services. Duo 2FA",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.1; FAR 52.204-21 b.1.i"
  },
  {
    "requirement_id": "AC.L2-3.1.2",
    "title": "Transaction & Function Control",
    "domain": "Access Control (AC)",
    "statement": "Limit system access to the types of transactions and functions that authorized users are permitted to execute.",
    "assessment_objectives": "[a] Transactions/functions defined;\n[b] Access limited to defined functions.",
    "assessment_methods": "Examine: access control policy, system design docs;\n\nInterview: admins, developers;\n\nTest: enforcement mechanisms.",
    "discussion": "Organizations define access privileges by account type or attributes.",
    "further_discussion": "Limit users to only the systems/roles needed for their job.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to resources on the network are managed by Microsoft Active Directory Security Services. DUo 2FA",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.2; FAR 52.204-21 b.1.ii"
  },
  {
    "requirement_id": "AC.L2-3.1.3",
    "title": "Control CUI Flow",
    "domain": "Access Control (AC)",
    "statement": "Control the flow of CUI in accordance with approved authorizations.",
    "assessment_objectives": "[a] Flow control policies defined;\n[b] Enforcement mechanisms defined;\n[c] Sources/destinations identified;\n[d] Authorizations defined;\n[e] Authorizations enforced.",
    "assessment_methods": "Examine: flow control policies, configs;\n\nInterview: admins;\n\nTest: firewall/proxy enforcement.",
    "discussion": "Flow control regulates where information can travel.",
    "further_discussion": "Use firewalls, proxies, routing rules to separate sensitive data.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Controlled through Active Directory Security and Permissions",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.3"
  },
  {
    "requirement_id": "AC.L2-3.1.4",
    "title": "Separation of Duties",
    "domain": "Access Control (AC)",
    "statement": "Separate duties of individuals to reduce risk of malevolent activity without collusion.",
    "assessment_objectives": "[a] Duties separated;\n[b] Enforcement mechanisms implemented.",
    "assessment_methods": "Examine: org charts, role assignments;\n\nInterview: managers;\n\nTest: access restrictions.",
    "discussion": "Separation reduces insider threat.",
    "further_discussion": "Example: one person requests purchase, another approves.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to resources on the network are managed by Microsoft Active Directory Security Services",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.4"
  },
  {
    "requirement_id": "AC.L2-3.1.5",
    "title": "Least Privilege",
    "domain": "Access Control (AC)",
    "statement": "Employ the principle of least privilege, including for specific security functions and privileged accounts.",
    "assessment_objectives": "[a] Privileges defined;\n[b] Privileges limited;\n[c] Privileged accounts restricted.",
    "assessment_methods": "Examine: access control policy, account permissions;\n\nInterview: admins;\n\nTest: privilege enforcement.",
    "discussion": "Least privilege minimizes damage from compromise.",
    "further_discussion": "Example: admin rights only for IT staff.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to resources on the network are managed by Microsoft Active Directory Security Services",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.5"
  },
  {
    "requirement_id": "AC.L2-3.1.6",
    "title": "Non-Privileged Account Use",
    "domain": "Access Control (AC)",
    "statement": "Use non-privileged accounts or roles when accessing nonsecurity functions.",
    "assessment_objectives": "[a] Non-privileged accounts used for nonsecurity functions.",
    "assessment_methods": "Examine: account usage logs;\n\nInterview: users;\n\nTest: login restrictions.",
    "discussion": "Prevents unnecessary use of elevated accounts.",
    "further_discussion": "Example: admins use standard accounts for email.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Implemented 2019/2020 - Microsoft Active Directory",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.6"
  },
  {
    "requirement_id": "AC.L2-3.1.7",
    "title": "Privileged Functions",
    "domain": "Access Control (AC)",
    "statement": "Prevent non-privileged users from executing privileged functions and audit the execution of such functions.",
    "assessment_objectives": "[a] Privileged functions identified;\n[b] Non-privileged users restricted;\n[c] Privileged functions audited.",
    "assessment_methods": "Examine: audit logs, system configs;\n\nInterview: admins;\n\nTest: privilege enforcement.",
    "discussion": "Ensures only authorized users perform sensitive actions.",
    "further_discussion": "Example: only admins can install software.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to resources on the network are managed by Microsoft Active Directory Security Services",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.7"
  },
  {
    "requirement_id": "AC.L2-3.1.8",
    "title": "Unsuccessful Logon Attempts",
    "domain": "Access Control (AC)",
    "statement": "Limit unsuccessful logon attempts.",
    "assessment_objectives": "[a] Threshold defined;\n[b] Threshold enforced.",
    "assessment_methods": "Examine: system configs;\n\nInterview: admins;\n\nTest: lockout mechanism.",
    "discussion": "Prevents brute-force attacks.",
    "further_discussion": "Example: lock account after 5 failed attempts.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Lock the account on 3 unsuccessful logon attemps and account is locked for 30min or until administrator unlocks. Implemented using AD Group Polocies",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.8"
  },
  {
    "requirement_id": "AC.L2-3.1.9",
    "title": "Privacy & Security Notices",
    "domain": "Access Control (AC)",
    "statement": "Provide privacy and security notices consistent with applicable CUI rules.",
    "assessment_objectives": "[a] Notices displayed;\n[b] Notices consistent with rules.",
    "assessment_methods": "Examine: login banners;\n\nInterview: users;\n\nTest: system login.",
    "discussion": "Reminds users of responsibilities.",
    "further_discussion": "Example: “Unauthorized use prohibited” banner.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Screen saver in power management turns off display after 15 min",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.9"
  },
  {
    "requirement_id": "AC.L2-3.1.10",
    "title": "Session Lock",
    "domain": "Access Control (AC)",
    "statement": "Use session lock with pattern-hiding displays to prevent access/viewing after inactivity.",
    "assessment_objectives": "[a] Session lock implemented;\n[b] Pattern-hiding enabled.",
    "assessment_methods": "Examine: system configs;\n\nInterview: users;\n\nTest: inactivity lock.",
    "discussion": "Protects unattended systems.",
    "further_discussion": "Example: auto-lock after 15 minutes.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Session will lock after 15 min of inactivity.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.10"
  },
  {
    "requirement_id": "AC.L2-3.1.11",
    "title": "Session Termination",
    "domain": "Access Control (AC)",
    "statement": "Terminate (or log off) user sessions after defined conditions.",
    "assessment_objectives": "[a] Termination conditions defined;\n[b] Termination enforced.",
    "assessment_methods": "Examine: configs;\n\nInterview: admins;\n\nTest: session timeout.",
    "discussion": "Prevents hijacking of idle sessions.",
    "further_discussion": "Example: VPN disconnect after 30 minutes idle.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Terminal server sessions will be terminated after 8 hours of inactivity.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.11"
  },
  {
    "requirement_id": "AC.L2-3.1.12",
    "title": "Control Remote Access",
    "domain": "Access Control (AC)",
    "statement": "Authorize remote access prior to connection.",
    "assessment_objectives": "[a] Remote access authorized;\n[b] Authorization enforced.",
    "assessment_methods": "Examine: remote access policy;\n\nInterview: admins;\n\nTest: VPN access.",
    "discussion": "Ensures only approved users connect remotely.",
    "further_discussion": "Example: VPN access requires manager approval.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Active Directory Audit / Meraki VPN logs / Duo 2FA",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.12"
  },
  {
    "requirement_id": "AC.L2-3.1.13",
    "title": "Remote Access Confidentiality",
    "domain": "Access Control (AC)",
    "statement": "Protect the confidentiality of CUI during remote access sessions.",
    "assessment_objectives": "[a] Confidentiality protections defined; [b] Protections enforced.",
    "assessment_methods": "Examine: configs, encryption settings;\n\nInterview: admins;\n\nTest: remote session encryption.",
    "discussion": "Protects CUI in transit.",
    "further_discussion": "Example: VPN with AES-256 encryption.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Use key encrypted VPN tunnels for remote users",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.13"
  },
  {
    "requirement_id": "AC.L2-3.1.14",
    "title": "Remote Access Routing",
    "domain": "Access Control (AC)",
    "statement": "Route remote access through managed access control points.",
    "assessment_objectives": "[a] Routing defined;\n[b] Routing enforced.",
    "assessment_methods": "Examine: network diagrams;\n\nInterview: admins;\n\nTest: routing enforcement.",
    "discussion": "Centralizes monitoring and control.",
    "further_discussion": "Example: all remote traffic through VPN gateway.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Through VPN Connections w/Duo 2FA",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.14"
  },
  {
    "requirement_id": "AC.L2-3.1.15",
    "title": "Privileged Remote Access",
    "domain": "Access Control (AC)",
    "statement": "Authorize privileged commands and access only for remote sessions.",
    "assessment_objectives": "[a] Privileged remote access authorized; [b] Authorization enforced.",
    "assessment_methods": "Examine: remote access logs;\n\nInterview: admins;\n\nTest: privileged session controls.",
    "discussion": "Prevents abuse of remote admin access.",
    "further_discussion": "Example: separate approval for remote admin login.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Active Directory Audit / Meraki VPN logs / Duo 2FA",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.15"
  },
  {
    "requirement_id": "AC.L2-3.1.16",
    "title": "Wireless Access Authorization",
    "domain": "Access Control (AC)",
    "statement": "Authorize wireless access prior to allowing such connections.",
    "assessment_objectives": "[a] Wireless access authorized;\n[b] Authorization enforced.",
    "assessment_methods": "Examine: wireless configs;\n\nInterview: admins;\n\nTest: wireless access.",
    "discussion": "Prevents rogue wireless connections.",
    "further_discussion": "Example: MAC filtering for wireless devices.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Planned or Not Implemented",
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.16"
  },
  {
    "requirement_id": "AC.L2-3.1.17",
    "title": "Wireless Access Protection",
    "domain": "Access Control (AC)",
    "statement": "Protect wireless access using authentication and encryption.",
    "assessment_objectives": "[a] Authentication defined;\n[b] Encryption defined;\n[c] Protections enforced.",
    "assessment_methods": "Examine: configs;\n\nInterview: admins;\n\nTest: wireless encryption.",
    "discussion": "Protects wireless CUI transmissions.",
    "further_discussion": "Example: WPA3 enterprise authentication.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Planned or Not Implemented",
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.17"
  },
  {
    "requirement_id": "AC.L2-3.1.18",
    "title": "Mobile Device Connection",
    "domain": "Access Control (AC)",
    "statement": "Authorize mobile device connections to organizational systems.",
    "assessment_objectives": "[a] Mobile connections authorized;\n[b] Authorization enforced.",
    "assessment_methods": "Examine: mobile device policy;\n\nInterview: admins;\n\nTest: device enrollment.",
    "discussion": "Prevents unauthorized mobile access.",
    "further_discussion": "Example: MDM approval required.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": "Connection to devices that access USB storage disabled via computer manangement agent and SentinalOne",
    "Documentation": None,
    "Key References": "NIST SP 800-"
  },
  {
    "requirement_id": "AC.L2-3.1.19",
    "title": "Encrypt CUI on Mobile",
    "domain": "Access Control (AC)",
    "statement": "Encrypt CUI on mobile devices and mobile computing platforms.",
    "assessment_objectives": "[a] Mobile devices and platforms that store or process CUI are identified;\n[b] Cryptographic protections for CUI on mobile devices are defined;\n[c] Approved encryption methods are implemented;\n[d] Encryption is enforced for CUI at rest on mobile devices;\n[e] Encryption keys are managed per organizational policy.",
    "assessment_methods": "Examine: mobile device policy, MDM/EMM configurations, crypto standards (e.g., FIPS-validated modules), encryption settings;\n\nInterview: mobile administrators, security staff;\n\nTest: verify device encryption status, recovery/key management procedures.",
    "discussion": "Mobile devices pose elevated risk for loss or theft; encryption reduces exposure of CUI at rest. Controls typically rely on enterprise MDM enforcing full-disk/file-based encryption and disallowing storage of CUI on unencrypted devices.",
    "further_discussion": "Define what qualifies as a “mobile device” (phones, tablets, laptops used as mobile platforms). Enforce FIPS-validated crypto where required, disable local storage where encryption is infeasible, and verify escrowed keys are protected.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": "No company assigned mobile devices",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.19"
  },
  {
    "requirement_id": "AC.L2-3.1.20",
    "title": "External Connections [CUI Data]",
    "domain": "Access Control (AC)",
    "statement": "Verify and control/limit connections to and use of external systems.",
    "assessment_objectives": "[a] External systems relevant to CUI processing are identified;\n[b] Conditions for connecting to external systems are defined;\n[c] Connections to external systems are authorized and verified;\n[d] Use of external systems is controlled/limited per authorization;\n[e] Monitoring and review of external connections are performed.",
    "assessment_methods": "Examine: access control policy, external system use policy, supplier/cloud agreements, network diagrams;\n\nInterview: network/security admins, vendor managers;\n\nTest: connection authorization workflows, egress controls, allowlists/denylists.",
    "discussion": "External systems (e.g., cloud services, partner networks) increase attack surface; authorization and technical controls (gateways, proxies, CASB) help ensure CUI flows only to approved destinations under defined conditions.",
    "further_discussion": "Maintain an inventory of external services handling CUI. Use managed access points, enforce conditional access, and require contractual safeguards for CUI. Periodically review logs and access reports for policy compliance.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": "Meraki content filtering",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.20"
  },
  {
    "requirement_id": "AC.L2-3.1.21",
    "title": "Portable Storage Use",
    "domain": "Access Control (AC)",
    "statement": "Limit use of portable storage devices on external systems.",
    "assessment_objectives": "[a] Policies for portable storage device (PSD) use with external systems are defined;\n[b] PSD use on external systems is limited or prohibited;\n[c] Exceptions are authorized and documented;\n[d] Technical controls enforce PSD restrictions;\n[e] Monitoring detects and responds to unauthorized PSD use.",
    "assessment_methods": "Examine: media protection and access control policies, endpoint control configurations (DLP/EDR), exception registers;\n\nInterview: endpoint/security admins;\n\nTest: PSD blocking/enforcement on external and unmanaged systems.",
    "discussion": "Portable storage (USB) can bypass protections and exfiltrate CUI; restricting or prohibiting PSD use with external/unmanaged systems reduces leakage and malware risk.",
    "further_discussion": "Implement device control to block USB mass storage on systems that may connect externally; require encrypted, managed media when PSD use is necessary and maintain auditable exception processes.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": "External storage devices are blocked.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.21"
  },
  {
    "requirement_id": "AC.L2-3.1.22",
    "title": "Control Public Information [CUI Data]",
    "domain": "Access Control (AC)",
    "statement": "Control information posted or processed on publicly accessible systems.",
    "assessment_objectives": "[a] Rules for public posting/processing are defined;\n[b] Approval workflow exists for public releases;\n[c] CUI is prevented from being posted/processed on public systems;\n[d] Monitoring detects potential public exposure;\n[e] Remediation procedures exist for accidental disclosure.",
    "assessment_methods": "Examine: public website/content policies, release approval records, DLP/web gateway configurations;\n\nInterview: content owners, compliance, security staff;\n\nTest: publication workflows, preventative controls (DLP, tagging), takedown procedures.",
    "discussion": "Publicly accessible systems must not host CUI; governance and technical safeguards ensure only authorized public information is posted, with rapid response to exposure events.",
    "further_discussion": "Use data classification/tagging to prevent CUI from entering public channels. Require pre-publication reviews, implement DLP on egress and web, and establish takedown and notification playbooks for incidents.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": "Website",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.1.22"
  },
  {
    "requirement_id": "AT.L2-3.2.1",
    "title": "Role-Based Risk Awareness",
    "domain": "Awareness & Training (AT)",
    "statement": "Ensure that managers, system administrators, and users of organizational systems are made aware of the security risks associated with their activities and of the applicable policies, standards, and procedures related to the security of those systems.",
    "assessment_objectives": "[a] Managers are made aware of security risks;\n[b] System administrators are made aware of security risks;\n[c] Users are made aware of security risks;\n[d] Managers are made aware of applicable policies, standards, and procedures;\n[e] System administrators are made aware of applicable policies, standards, and procedures;\n[f] Users are made aware of applicable policies, standards, and procedures.",
    "assessment_methods": "Examine: training policy, awareness materials, attendance records, communications;\n\nInterview: managers, admins, users;\n\nTest: awareness through spot checks or quizzes.",
    "discussion": "Awareness ensures that all personnel understand their role in protecting CUI and the risks of mishandling it.",
    "further_discussion": "Training should be tailored to roles: managers focus on oversight, admins on technical risks, users on daily practices. Example: phishing awareness for all staff, configuration hardening for admins.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Planned or Not Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "Yearly training planned - Feb 2021 session",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.2.1"
  },
  {
    "requirement_id": "AT.L2-3.2.2",
    "title": "Role-Based Training",
    "domain": "Awareness & Training (AT)",
    "statement": "Ensure that organizational personnel are adequately trained to carry out their assigned information security-related duties and responsibilities.",
    "assessment_objectives": "[a] Personnel with security-related duties are identified;\n[b] Training content is defined;\n[c] Training is provided;\n[d] Training effectiveness is evaluated.",
    "assessment_methods": "Examine: training plans, curricula, attendance logs, certification records;\n\nInterview: staff with security duties, training coordinators;\n\nTest: demonstration of security tasks.",
    "discussion": "Training ensures staff can perform their security responsibilities effectively.",
    "further_discussion": "Example: system admins trained on patch management, incident responders trained on reporting procedures.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Planned or Not Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "Yearly training planned - Feb 2021 session",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.2.2"
  },
  {
    "requirement_id": "AT.L2-3.2.3",
    "title": "Insider Threat Awareness",
    "domain": "Awareness & Training (AT)",
    "statement": "Provide security awareness training on recognizing and reporting potential indicators of insider threat.",
    "assessment_objectives": "[a] Insider threat indicators are defined;\n[b] Training includes insider threat awareness;\n[c] Personnel are trained to recognize insider threat indicators;\n[d] Personnel are trained to report insider threat indicators.",
    "assessment_methods": "Examine: insider threat training materials, attendance logs, reporting procedures;\n\nInterview: staff, insider threat program managers;\n\nTest: awareness through scenarios or exercises.",
    "discussion": "Insider threats can cause significant harm; awareness helps detect and mitigate risks early.",
    "further_discussion": "Example: training staff to recognize unusual downloading, unauthorized data transfers, or behavioral red flags.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Partially Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "Yearly training planned - Feb 2021 session",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.2.3"
  },
  {
    "requirement_id": "AU.L2-3.3.1",
    "title": "System Auditing",
    "domain": "Audit & Accountability (AU)",
    "statement": "Create and retain system audit logs and records to enable the monitoring, analysis, investigation, and reporting of unlawful, unauthorized, or inappropriate system activity.",
    "assessment_objectives": "[a] Events to be audited are defined;\n[b] Audit records are generated;\n[c] Audit records are retained;\n[d] Audit records support monitoring, analysis, investigation, and reporting.",
    "assessment_methods": "Examine: audit policy, system configs, log retention settings;\n\nInterview: admins, security staff;\n\nTest: log generation and retention.",
    "discussion": "Audit logs are critical for detecting and investigating incidents.",
    "further_discussion": "Define what events to log (e.g., logons, privilege use, file access). Retain logs per policy.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Audit logs are being back up with servers.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.1"
  },
  {
    "requirement_id": "AU.L2-3.3.2",
    "title": "User Accountability",
    "domain": "Audit & Accountability (AU)",
    "statement": "Ensure that the actions of individual system users can be uniquely traced to those users so they can be held accountable for their actions.",
    "assessment_objectives": "[a] Users uniquely identified;\n[b] User actions uniquely traced;\n[c] Accountability enforced.",
    "assessment_methods": "Examine: account management, audit logs;\n\nInterview: admins;\n\nTest: traceability of user actions.",
    "discussion": "Accountability requires unique IDs and audit trails.",
    "further_discussion": "Shared accounts undermine accountability; enforce unique logins.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Audit tools and Event Logs, Meraki logs",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.2"
  },
  {
    "requirement_id": "AU.L2-3.3.3",
    "title": "Event Review",
    "domain": "Audit & Accountability (AU)",
    "statement": "Review and update audited events.",
    "assessment_objectives": "[a] Audited events reviewed;\n[b] Audited events updated.",
    "assessment_methods": "Examine: audit policy, review records;\n\nInterview: security staff;\n\nTest: review process.",
    "discussion": "Regular review ensures logging remains relevant.",
    "further_discussion": "Example: add new event types after system changes.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "LionGard Roar",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.3"
  },
  {
    "requirement_id": "AU.L2-3.3.4",
    "title": "Audit Failure Alerting",
    "domain": "Audit & Accountability (AU)",
    "statement": "Alert in the event of an audit logging process failure.",
    "assessment_objectives": "[a] Audit failures detected;\n[b] Alerts generated;\n[c] Alerts acted upon.",
    "assessment_methods": "Examine: system configs, alerting tools;\n\nInterview: admins;\n\nTest: simulate audit failure.",
    "discussion": "Alerts prevent silent loss of audit data.",
    "further_discussion": "Example: SIEM alerts if log service stops.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Agents on each server will trigger alerts if suspected behavior",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.4"
  },
  {
    "requirement_id": "AU.L2-3.3.5",
    "title": "Audit Correlation",
    "domain": "Audit & Accountability (AU)",
    "statement": "Correlate audit record review, analysis, and reporting processes for investigation and response to indications of unlawful, unauthorized, suspicious, or unusual activity.",
    "assessment_objectives": "[a] Audit correlation defined;\n[b] Audit correlation implemented.",
    "assessment_methods": "Examine: SIEM configs, correlation rules;\n\nInterview: SOC staff;\n\nTest: correlation in action.",
    "discussion": "Correlation links events across systems.",
    "further_discussion": "Example: failed logins + privilege escalation attempt.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Agents on each server will trigger alerts if suspected behavior",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.5"
  },
  {
    "requirement_id": "AU.L2-3.3.6",
    "title": "Reduction & Reporting",
    "domain": "Audit & Accountability (AU)",
    "statement": "Provide audit record reduction and report generation to support on-demand analysis and reporting.",
    "assessment_objectives": "[a] Reduction capability implemented;\n[b] Reporting capability implemented.",
    "assessment_methods": "Examine: SIEM/reporting tools;\n\nInterview: admins;\n\nTest: generate reports.",
    "discussion": "Reduces audit data volume for analysis.",
    "further_discussion": "Example: filter logs by user, time, or event type.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Audit tools and Event Logs, Remote Monitoring Agent",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.6"
  },
  {
    "requirement_id": "AU.L2-3.3.7",
    "title": "Authoritative Time Source",
    "domain": "Audit & Accountability (AU)",
    "statement": "Provide a system capability that compares and synchronizes internal system clocks with an authoritative source to generate time stamps for audit records.",
    "assessment_objectives": "[a] Authoritative time source defined;\n[b] Synchronization implemented;\n[c] Audit records time-stamped.",
    "assessment_methods": "Examine: NTP configs, system logs;\n\nInterview: admins;\n\nTest: time sync.",
    "discussion": "Accurate time is essential for correlating logs.",
    "further_discussion": "Use NTP servers; sync across systems.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.7"
  },
  {
    "requirement_id": "AU.L2-3.3.8",
    "title": "Audit Protection",
    "domain": "Audit & Accountability (AU)",
    "statement": "Protect audit information and audit tools from unauthorized access, modification, and deletion.",
    "assessment_objectives": "[a] Audit info protected;\n[b] Audit tools protected;\n[c] Unauthorized access prevented.",
    "assessment_methods": "Examine: access controls, permissions;\n\nInterview: admins;\n\nTest: attempt unauthorized access.",
    "discussion": "Protects integrity of audit data.",
    "further_discussion": "Restrict log access to security staff only.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Audit logs are being back up with servers.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.8"
  },
  {
    "requirement_id": "AU.L2-3.3.9",
    "title": "Audit Management",
    "domain": "Audit & Accountability (AU)",
    "statement": "Limit management of audit logging functionality to a subset of privileged users.",
    "assessment_objectives": "[a] Audit management restricted;\n[b] Restrictions enforced.",
    "assessment_methods": "Examine: role assignments, permissions;\n\nInterview: admins;\n\nTest: audit management controls.",
    "discussion": "Prevents tampering with audit logs.",
    "further_discussion": "Example: only security admins can disable logging.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Only Administrators have access to this information",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.3.9"
  },
  {
    "requirement_id": "CM.L2-3.4.1",
    "title": "System Baselining",
    "domain": "Configuration Management (CM)",
    "statement": "Establish and maintain baseline configurations and inventories of organizational systems (including hardware, software, firmware, and documentation) throughout the respective system development life cycles.",
    "assessment_objectives": "[a] Baseline configurations established;\n[b] Inventories maintained;\n[c] Baselines updated through lifecycle.",
    "assessment_methods": "Examine: baseline configs, inventories, system docs;\n\nInterview: admins;\n\nTest: verify baseline enforcement.",
    "discussion": "Baselines provide a known secure state for systems.",
    "further_discussion": "Example: maintain golden images for servers and track deviations.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.1"
  },
  {
    "requirement_id": "CM.L2-3.4.2",
    "title": "Security Configuration Enforcement",
    "domain": "Configuration Management (CM)",
    "statement": "Establish and enforce security configuration settings for information technology products employed in organizational systems.",
    "assessment_objectives": "[a] Security configs defined;\n[b] Configs enforced;\n[c] Configs documented.",
    "assessment_methods": "Examine: hardening guides, configs;\n\nInterview: admins;\n\nTest: verify enforcement.",
    "discussion": "Secure configs reduce vulnerabilities.",
    "further_discussion": "Example: CIS benchmarks applied to OS builds.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.2"
  },
  {
    "requirement_id": "CM.L2-3.4.3",
    "title": "System Change Management",
    "domain": "Configuration Management (CM)",
    "statement": "Track, review, approve/disapprove, and log changes to organizational systems.",
    "assessment_objectives": "[a] Changes tracked;\n[b] Changes reviewed;\n[c] Changes approved/disapproved;\n[d] Changes logged.",
    "assessment_methods": "Examine: change management policy, tickets;\n\nInterview: admins;\n\nTest: change workflow.",
    "discussion": "Change control prevents unauthorized modifications.",
    "further_discussion": "Example: ITIL change management process.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.3"
  },
  {
    "requirement_id": "CM.L2-3.4.4",
    "title": "Security Impact Analysis",
    "domain": "Configuration Management (CM)",
    "statement": "Analyze the security impact of changes prior to implementation.",
    "assessment_objectives": "[a] Security impact analysis performed;\n[b] Analysis documented;\n[c] Analysis considered in approval.",
    "assessment_methods": "Examine: change records, risk assessments;\n\nInterview: admins;\n\nTest: review change approvals.",
    "discussion": "Ensures changes don’t weaken security.",
    "further_discussion": "Example: patch tested in staging before production.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Group Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.4"
  },
  {
    "requirement_id": "CM.L2-3.4.5",
    "title": "Access Restrictions for Change",
    "domain": "Configuration Management (CM)",
    "statement": "Define, document, approve, and enforce physical and logical access restrictions associated with changes to organizational systems.",
    "assessment_objectives": "[a] Restrictions defined;\n[b] Restrictions documented;\n[c] Restrictions approved;\n[d] Restrictions enforced.",
    "assessment_methods": "Examine: access control policies, change records;\n\nInterview: admins;\n\nTest: verify restrictions.",
    "discussion": "Prevents unauthorized changes.",
    "further_discussion": "Example: only DBAs can alter production databases.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Group Policies).  Also with LionGard Roar",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.5"
  },
  {
    "requirement_id": "CM.L2-3.4.6",
    "title": "Least Functionality",
    "domain": "Configuration Management (CM)",
    "statement": "Employ the principle of least functionality by configuring systems to provide only essential capabilities.",
    "assessment_objectives": "[a] Essential capabilities defined;\n[b] Nonessential capabilities disabled.",
    "assessment_methods": "Examine: configs, system docs;\n\nInterview: admins;\n\nTest: verify disabled services.",
    "discussion": "Reduces attack surface.",
    "further_discussion": "Example: disable unused ports/services.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (NTFS Security)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.6"
  },
  {
    "requirement_id": "CM.L2-3.4.7",
    "title": "Nonessential Functionality",
    "domain": "Configuration Management (CM)",
    "statement": "Restrict, disable, or prevent the use of nonessential programs, functions, ports, protocols, and services.",
    "assessment_objectives": "[a] Nonessential items identified;\n[b] Items restricted/disabled/prevented.",
    "assessment_methods": "Examine: configs, inventories;\n\nInterview: admins;\n\nTest: verify restrictions.",
    "discussion": "Builds on least functionality.",
    "further_discussion": "Example: block FTP if not needed.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Group Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.7"
  },
  {
    "requirement_id": "CM.L2-3.4.8",
    "title": "Application Execution Policy",
    "domain": "Configuration Management (CM)",
    "statement": "Apply deny-by-exception (blacklisting) or allow-by-exception (whitelisting) policy to prevent unauthorized software execution.",
    "assessment_objectives": "[a] Execution policy defined;\n[b] Policy enforced.",
    "assessment_methods": "Examine: application control configs;\n\nInterview: admins;\n\nTest: attempt unauthorized execution.",
    "discussion": "Prevents malware/unauthorized apps.",
    "further_discussion": "Example: AppLocker or whitelisting tools.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Group Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.8"
  },
  {
    "requirement_id": "CM.L2-3.4.9",
    "title": "User-Installed Software",
    "domain": "Configuration Management (CM)",
    "statement": "Control and monitor user-installed software.",
    "assessment_objectives": "[a] Policy for user-installed software defined;\n[b] User-installed software monitored;\n[c] Unauthorized software removed.",
    "assessment_methods": "Examine: software inventories, policies;\n\nInterview: admins;\n\nTest: verify monitoring.",
    "discussion": "Prevents shadow IT and malware.",
    "further_discussion": "Example: block unauthorized installs via endpoint controls.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Group Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.4.9"
  },
  {
    "requirement_id": "IA.L2-3.5.1",
    "title": "Identification [CUI Data]",
    "domain": "Identification & Authentication (IA)",
    "statement": "Identify system users, processes acting on behalf of users, and devices.",
    "assessment_objectives": "[a] Users identified;\n[b] Processes identified;\n[c] Devices identified.",
    "assessment_methods": "Examine: account lists, device inventories;\n\nInterview: admins;\n\nTest: account/device identification.",
    "discussion": "Identification is the foundation for access control.",
    "further_discussion": "Example: maintain unique IDs for each user and device.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Microsoft Domain Controller",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.1"
  },
  {
    "requirement_id": "IA.L2-3.5.2",
    "title": "Authentication [CUI Data]",
    "domain": "Identification & Authentication (IA)",
    "statement": "Authenticate (or verify) the identities of users, processes, or devices as a prerequisite to allowing access.",
    "assessment_objectives": "[a] Users authenticated;\n[b] Processes authenticated;\n[c] Devices authenticated.",
    "assessment_methods": "Examine: authentication configs, logs;\n\nInterview: admins;\n\nTest: login/authentication.",
    "discussion": "Authentication ensures only valid identities gain access.",
    "further_discussion": "Example: password login, certificate-based device auth.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Microsoft Domain Controller w/Duo Two Form Factor Authentication",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.2"
  },
  {
    "requirement_id": "IA.L2-3.5.3",
    "title": "Multifactor Authentication",
    "domain": "Identification & Authentication (IA)",
    "statement": "Use multifactor authentication for local and network access to privileged accounts and for network access to non-privileged accounts.",
    "assessment_objectives": "[a] MFA implemented for privileged local access;\n[b] MFA implemented for privileged network access;\n[c] MFA implemented for non-privileged network access.",
    "assessment_methods": "Examine: MFA configs, policies;\n\nInterview: admins;\n\nTest: MFA login.",
    "discussion": "MFA strengthens authentication.",
    "further_discussion": "Example: smart card + PIN for VPN access.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools and Duo Two Form Factor Authentication. (Group Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.3"
  },
  {
    "requirement_id": "IA.L2-3.5.4",
    "title": "Replay-Resistant Authentication",
    "domain": "Identification & Authentication (IA)",
    "statement": "Employ replay-resistant authentication mechanisms for network access to privileged and non-privileged accounts.",
    "assessment_objectives": "[a] Replay-resistant mechanisms defined;\n[b] Mechanisms enforced.",
    "assessment_methods": "Examine: configs, protocols;\n\nInterview: admins;\n\nTest: authentication attempts.",
    "discussion": "Prevents reuse of captured credentials.",
    "further_discussion": "Example: Kerberos, TLS mutual auth.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.4"
  },
  {
    "requirement_id": "IA.L2-3.5.5",
    "title": "Identifier Reuse",
    "domain": "Identification & Authentication (IA)",
    "statement": "Prevent reuse of identifiers for a defined period.",
    "assessment_objectives": "[a] Identifier reuse period defined;\n[b] Identifier reuse prevented.",
    "assessment_methods": "Examine: account policies;\n\nInterview: admins;\n\nTest: account creation.",
    "discussion": "Prevents confusion and accountability issues.",
    "further_discussion": "Example: don’t reuse usernames for 1 year.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.5"
  },
  {
    "requirement_id": "IA.L2-3.5.6",
    "title": "Identifier Handling",
    "domain": "Identification & Authentication (IA)",
    "statement": "Disable identifiers after a defined period of inactivity.",
    "assessment_objectives": "[a] Inactivity period defined;\n[b] Identifiers disabled after inactivity.",
    "assessment_methods": "Examine: account policies, logs;\n\nInterview: admins;\n\nTest: inactive account handling.",
    "discussion": "Reduces risk from dormant accounts.",
    "further_discussion": "Example: disable accounts after 90 days inactive.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Terminal Server Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.6"
  },
  {
    "requirement_id": "IA.L2-3.5.7",
    "title": "Password Complexity",
    "domain": "Identification & Authentication (IA)",
    "statement": "Enforce a minimum password complexity and change of characters when new passwords are created.",
    "assessment_objectives": "[a] Complexity requirements defined;\n[b] Complexity enforced;\n[c] Character change enforced.",
    "assessment_methods": "Examine: password policy, configs;\n\nInterview: admins;\n\nTest: password creation.",
    "discussion": "Strong passwords reduce guessing risk.",
    "further_discussion": "Example: require 12+ characters, mix of types.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.7"
  },
  {
    "requirement_id": "IA.L2-3.5.8",
    "title": "Password Reuse",
    "domain": "Identification & Authentication (IA)",
    "statement": "Prohibit password reuse for a specified number of generations.",
    "assessment_objectives": "[a] Reuse limit defined;\n[b] Reuse prevented.",
    "assessment_methods": "Examine: password policy, configs;\n\nInterview: admins;\n\nTest: password change.",
    "discussion": "Prevents cycling back to old passwords.",
    "further_discussion": "Example: disallow reuse of last 24 passwords.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.8"
  },
  {
    "requirement_id": "IA.L2-3.5.9",
    "title": "Temporary Passwords",
    "domain": "Identification & Authentication (IA)",
    "statement": "Allow temporary password use only with immediate change upon first use.",
    "assessment_objectives": "[a] Temporary passwords allowed only for initial use;\n[b] Immediate change enforced.",
    "assessment_methods": "Examine: account creation procedures;\n\nInterview: admins;\n\nTest: temporary password use.",
    "discussion": "Prevents long-term use of insecure temporary credentials.",
    "further_discussion": "Example: new hire must change password at first login.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.9"
  },
  {
    "requirement_id": "IA.L2-3.5.10",
    "title": "Cryptographically-Protected Passwords",
    "domain": "Identification & Authentication (IA)",
    "statement": "Store and transmit only cryptographically-protected passwords.",
    "assessment_objectives": "[a] Passwords stored cryptographically protected;\n[b] Passwords transmitted cryptographically protected.",
    "assessment_methods": "Examine: configs, password storage methods;\n\nInterview: admins;\n\nTest: password storage/transmission.",
    "discussion": "Protects passwords from disclosure.",
    "further_discussion": "Example: salted hash storage, TLS transmission.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.10"
  },
  {
    "requirement_id": "IA.L2-3.5.11",
    "title": "Obscure Feedback",
    "domain": "Identification & Authentication (IA)",
    "statement": "Obscure feedback of authentication information during the authentication process.",
    "assessment_objectives": "[a] Feedback obscured during authentication.",
    "assessment_methods": "Examine: login screens, configs;\n\nInterview: admins;\n\nTest: login attempts.",
    "discussion": "Prevents attackers from learning details about authentication.",
    "further_discussion": "Example: generic error messages (“Login failed”).",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Not Applicable",
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.5.11"
  },
  {
    "requirement_id": "IR.L2-3.6.1",
    "title": "Incident Handling",
    "domain": "Incident Response (IR)",
    "statement": "Establish an operational incident-handling capability for organizational systems that includes preparation, detection, analysis, containment, recovery, and user response activities.",
    "assessment_objectives": "[a] Incident-handling capability established;\n[b] Capability includes preparation;\n[c] Capability includes detection;\n[d] Capability includes analysis;\n[e] Capability includes containment;\n[f] Capability includes recovery;\n[g] Capability includes user response.",
    "assessment_methods": "Examine: incident response plan, playbooks, training records, incident logs;\n\nInterview: IR team, security staff;\n\nTest: tabletop or live exercises.",
    "discussion": "Incident handling ensures organizations can respond effectively to security events.",
    "further_discussion": "A mature IR program includes documented procedures, trained staff, and tested playbooks. Example: phishing incident → detect, analyze, contain, recover, notify users.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "On-Site Ticketing System documents issues and resolutions",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.6.1"
  },
  {
    "requirement_id": "IR.L2-3.6.2",
    "title": "Incident Reporting",
    "domain": "Incident Response (IR)",
    "statement": "Track, document, and report incidents to designated officials and/or authorities both internal and external to the organization.",
    "assessment_objectives": "[a] Incidents tracked;\n[b] Incidents documented;\n[c] Incidents reported internally;\n[d] Incidents reported externally (as required).",
    "assessment_methods": "Examine: incident logs, reporting procedures, communication records;\n\nInterview: IR staff, compliance officers;\n\nTest: reporting workflow.",
    "discussion": "Reporting ensures accountability and compliance with DoD/contractual requirements.",
    "further_discussion": "Example: report CUI breach to DoD within required timeframe; maintain internal incident register.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "On-Site Ticketing System documents issues and resolutions",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.6.2"
  },
  {
    "requirement_id": "IR.L2-3.6.3",
    "title": "Incident Response Testing",
    "domain": "Incident Response (IR)",
    "statement": "Test the organizational incident response capability.",
    "assessment_objectives": "[a] Incident response capability tested;\n[b] Test results documented;\n[c] Lessons learned captured and applied.",
    "assessment_methods": "Examine: test plans, after-action reports;\n\nInterview: IR staff;\n\nTest: conduct tabletop or simulated incident.",
    "discussion": "Testing validates readiness and identifies gaps.",
    "further_discussion": "Example: annual tabletop exercise simulating ransomware attack; update IR plan based on lessons learned.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "On-Site Computer Management Agent automates most processes and monthly hands on maintenance.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.6.3"
  },
  {
    "requirement_id": "MA.L2-3.7.1",
    "title": "Perform Maintenance",
    "domain": "Maintenance (MA)",
    "statement": "Perform maintenance on organizational systems.",
    "assessment_objectives": "[a] Maintenance activities are defined;\n[b] Maintenance activities are performed;\n[c] Maintenance activities are documented.",
    "assessment_methods": "Examine: maintenance logs, policies, procedures;\n\nInterview: system admins, maintenance staff;\n\nTest: review maintenance records.",
    "discussion": "Regular maintenance ensures systems remain secure and functional.",
    "further_discussion": "Example: patching servers, replacing failing hardware, updating firmware.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Remote agents perform some automated maintenance and scheduled in person onsite performed by On-Site Technology",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.7.1"
  },
  {
    "requirement_id": "MA.L2-3.7.2",
    "title": "System Maintenance Control",
    "domain": "Maintenance (MA)",
    "statement": "Provide controls on the tools, techniques, mechanisms, and personnel used to conduct system maintenance.",
    "assessment_objectives": "[a] Tools/techniques/mechanisms/personnel defined;\n[b] Controls implemented;\n[c] Controls enforced.",
    "assessment_methods": "Examine: maintenance tool inventories, access controls, policies;\n\nInterview: admins;\n\nTest: verify tool restrictions.",
    "discussion": "Maintenance tools can be powerful and must be controlled.",
    "further_discussion": "Example: restrict use of remote admin tools to authorized staff only.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.7.2"
  },
  {
    "requirement_id": "MA.L2-3.7.3",
    "title": "Equipment Sanitization",
    "domain": "Maintenance (MA)",
    "statement": "Ensure equipment removed for off-site maintenance is sanitized of CUI.",
    "assessment_objectives": "[a] Equipment requiring sanitization identified;\n[b] Sanitization performed;\n[c] Sanitization documented.",
    "assessment_methods": "Examine: sanitization policies, logs;\n\nInterview: admins;\n\nTest: verify sanitization before removal.",
    "discussion": "Prevents CUI leakage when equipment leaves premises.",
    "further_discussion": "Example: wipe hard drives before sending laptops for repair.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Use of DBAN software to sanitzie media and hard drives crushed before recycling. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.7.3"
  },
  {
    "requirement_id": "MA.L2-3.7.4",
    "title": "Media Inspection",
    "domain": "Maintenance (MA)",
    "statement": "Check media containing diagnostic and test programs for malicious code before use.",
    "assessment_objectives": "[a] Media identified;\n[b] Media inspected for malicious code;\n[c] Inspection documented.",
    "assessment_methods": "Examine: scanning procedures, logs;\n\nInterview: admins;\n\nTest: scan diagnostic media.",
    "discussion": "Prevents introduction of malware via maintenance media.",
    "further_discussion": "Example: scan vendor-provided firmware update USB before use.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "SentinalOne software implemented",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.7.4"
  },
  {
    "requirement_id": "MA.L2-3.7.5",
    "title": "Nonlocal Maintenance",
    "domain": "Maintenance (MA)",
    "statement": "Approve and monitor nonlocal maintenance and diagnostic activities.",
    "assessment_objectives": "[a] Nonlocal maintenance authorized;\n[b] Nonlocal maintenance monitored;\n[c] Records maintained.",
    "assessment_methods": "Examine: remote maintenance policies, logs;\n\nInterview: admins;\n\nTest: observe remote maintenance session.",
    "discussion": "Remote maintenance poses risks; must be controlled and monitored.",
    "further_discussion": "Example: vendor remote support requires approval and monitoring.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Configured through VPN and Duo two form factor authentication",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.7.5"
  },
  {
    "requirement_id": "MA.L2-3.7.6",
    "title": "Maintenance Personnel",
    "domain": "Maintenance (MA)",
    "statement": "Supervise the maintenance activities of maintenance personnel without required access authorization.",
    "assessment_objectives": "[a] Personnel without authorization supervised;\n[b] Supervision documented.",
    "assessment_methods": "Examine: supervision policies, logs;\n\nInterview: supervisors;\n\nTest: observe maintenance activities.",
    "discussion": "Ensures untrusted personnel don’t gain unsupervised access to systems.",
    "further_discussion": "Example: escort vendor technician during hardware repair.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.7.6"
  },
  {
    "requirement_id": "MP.L2-3.8.1",
    "title": "Media Protection",
    "domain": "Media Protection (MP)",
    "statement": "Protect (i.e., physically control and securely store) system media containing CUI, both paper and digital.",
    "assessment_objectives": "[a] Media containing CUI identified;\n[b] Media physically controlled;\n[c] Media securely stored.",
    "assessment_methods": "Examine: media protection policies, storage procedures;\n\nInterview: staff;\n\nTest: inspect storage areas.",
    "discussion": "Protecting media prevents unauthorized access to CUI.",
    "further_discussion": "Example: lock cabinets for paper, safes for removable drives.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "On-Site Tech. does not store any paper media containing CUI.  Media containing paper media is handed to Juniper for storage if any. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.1"
  },
  {
    "requirement_id": "MP.L2-3.8.2",
    "title": "Media Access",
    "domain": "Media Protection (MP)",
    "statement": "Limit access to CUI on system media to authorized users.",
    "assessment_objectives": "[a] Authorized users identified;\n[b] Access limited to authorized users.",
    "assessment_methods": "Examine: access logs, policies;\n\nInterview: staff;\n\nTest: attempt unauthorized access.",
    "discussion": "Restricts who can handle CUI media.",
    "further_discussion": "Example: only cleared staff can access backup tapes.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Media is wiped with DBAN software & media is crushed before disposal. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.2"
  },
  {
    "requirement_id": "MP.L2-3.8.3",
    "title": "Media Disposal [CUI Data]",
    "domain": "Media Protection (MP)",
    "statement": "Sanitize or destroy system media containing CUI before disposal or release for reuse.",
    "assessment_objectives": "[a] Media requiring sanitization identified;\n[b] Sanitization performed;\n[c] Sanitization documented.",
    "assessment_methods": "Examine: sanitization logs, policies;\n\nInterview: admins;\n\nTest: observe sanitization.",
    "discussion": "Prevents CUI leakage when media is discarded.",
    "further_discussion": "Example: shred paper, wipe drives with DoD-approved tools.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "Use of DBAN software to sanitzie media and hard drives crushed before recycling. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.3"
  },
  {
    "requirement_id": "MP.L2-3.8.4",
    "title": "Media Markings",
    "domain": "Media Protection (MP)",
    "statement": "Mark media containing CUI to indicate distribution limitations, handling caveats, and applicable security markings.",
    "assessment_objectives": "[a] Media requiring markings identified;\n[b] Media marked appropriately.",
    "assessment_methods": "Examine: media labels, policies;\n\nInterview: staff;\n\nTest: inspect media.",
    "discussion": "Markings communicate handling requirements.",
    "further_discussion": "Example: label USB drives “CUI – Confidential.”",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Planned or Not Implemented",
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.4"
  },
  {
    "requirement_id": "MP.L2-3.8.5",
    "title": "Media Accountability",
    "domain": "Media Protection (MP)",
    "statement": "Control access to media containing CUI and maintain accountability records.",
    "assessment_objectives": "[a] Media access controlled;\n[b] Accountability records maintained.",
    "assessment_methods": "Examine: media logs, policies;\n\nInterview: staff;\n\nTest: review accountability process.",
    "discussion": "Accountability ensures traceability of CUI media.",
    "further_discussion": "Example: sign-out logs for removable drives.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to exteral media denied. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.5"
  },
  {
    "requirement_id": "MP.L2-3.8.6",
    "title": "Portable Storage Encryption",
    "domain": "Media Protection (MP)",
    "statement": "Implement cryptographic mechanisms to protect the confidentiality of CUI stored on digital media during transport.",
    "assessment_objectives": "[a] Encryption mechanisms defined;\n[b] Encryption enforced;\n[c] Keys managed.",
    "assessment_methods": "Examine: encryption configs, policies;\n\nInterview: admins;\n\nTest: verify encrypted media.",
    "discussion": "Encryption protects CUI in transit.",
    "further_discussion": "Example: encrypt USB drives with AES-256.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to removable media disabled with management agent. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.6"
  },
  {
    "requirement_id": "MP.L2-3.8.7",
    "title": "Removable Media",
    "domain": "Media Protection (MP)",
    "statement": "Control the use of removable media on system components.",
    "assessment_objectives": "[a] Removable media use defined;\n[b] Controls implemented;\n[c] Controls enforced.",
    "assessment_methods": "Examine: endpoint configs, policies;\n\nInterview: admins;\n\nTest: attempt unauthorized use.",
    "discussion": "Removable media can bypass protections.",
    "further_discussion": "Example: block USB ports except for approved devices.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to removable media disabled with management agent. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.7"
  },
  {
    "requirement_id": "MP.L2-3.8.8",
    "title": "Shared Media",
    "domain": "Media Protection (MP)",
    "statement": "Prohibit the use of portable storage devices when such devices have no identifiable owner.",
    "assessment_objectives": "[a] Policy defined;\n[b] Use of ownerless devices prohibited;\n[c] Enforcement implemented.",
    "assessment_methods": "Examine: policies, endpoint configs;\n\nInterview: admins;\n\nTest: attempt to use unregistered device.",
    "discussion": "Prevents introduction of untrusted media.",
    "further_discussion": "Example: disallow “found” USB drives.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Access to removable media disabled with management agent. ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.8"
  },
  {
    "requirement_id": "MP.L2-3.8.9",
    "title": "Protect Backups",
    "domain": "Media Protection (MP)",
    "statement": "Protect the confidentiality of backup CUI at storage locations.",
    "assessment_objectives": "[a] Backup media identified;\n[b] Confidentiality protections defined;\n[c] Protections enforced.",
    "assessment_methods": "Examine: backup policies, encryption configs;\n\nInterview: admins;\n\nTest: verify backup protections.",
    "discussion": "Backups often contain full datasets; must be protected.",
    "further_discussion": "Example: encrypt offsite backups, restrict access.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "All Backups are encrypted",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.8.9"
  },
  {
    "requirement_id": "PS.L2-3.9.1",
    "title": "Screen Individuals",
    "domain": "Personnel Security (PS)",
    "statement": "Screen individuals prior to authorizing access to organizational systems containing CUI.",
    "assessment_objectives": "[a] Screening criteria are defined;\n[b] Individuals are screened prior to access;\n[c] Screening results are used to determine access authorization.",
    "assessment_methods": "Examine: personnel security policies, HR records, background check documentation;\n\nInterview: HR staff, security officers;\n\nTest: verify screening before granting access.",
    "discussion": "Screening reduces risk of insider threats by ensuring only trustworthy individuals gain access to CUI systems.",
    "further_discussion": "Example: conduct background checks before granting system accounts; re-screen periodically as required by contracts.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.9.1"
  },
  {
    "requirement_id": "PS.L2-3.9.2",
    "title": "Personnel Actions",
    "domain": "Personnel Security (PS)",
    "statement": "Ensure that organizational systems containing CUI are protected during and after personnel actions such as terminations and transfers.",
    "assessment_objectives": "[a] Personnel actions that could affect system access are identified;\n[b] Access is modified or revoked as appropriate;\n[c] Protections are enforced during and after personnel actions.",
    "assessment_methods": "Examine: termination/transfer procedures, access revocation logs;\n\nInterview: HR staff, IT admins;\n\nTest: verify timely account disablement.",
    "discussion": "Protects CUI when staff leave or change roles.",
    "further_discussion": "Example: immediately disable accounts upon termination; adjust privileges when employees transfer roles.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.9.2"
  },
  {
    "requirement_id": "PE.L2-3.10.1",
    "title": "Limit Physical Access [CUI Data]",
    "domain": "Physical Protection (PE)",
    "statement": "Limit physical access to organizational systems, equipment, and the respective operating environments to authorized individuals.",
    "assessment_objectives": "[a] Authorized individuals identified;\n[b] Physical access limited to authorized individuals;\n[c] Access controls enforced.",
    "assessment_methods": "Examine: facility access policies, badge logs, visitor records;\n\nInterview: security staff;\n\nTest: attempt entry.",
    "discussion": "Physical access controls protect systems and CUI from unauthorized use.",
    "further_discussion": "Example: badge readers, locked server rooms, guards.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.10.1"
  },
  {
    "requirement_id": "PE.L2-3.10.2",
    "title": "Monitor Facility",
    "domain": "Physical Protection (PE)",
    "statement": "Protect and monitor the physical facility and support infrastructure for organizational systems.",
    "assessment_objectives": "[a] Facility protections defined;\n[b] Facility monitoring implemented;\n[c] Monitoring records maintained.",
    "assessment_methods": "Examine: surveillance policies, camera logs, monitoring systems;\n\nInterview: security staff;\n\nTest: review monitoring.",
    "discussion": "Monitoring deters and detects unauthorized access.",
    "further_discussion": "Example: CCTV, intrusion detection, security patrols.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": "Security cameras",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.10.2"
  },
  {
    "requirement_id": "PE.L2-3.10.3",
    "title": "Escort Visitors [CUI Data]",
    "domain": "Physical Protection (PE)",
    "statement": "Escort visitors and monitor visitor activity.",
    "assessment_objectives": "[a] Visitor escort policy defined;\n[b] Visitors escorted;\n[c] Visitor activity monitored.",
    "assessment_methods": "Examine: visitor logs, escort policies;\n\nInterview: staff;\n\nTest: observe escort procedures.",
    "discussion": "Visitors must not have unsupervised access to CUI systems.",
    "further_discussion": "Example: contractors escorted in server rooms.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.10.3"
  },
  {
    "requirement_id": "PE.L2-3.10.4",
    "title": "Physical Access Logs [CUI Data]",
    "domain": "Physical Protection (PE)",
    "statement": "Maintain audit logs of physical access.",
    "assessment_objectives": "[a] Physical access logs maintained;\n[b] Logs reviewed;\n[c] Logs protected.",
    "assessment_methods": "Examine: access logs, visitor records;\n\nInterview: security staff;\n\nTest: review log retention.",
    "discussion": "Logs provide accountability for facility access.",
    "further_discussion": "Example: electronic badge logs, visitor sign-in sheets.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.10.4"
  },
  {
    "requirement_id": "PE.L2-3.10.5",
    "title": "Manage Physical Access [CUI Data]",
    "domain": "Physical Protection (PE)",
    "statement": "Control and manage physical access devices.",
    "assessment_objectives": "[a] Physical access devices identified;\n[b] Devices managed;\n[c] Devices protected.",
    "assessment_methods": "Examine: badge/key management policies, inventories;\n\nInterview: security staff;\n\nTest: verify device management.",
    "discussion": "Access devices (keys, badges) must be controlled to prevent misuse.",
    "further_discussion": "Example: revoke badges upon termination, track keys.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "VPN, 2FA, Microft Domain Controller tools",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.10.5"
  },
  {
    "requirement_id": "PE.L2-3.10.6",
    "title": "Alternative Work Sites",
    "domain": "Physical Protection (PE)",
    "statement": "Enforce safeguarding measures for CUI at alternative work sites.",
    "assessment_objectives": "[a] Alternative work sites identified;\n[b] Safeguarding measures defined;\n[c] Measures enforced.",
    "assessment_methods": "Examine: telework/remote site policies, training;\n\nInterview: remote staff;\n\nTest: verify safeguards.",
    "discussion": "CUI must be protected outside primary facilities.",
    "further_discussion": "Example: lockable cabinets at home offices, VPN for remote access.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "VPN, 2FA, Microft Domain Controller tools",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.10.6"
  },
  {
    "requirement_id": "RA.L2-3.11.1",
    "title": "Risk Assessments",
    "domain": "Risk Assessment (RA)",
    "statement": "Periodically assess the risk to organizational operations (including mission, functions, image, or reputation), organizational assets, and individuals, resulting from the operation of organizational systems and the associated processing, storage, or transmission of CUI.",
    "assessment_objectives": "[a] Risk assessment policy/procedures defined;\n[b] Risk assessments conducted;\n[c] Assessments address organizational operations, assets, and individuals;\n[d] Assessments address systems processing, storing, or transmitting CUI;\n[e] Assessments conducted periodically.",
    "assessment_methods": "Examine: risk assessment policy, risk register, assessment reports;\n\nInterview: risk managers, security staff;\n\nTest: review risk assessment cycle.",
    "discussion": "Risk assessments identify threats, vulnerabilities, and impacts to prioritize mitigation.",
    "further_discussion": "Example: annual risk assessment identifies outdated software as a vulnerability, leading to patching.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, mananaged antivirus",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.11.1"
  },
  {
    "requirement_id": "RA.L2-3.11.2",
    "title": "Vulnerability Scan",
    "domain": "Risk Assessment (RA)",
    "statement": "Scan for vulnerabilities in organizational systems and applications periodically and when new vulnerabilities affecting those systems and applications are identified.",
    "assessment_objectives": "[a] Vulnerability scanning capability implemented;\n[b] Scans conducted periodically;\n[c] Scans conducted when new vulnerabilities identified;\n[d] Results reviewed and analyzed.",
    "assessment_methods": "Examine: vulnerability scan policies, scan reports;\n\nInterview: admins;\n\nTest: run vulnerability scan.",
    "discussion": "Scanning identifies technical weaknesses before adversaries exploit them.",
    "further_discussion": "Example: weekly Nessus scans; ad hoc scans after new CVEs released.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, mananaged antivirus, updates and patch management",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.11.2"
  },
  {
    "requirement_id": "RA.L2-3.11.3",
    "title": "Vulnerability Remediation",
    "domain": "Risk Assessment (RA)",
    "statement": "Remediate vulnerabilities in accordance with risk assessments.",
    "assessment_objectives": "[a] Vulnerabilities prioritized based on risk;\n[b] Remediation actions defined;\n[c] Remediation actions implemented;\n[d] Remediation actions tracked.",
    "assessment_methods": "Examine: patch management policy, remediation logs;\n\nInterview: admins;\n\nTest: verify remediation of identified vulnerabilities.",
    "discussion": "Remediation ensures vulnerabilities are addressed in a timely, risk-based manner.",
    "further_discussion": "Example: critical vulnerabilities patched within 30 days; lower-risk issues tracked for later remediation.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, Meraki Dashboard",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.11.3"
  },
  {
    "requirement_id": "CA.L2-3.12.1",
    "title": "Security Control Assessment",
    "domain": "Security Assessment (CA)",
    "statement": "Periodically assess the security controls in organizational systems to determine if the controls are effective in their application.",
    "assessment_objectives": "[a] Security controls identified;\n[b] Assessments conducted periodically;\n[c] Effectiveness of controls determined;\n[d] Assessment results documented.",
    "assessment_methods": "Examine: assessment policies, reports, risk registers;\n\nInterview: security staff;\n\nTest: review assessment activities.",
    "discussion": "Regular assessments verify that controls are working as intended.",
    "further_discussion": "Example: annual self-assessment against NIST SP 800-171 controls.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "Reviewed periodically with maintenance ",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.12.1"
  },
  {
    "requirement_id": "CA.L2-3.12.2",
    "title": "Operational Plan of Action",
    "domain": "Security Assessment (CA)",
    "statement": "Develop and implement plans of action designed to correct deficiencies and reduce or eliminate vulnerabilities in organizational systems.",
    "assessment_objectives": "[a] Deficiencies identified;\n[b] Plans of action developed;\n[c] Plans implemented;\n[d] Plans tracked to completion.",
    "assessment_methods": "Examine: POA&M documents, remediation logs;\n\nInterview: security staff;\n\nTest: verify remediation progress.",
    "discussion": "Plans of action ensure continuous improvement.",
    "further_discussion": "Example: POA&M created for missing MFA, tracked until resolved.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, mananaged antivirus",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.12.2"
  },
  {
    "requirement_id": "CA.L2-3.12.3",
    "title": "Security Control Monitoring",
    "domain": "Security Assessment (CA)",
    "statement": "Monitor security controls on an ongoing basis to ensure the continued effectiveness of the controls.",
    "assessment_objectives": "[a] Monitoring strategy defined;\n[b] Monitoring implemented;\n[c] Monitoring results reviewed.",
    "assessment_methods": "Examine: monitoring policies, SIEM dashboards, reports;\n\nInterview: SOC staff;\n\nTest: review monitoring activities.",
    "discussion": "Ongoing monitoring detects control failures early.",
    "further_discussion": "Example: continuous monitoring of firewall rules and alerts.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, mananaged antivirus, Meraki Dashboard, Barracuda Spam filter",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.12.3"
  },
  {
    "requirement_id": "CA.L2-3.12.4",
    "title": "System Security Plan",
    "domain": "Security Assessment (CA)",
    "statement": "Develop, document, and periodically update system security plans that describe system boundaries, operational environment, how security requirements are implemented, and the relationships with or connections to other systems.",
    "assessment_objectives": "[a] System security plan developed;\n[b] Plan documents boundaries, environment, implementation, and connections;\n[c] Plan updated periodically.",
    "assessment_methods": "Examine: SSP documents, update logs;\n\nInterview: system owners;\n\nTest: review SSP content.",
    "discussion": "The SSP is the cornerstone of compliance documentation.",
    "further_discussion": "Example: SSP describes enclave boundaries, CUI handling, and external connections.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Shared/Hybrid",
    "What is the Solution?\nHow is it implemented?": "User access to network are monitored on network and documented. LionGard Roar",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.12.4"
  },
  {
    "requirement_id": "SC.L2-3.13.1",
    "title": "Boundary Protection [CUI Data]",
    "domain": "System & Communications Protection (SC)",
    "statement": "Monitor, control, and protect organizational communications (i.e., information transmitted or received by organizational systems) at the external boundaries and key internal boundaries of the systems.",
    "assessment_objectives": "[a] External boundaries identified;\n[b] Key internal boundaries identified;\n[c] Communications monitored, controlled, and protected at boundaries.",
    "assessment_methods": "Examine: network diagrams, firewall configs, IDS/IPS logs;\n\nInterview: network admins;\n\nTest: boundary protections.",
    "discussion": "Boundary protection prevents unauthorized access and data leakage.",
    "further_discussion": "Example: firewalls, IDS/IPS, DMZs.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.1"
  },
  {
    "requirement_id": "SC.L2-3.13.2",
    "title": "Security Engineering",
    "domain": "System & Communications Protection (SC)",
    "statement": "Employ architectural designs, software development techniques, and systems engineering principles that promote effective information security within organizational systems.",
    "assessment_objectives": "[a] Security principles defined;\n[b] Principles applied in design/development.",
    "assessment_methods": "Examine: design docs, SDLC policies;\n\nInterview: developers;\n\nTest: review secure coding practices.",
    "discussion": "Embedding security in design reduces vulnerabilities.",
    "further_discussion": "Example: threat modeling during system design.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.2"
  },
  {
    "requirement_id": "SC.L2-3.13.3",
    "title": "Role Separation",
    "domain": "System & Communications Protection (SC)",
    "statement": "Separate user functionality from system management functionality.",
    "assessment_objectives": "[a] User functionality separated;\n[b] Separation enforced.",
    "assessment_methods": "Examine: system configs, role assignments;\n\nInterview: admins;\n\nTest: verify separation.",
    "discussion": "Prevents users from accessing management functions.",
    "further_discussion": "Example: separate admin and user accounts.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Implemented through Activie Directory security groups",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.3"
  },
  {
    "requirement_id": "SC.L2-3.13.4",
    "title": "Shared Resource Control",
    "domain": "System & Communications Protection (SC)",
    "statement": "Prevent unauthorized and unintended information transfer via shared system resources.",
    "assessment_objectives": "[a] Shared resources identified;\n[b] Protections implemented.",
    "assessment_methods": "Examine: configs, virtualization settings;\n\nInterview: admins;\n\nTest: verify isolation.",
    "discussion": "Shared resources can leak data.",
    "further_discussion": "Example: VM isolation, memory protections.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Account Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.4"
  },
  {
    "requirement_id": "SC.L2-3.13.5",
    "title": "Public-Access System Separation [CUI Data]",
    "domain": "System & Communications Protection (SC)",
    "statement": "Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks.",
    "assessment_objectives": "[a] Public components identified;\n[b] Separation implemented.",
    "assessment_methods": "Examine: network diagrams, configs;\n\nInterview: admins;\n\nTest: verify separation.",
    "discussion": "Separation protects internal systems from public exposure.",
    "further_discussion": "Example: DMZ for web servers.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Each site has a different subnet.",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.5"
  },
  {
    "requirement_id": "SC.L2-3.13.6",
    "title": "Network Communication by Exception",
    "domain": "System & Communications Protection (SC)",
    "statement": "Deny network communications traffic by default and allow network communications traffic by exception (i.e., deny all, permit by exception).",
    "assessment_objectives": "[a] Default deny implemented;\n[b] Exceptions defined;\n[c] Exceptions enforced.",
    "assessment_methods": "Examine: firewall rules, ACLs;\n\nInterview: admins;\n\nTest: verify deny-by-default.",
    "discussion": "Default deny reduces attack surface.",
    "further_discussion": "Example: block all ports except 443.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Implemented through Firewall on router",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.6"
  },
  {
    "requirement_id": "SC.L2-3.13.7",
    "title": "Split Tunneling",
    "domain": "System & Communications Protection (SC)",
    "statement": "Prevent remote devices from simultaneously establishing non-remote connections with organizational systems and communicating via external networks (i.e., split tunneling).",
    "assessment_objectives": "[a] Split tunneling prevented;\n[b] Enforcement implemented.",
    "assessment_methods": "Examine: VPN configs, policies;\n\nInterview: admins;\n\nTest: attempt split tunneling.",
    "discussion": "Split tunneling bypasses protections.",
    "further_discussion": "Example: force all traffic through VPN.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Not Applicable",
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.7"
  },
  {
    "requirement_id": "SC.L2-3.13.8",
    "title": "Data in Transit",
    "domain": "System & Communications Protection (SC)",
    "statement": "Protect the confidentiality of CUI at rest and in transit.",
    "assessment_objectives": "[a] Confidentiality protections defined;\n[b] Protections enforced.",
    "assessment_methods": "Examine: encryption configs, TLS settings;\n\nInterview: admins;\n\nTest: verify encryption.",
    "discussion": "Encryption protects CUI in transit.",
    "further_discussion": "Example: TLS 1.2+ for web traffic.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Use of SSL certificate for email comunications",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.8"
  },
  {
    "requirement_id": "SC.L2-3.13.9",
    "title": "Connections Termination",
    "domain": "System & Communications Protection (SC)",
    "statement": "Terminate network connections associated with communications sessions at the end of the sessions or after a defined period of inactivity.",
    "assessment_objectives": "[a] Termination conditions defined;\n[b] Termination enforced.",
    "assessment_methods": "Examine: configs, logs;\n\nInterview: admins;\n\nTest: session termination.",
    "discussion": "Prevents hijacking of idle sessions.",
    "further_discussion": "Example: VPN disconnect after 30 minutes idle.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Terminal Server Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.9"
  },
  {
    "requirement_id": "SC.L2-3.13.10",
    "title": "Key Management",
    "domain": "System & Communications Protection (SC)",
    "statement": "Establish and manage cryptographic keys for cryptography employed in organizational systems.",
    "assessment_objectives": "[a] Key management policy defined;\n[b] Keys generated securely;\n[c] Keys distributed securely;\n[d] Keys stored securely;\n[e] Keys retired/destroyed securely.",
    "assessment_methods": "Examine: key management policy, HSM configs;\n\nInterview: admins;\n\nTest: key lifecycle.",
    "discussion": "Proper key management is critical for encryption.",
    "further_discussion": "Example: use HSMs, rotate keys regularly.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Drive encryption",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.10"
  },
  {
    "requirement_id": "SC.L2-3.13.11",
    "title": "CUI Encryption",
    "domain": "System & Communications Protection (SC)",
    "statement": "Employ FIPS-validated cryptography when used to protect the confidentiality of CUI.",
    "assessment_objectives": "[a] FIPS-validated cryptography identified;\n[b] Cryptography implemented.",
    "assessment_methods": "Examine: crypto configs, FIPS validation docs;\n\nInterview: admins;\n\nTest: verify crypto modules.",
    "discussion": "FIPS validation ensures compliance with federal standards.",
    "further_discussion": "Example: AES-256 FIPS-validated modules.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Not Applicable",
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.11"
  },
  {
    "requirement_id": "SC.L2-3.13.12",
    "title": "Collaborative Device Control",
    "domain": "System & Communications Protection (SC)",
    "statement": "Prohibit remote activation of collaborative computing devices and provide indication of devices in use to users present at the device.",
    "assessment_objectives": "[a] Remote activation prohibited;\n[b] Indication provided.",
    "assessment_methods": "Examine: device configs, policies;\n\nInterview: users;\n\nTest: attempt remote activation.",
    "discussion": "Prevents unauthorized surveillance.",
    "further_discussion": "Example: webcams with indicator lights.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools. (Terminal Server Security Policies)",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.12"
  },
  {
    "requirement_id": "SC.L2-3.13.13",
    "title": "Mobile Code",
    "domain": "System & Communications Protection (SC)",
    "statement": "Control and monitor the use of mobile code.",
    "assessment_objectives": "[a] Mobile code use defined;\n[b] Controls implemented;\n[c] Controls enforced.",
    "assessment_methods": "Examine: policies, configs;\n\nInterview: admins;\n\nTest: verify mobile code controls.",
    "discussion": "Mobile code (Java, ActiveX) can introduce vulnerabilities.",
    "further_discussion": "Example: restrict unsigned scripts.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Planned or Not Implemented",
    "Control Provider": "Provided By External Service Provider",
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.13"
  },
  {
    "requirement_id": "SC.L2-3.13.14",
    "title": "Voice over Internet Protocol",
    "domain": "System & Communications Protection (SC)",
    "statement": "Control and monitor the use of Voice over Internet Protocol (VoIP) technologies.",
    "assessment_objectives": "[a] VoIP use defined;\n[b] Controls implemented;\n[c] Controls enforced.",
    "assessment_methods": "Examine: VoIP configs, policies;\n\nInterview: admins;\n\nTest: verify VoIP controls.",
    "discussion": "VoIP can be exploited if not secured.",
    "further_discussion": "Example: encrypt VoIP traffic, restrict devices.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Planned or Not Implemented",
    "Control Provider": "Provided By External Service Provider",
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.14"
  },
  {
    "requirement_id": "SC.L2-3.13.15",
    "title": "Communications Authenticity",
    "domain": "System & Communications Protection (SC)",
    "statement": "Protect the authenticity of communications sessions.",
    "assessment_objectives": "[a] Authenticity protections defined;\n[b] Protections enforced.",
    "assessment_methods": "Examine: configs, protocols;\n\nInterview: admins;\n\nTest: verify authenticity.",
    "discussion": "Authenticity prevents spoofing and MITM attacks.",
    "further_discussion": "Example: digital signatures, TLS certificates.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Managed By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Using default Microsoft Domain Controllers tools & data encrytion",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.15"
  },
  {
    "requirement_id": "SC.L2-3.13.16",
    "title": "Data at Rest",
    "domain": "System & Communications Protection (SC)",
    "statement": "Protect the confidentiality of CUI at rest.",
    "assessment_objectives": "[a] Confidentiality protections defined;\n[b] Protections enforced.",
    "assessment_methods": "Examine: encryption configs, storage policies;\n\nInterview: admins;\n\nTest: verify encryption.",
    "discussion": "Encryption protects stored CUI.",
    "further_discussion": "Example: full-disk encryption on laptops.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, mananaged antivirus, and ticketing system, servers encryption",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.13.16"
  },
  {
    "requirement_id": "SI.L2-3.14.1",
    "title": "Flaw Remediation [CUI Data]",
    "domain": "System & Information Integrity (SI)",
    "statement": "Identify, report, and correct system flaws in a timely manner.",
    "assessment_objectives": "[a] Flaws identified;\n[b] Flaws reported;\n[c] Flaws corrected;\n[d] Timeliness defined and enforced.",
    "assessment_methods": "Examine: patch management policy, vulnerability reports, remediation logs;\n\nInterview: admins;\n\nTest: patch deployment.",
    "discussion": "Timely remediation reduces exposure to exploits.",
    "further_discussion": "Example: apply vendor patches within 30 days of release.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, mananaged antivirus",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.14.1"
  },
  {
    "requirement_id": "SI.L2-3.14.2",
    "title": "Malicious Code Protection [CUI Data]",
    "domain": "System & Information Integrity (SI)",
    "statement": "Provide protection from malicious code at appropriate locations within organizational systems.",
    "assessment_objectives": "[a] Malicious code protection capability implemented;\n[b] Protection applied at appropriate locations;\n[c] Protection updated.",
    "assessment_methods": "Examine: AV/EDR configs, logs;\n\nInterview: admins;\n\nTest: malware detection.",
    "discussion": "Malware protection is essential for safeguarding CUI.",
    "further_discussion": "Example: endpoint protection on servers, workstations, and email gateways.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": "Implemented",
    "Control Provider": "Configured By On-Site Technology",
    "What is the Solution?\nHow is it implemented?": "Computer Mangement Agent, mananaged antivirus",
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.14.2"
  },
  {
    "requirement_id": "SI.L2-3.14.3",
    "title": "Security Alerts & Advisories",
    "domain": "System & Information Integrity (SI)",
    "statement": "Monitor system security alerts and advisories and take action in response.",
    "assessment_objectives": "[a] Alerts/advisories monitored;\n[b] Actions taken in response;\n[c] Actions documented.",
    "assessment_methods": "Examine: threat intel feeds, patch advisories, response logs;\n\nInterview: admins;\n\nTest: review alert handling.",
    "discussion": "Staying current on threats enables proactive defense.",
    "further_discussion": "Example: subscribe to US-CERT alerts and patch accordingly.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.14.3"
  },
  {
    "requirement_id": "SI.L2-3.14.4",
    "title": "Update Malicious Code Protection [CUI Data]",
    "domain": "System & Information Integrity (SI)",
    "statement": "Update malicious code protection mechanisms when new releases are available.",
    "assessment_objectives": "[a] Updates identified;\n[b] Updates applied;\n[c] Updates verified.",
    "assessment_methods": "Examine: AV/EDR update logs, configs;\n\nInterview: admins;\n\nTest: verify update status.",
    "discussion": "Frequent updates ensure protection against new threats.",
    "further_discussion": "Example: daily signature updates for antivirus.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.14.4"
  },
  {
    "requirement_id": "SI.L2-3.14.5",
    "title": "System & File Scanning [CUI Data]",
    "domain": "System & Information Integrity (SI)",
    "statement": "Perform periodic scans of organizational systems and real-time scans of files from external sources as files are downloaded, opened, or executed.",
    "assessment_objectives": "[a] Periodic scans performed;\n[b] Real-time scans performed;\n[c] Scans cover external files;\n[d] Results reviewed.",
    "assessment_methods": "Examine: scan schedules, logs;\n\nInterview: admins;\n\nTest: run scan.",
    "discussion": "Scanning detects malware and unauthorized changes.",
    "further_discussion": "Example: weekly full scans, real-time scanning of email attachments.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.14.5"
  },
  {
    "requirement_id": "SI.L2-3.14.6",
    "title": "Monitor Communications for Attacks",
    "domain": "System & Information Integrity (SI)",
    "statement": "Monitor organizational systems, including inbound and outbound communications traffic, to detect attacks and indicators of potential attacks.",
    "assessment_objectives": "[a] Monitoring capability implemented;\n[b] Monitoring covers inbound/outbound traffic;\n[c] Indicators of attack detected;\n[d] Alerts generated.",
    "assessment_methods": "Examine: IDS/IPS configs, SIEM dashboards;\n\nInterview: SOC staff;\n\nTest: simulate attack traffic.",
    "discussion": "Monitoring detects intrusions and anomalies.",
    "further_discussion": "Example: IDS alerts on port scans or brute-force attempts.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.14.6"
  },
  {
    "requirement_id": "SI.L2-3.14.7",
    "title": "Identify Unauthorized Use",
    "domain": "System & Information Integrity (SI)",
    "statement": "Identify unauthorized use of organizational systems.",
    "assessment_objectives": "[a] Unauthorized use defined;\n[b] Unauthorized use detected;\n[c] Unauthorized use reported;\n[d] Unauthorized use remediated.",
    "assessment_methods": "Examine: monitoring policies, logs;\n\nInterview: admins;\n\nTest: review detection of unauthorized activity.",
    "discussion": "Detecting unauthorized use prevents insider and outsider threats.",
    "further_discussion": "Example: alert on use of unauthorized software or accounts.",
    "Assesment Findings": None,
    "Self-Reported Implementation Status": None,
    "Control Provider": None,
    "What is the Solution?\nHow is it implemented?": None,
    "Documentation": None,
    "Key References": "NIST SP 800-171 Rev. 2 3.14.7"
  }
]

from sqlmodel import select, Session
with Session(engine) as s:
    cnt = s.exec(select(Control)).all()
    if not cnt:
        for row in SEED:
            s.add(Control(**row))
        s.commit()
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/controls")
async def list_controls(q: Optional[str] = None, domain: Optional[str] = None, session: Session = Depends(get_session)):
    stmt = select(Control)
    rows = session.exec(stmt).all()
    if domain:
        rows = [r for r in rows if r.domain.lower() == domain.lower()]
    if q:
        needle = q.strip().lower()
        rows = [r for r in rows if any([
            needle in (r.title or '').lower(),
            needle in (r.statement or '').lower(),
            needle in (r.requirement_id or '').lower(),
            needle in (r.domain or '').lower()
        ])]
    return rows

@app.get("/controls/{control_id}")
async def get_control(control_id: int, session: Session = Depends(get_session)):
    c = session.get(Control, control_id)
    if not c:
        raise HTTPException(404, "Control not found")
    return c

from pydantic import BaseModel
class ControlUpdate(BaseModel):
    c3pao_finding: Optional[str] = None
    self_impl_status: Optional[str] = None

@app.patch("/controls/{control_id}")
async def update_control(control_id: int, payload: ControlUpdate, session: Session = Depends(get_session)):
    c = session.get(Control, control_id)
    if not c:
        raise HTTPException(404, "Control not found")
    if payload.c3pao_finding is not None:
        c.c3pao_finding = payload.c3pao_finding
    if payload.self_impl_status is not None:
        c.self_impl_status = payload.self_impl_status
    session.add(c)
    session.commit()
    session.refresh(c)
    return c
C3PAO_STATUS_BUCKETS = ["MET", "NOT_MET", "NA", "UNASSIGNED"]
SELF_IMPL_STATUS_BUCKETS = [
    "Implemented",
    "Partially Implemented",
    "Planned or Not Implemented",
    "Alternative Implementation",
    "N/A",
    "UNASSIGNED",
]


@app.get("/dashboard")
async def dashboard(session: Session = Depends(get_session)):
    rows = session.exec(select(Control)).all()
    total = len(rows)
    c3pao_counts = Counter((r.c3pao_finding or "UNASSIGNED") for r in rows)
    impl_counts = Counter((r.self_impl_status or "UNASSIGNED") for r in rows)

    for bucket in C3PAO_STATUS_BUCKETS:
        c3pao_counts.setdefault(bucket, 0)
    for bucket in SELF_IMPL_STATUS_BUCKETS:
        impl_counts.setdefault(bucket, 0)

    return {
        "total": total,
        "c3pao": dict(c3pao_counts),
        "impl": dict(impl_counts),
    }

class TextLogIn(BaseModel):
    kind: str
    text: str

@app.post("/controls/{requirement_id}/textlog")
async def add_textlog(requirement_id: str, payload: TextLogIn, session: Session = Depends(get_session)):
    entry = TextLog(requirement_id=requirement_id, kind=payload.kind, text=payload.text)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

@app.get("/controls/{requirement_id}/textlog")
async def list_textlog(requirement_id: str, kind: Optional[str]=None, session: Session = Depends(get_session)):
    q = select(TextLog).where(TextLog.requirement_id==requirement_id)
    rows = session.exec(q).all()
    if kind:
        rows = [r for r in rows if r.kind==kind]
    rows.sort(key=lambda x: x.ts)
    return rows

@app.delete("/textlog/{log_id}")
async def delete_textlog(log_id: int, session: Session = Depends(get_session)):
    row = session.get(TextLog, log_id)
    if not row:
        raise HTTPException(404, "Log not found")
    session.delete(row)
    session.commit()
    return {"ok": True}
@app.post("/controls/{requirement_id}/evidence")
async def upload_evidence(requirement_id: str, files: List[UploadFile]=File(...), session: Session = Depends(get_session)):
    saved = []
    target = os.path.join(UPLOAD_DIR, requirement_id)
    os.makedirs(target, exist_ok=True)
    for uf in files:
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        safe_name = f"{ts}__{uf.filename}"
        dest = os.path.join(target, safe_name)
        with open(dest, "wb") as out:
            shutil.copyfileobj(uf.file, out)
        meta = Evidence(requirement_id=requirement_id, filename=uf.filename, size=os.path.getsize(dest), path=dest)
        session.add(meta)
        session.commit()
        session.refresh(meta)
        saved.append(meta)
    return saved

@app.get("/controls/{requirement_id}/evidence")
async def list_evidence(requirement_id: str, session: Session = Depends(get_session)):
    q = select(Evidence).where(Evidence.requirement_id==requirement_id)
    rows = session.exec(q).all()
    rows.sort(key=lambda x: x.ts)
    return rows

@app.delete("/evidence/{evidence_id}")
async def delete_evidence(evidence_id: int, session: Session = Depends(get_session)):
    row = session.get(Evidence, evidence_id)
    if not row:
        raise HTTPException(404, "Evidence not found")
    try:
        if os.path.exists(row.path):
            os.remove(row.path)
    except Exception:
        pass
    session.delete(row)
    session.commit()
    return {"ok": True}
