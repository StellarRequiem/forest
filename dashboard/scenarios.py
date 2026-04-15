"""
Forest Blue-Team Trainer — Scenario Bank
All scenario data in one place. Easy to extend.

Each scenario dict has:
  phishing/url:
    prompt      — the email or URL shown to the user
    answer      — "phishing"/"safe" or "high"/"medium"/"low"
    explanation — shown after answering
    hint        — shown on wrong answer
    category    — for filtering/stats

  password:
    password    — the password to evaluate
    rating      — "weak"/"moderate"/"strong"
    issues      — list of problems (shown in feedback)
    good_points — list of strengths
"""

# ── Phishing email scenarios ──────────────────────────────────────────────────
# 20 scenarios across 5 categories

PHISHING_SCENARIOS = [
    # ── Urgency / Account threat ──
    {
        "category": "Account Threat",
        "prompt": (
            "Subject: URGENT — Your Microsoft account has been suspended\n\n"
            "We detected unusual activity on your account. Your access will be "
            "permanently disabled in 24 hours unless you verify your identity.\n\n"
            "Click here to restore access: https://microsoft-verify-secure.com/login"
        ),
        "answer": "phishing",
        "explanation": "Microsoft never sends suspension notices with third-party links. The domain 'microsoft-verify-secure.com' is not Microsoft.",
        "hint": "Look at the URL domain — is it actually microsoft.com?",
        "category": "Account Threat",
    },
    {
        "category": "Account Threat",
        "prompt": (
            "Subject: Your PayPal account is limited\n\n"
            "We've noticed some unusual activity and temporarily limited your account. "
            "To restore full access, please confirm your information:\n\n"
            "https://www.paypal.com/signin"
        ),
        "answer": "safe",
        "explanation": "This URL (paypal.com/signin) is the legitimate PayPal sign-in page. Subject lines like this are common phishing hooks, but the link itself is real here.",
        "hint": "Check the domain carefully — is this actually paypal.com?",
        "category": "Account Threat",
    },
    {
        "category": "Account Threat",
        "prompt": (
            "Subject: Your Apple ID has been locked\n\n"
            "Your Apple ID was used to sign in on a new device in Russia. "
            "If this wasn't you, your account may be compromised.\n\n"
            "Verify: https://appleid.apple.com/account/manage"
        ),
        "answer": "safe",
        "explanation": "appleid.apple.com is Apple's legitimate domain. This exact message format is used by Apple for real sign-in alerts.",
        "hint": "Is this Apple's actual domain?",
        "category": "Account Threat",
    },
    {
        "category": "Account Threat",
        "prompt": (
            "Subject: Action Required: Unusual sign-in to your Google Account\n\n"
            "We blocked a sign-in attempt from Bulgaria (IP: 185.220.101.55). "
            "Secure your account immediately:\n\n"
            "https://accounts.google.com-security.net/verify"
        ),
        "answer": "phishing",
        "explanation": "The domain is 'google.com-security.net' — NOT google.com. Attackers add legitimate brand names as subdomains of their own domains.",
        "hint": "Read the full domain carefully. What comes after the last dot before /verify?",
        "category": "Account Threat",
    },

    # ── Prize / Reward ──
    {
        "category": "Prize / Reward",
        "prompt": (
            "Subject: Congratulations! You've been selected for a $500 Amazon Gift Card\n\n"
            "You are today's lucky winner! Claim your gift card before it expires:\n\n"
            "https://amazon-rewards-winner.com/claim?id=84729"
        ),
        "answer": "phishing",
        "explanation": "Amazon does not send unsolicited gift card emails. The domain is not amazon.com.",
        "hint": "Did you enter any Amazon contest recently?",
        "category": "Prize / Reward",
    },
    {
        "category": "Prize / Reward",
        "prompt": (
            "Subject: Your Amazon order has shipped — Track your package\n\n"
            "Order #112-8472930-1928374 has shipped.\n"
            "Estimated delivery: Tomorrow by 8pm\n\n"
            "Track: https://www.amazon.com/gp/css/order-history"
        ),
        "answer": "safe",
        "explanation": "This is a standard Amazon shipping notification. The link goes to amazon.com's order history — a legitimate page.",
        "hint": "Check the sender domain and the link domain.",
        "category": "Prize / Reward",
    },

    # ── Financial / Invoice ──
    {
        "category": "Financial",
        "prompt": (
            "Subject: Invoice #INV-2847 from QuickBooks — Payment due\n\n"
            "You have a new invoice for $3,247.00 from Acme Supplies LLC.\n"
            "Pay now to avoid late fees:\n\n"
            "https://qbo.intuit.com/app/invoice?id=2847"
        ),
        "answer": "safe",
        "explanation": "qbo.intuit.com is QuickBooks Online's legitimate domain. This is a real invoice notification format.",
        "hint": "Is qbo.intuit.com a real QuickBooks domain?",
        "category": "Financial",
    },
    {
        "category": "Financial",
        "prompt": (
            "Subject: Wire Transfer Confirmation Required — $47,500\n\n"
            "This is your CFO. I need you to initiate a wire transfer of $47,500 "
            "to our new vendor before end of day. Keep this confidential.\n\n"
            "Reply to: john.cfo.urgent@gmail.com"
        ),
        "answer": "phishing",
        "explanation": "This is a classic Business Email Compromise (BEC) attack. Real CFOs use company email, not Gmail. Wire transfers are never initiated by email alone.",
        "hint": "Why would the CFO use a Gmail address?",
        "category": "Financial",
    },
    {
        "category": "Financial",
        "prompt": (
            "Subject: Your bank statement is ready\n\n"
            "Your monthly statement for account ending in 4821 is ready to view.\n\n"
            "https://secure.wellsfargo.com/accounts/statements"
        ),
        "answer": "safe",
        "explanation": "secure.wellsfargo.com is Wells Fargo's legitimate secure domain. Banks do send statement ready notifications with direct links to their own domains.",
        "hint": "Is this Wells Fargo's actual domain?",
        "category": "Financial",
    },
    {
        "category": "Financial",
        "prompt": (
            "Subject: IRS: Final Notice — Unpaid Tax Liability\n\n"
            "You have an unpaid federal tax debt of $2,847.00. Failure to pay "
            "within 48 hours will result in asset seizure and arrest warrant.\n\n"
            "Pay immediately: https://irs-payment-portal.com/pay"
        ),
        "answer": "phishing",
        "explanation": "The IRS never threatens immediate arrest via email, and never uses domains other than irs.gov. This is a fear-based scam.",
        "hint": "Does the IRS contact people via email for urgent tax debt?",
        "category": "Financial",
    },

    # ── IT / Helpdesk ──
    {
        "category": "IT / Helpdesk",
        "prompt": (
            "Subject: IT Security: Your password expires in 1 day\n\n"
            "Your network password will expire tomorrow. Reset it now to avoid "
            "losing access to all company systems:\n\n"
            "https://company-password-reset.com/renew"
        ),
        "answer": "phishing",
        "explanation": "Legitimate IT password reset links come from your company's own domain (e.g., company.com), not external sites like 'company-password-reset.com'.",
        "hint": "Would your company IT team use a .com domain for internal password resets?",
        "category": "IT / Helpdesk",
    },
    {
        "category": "IT / Helpdesk",
        "prompt": (
            "Subject: Zoom Meeting Invitation from Sarah Chen\n\n"
            "Sarah Chen is inviting you to a scheduled Zoom meeting.\n\n"
            "Time: Jan 15, 2026 10:00 AM Pacific\n"
            "Join Zoom Meeting: https://zoom.us/j/94832847392\n\n"
            "Password: 847293"
        ),
        "answer": "safe",
        "explanation": "zoom.us/j/ is Zoom's legitimate meeting link format. This is a standard Zoom invitation.",
        "hint": "Is zoom.us the legitimate Zoom domain?",
        "category": "IT / Helpdesk",
    },
    {
        "category": "IT / Helpdesk",
        "prompt": (
            "Subject: [ACTION REQUIRED] DocuSign: Sign the attached NDA\n\n"
            "You have a document ready for signature.\n\n"
            "Sign here: https://docusign.net-signature-request.com/sign?token=8d7f2a"
        ),
        "answer": "phishing",
        "explanation": "DocuSign uses docusign.com — not 'docusign.net-signature-request.com'. The legitimate domain is being used as a subdomain of an attacker's site.",
        "hint": "What is the actual registrable domain here?",
        "category": "IT / Helpdesk",
    },

    # ── Delivery / Package ──
    {
        "category": "Delivery",
        "prompt": (
            "Subject: Your FedEx package could not be delivered\n\n"
            "We attempted to deliver your package but no one was home. "
            "A $2.99 redelivery fee is required:\n\n"
            "https://fedex-delivery-reschedule.com/pay"
        ),
        "answer": "phishing",
        "explanation": "FedEx never charges a redelivery fee online and uses fedex.com only. This is a common package delivery scam.",
        "hint": "When did FedEx start charging redelivery fees?",
        "category": "Delivery",
    },
    {
        "category": "Delivery",
        "prompt": (
            "Subject: Your UPS shipment 1Z999AA10123456784 is out for delivery\n\n"
            "Your package will be delivered today by 7:00 PM.\n\n"
            "Track your shipment: https://www.ups.com/track?tracknum=1Z999AA10123456784"
        ),
        "answer": "safe",
        "explanation": "ups.com is UPS's legitimate domain. This matches the standard UPS shipment notification format.",
        "hint": "Is ups.com UPS's real domain?",
        "category": "Delivery",
    },

    # ── Social ──
    {
        "category": "Social",
        "prompt": (
            "Subject: You have a new LinkedIn connection request\n\n"
            "John Smith, VP at Goldman Sachs, wants to connect with you on LinkedIn.\n\n"
            "View profile: https://www.linkedin.com/in/johnsmith-gs"
        ),
        "answer": "safe",
        "explanation": "linkedin.com is LinkedIn's real domain. Standard connection request emails link directly to linkedin.com profiles.",
        "hint": "Is linkedin.com LinkedIn's real domain?",
        "category": "Social",
    },
    {
        "category": "Social",
        "prompt": (
            "Subject: Someone shared a file with you on Google Drive\n\n"
            "Jennifer Martinez has shared 'Q4 Salary Adjustments.xlsx' with you.\n\n"
            "Open: https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"
        ),
        "answer": "safe",
        "explanation": "drive.google.com is Google Drive's legitimate domain. Sharing files from real Drive accounts is a normal workflow.",
        "hint": "Is drive.google.com legitimate?",
        "category": "Social",
    },
    {
        "category": "Social",
        "prompt": (
            "Subject: Your friend tagged you in a photo\n\n"
            "Mike Johnson tagged you in a photo on Facebook. You might not like this!\n\n"
            "View photo: https://facebook-photos-viewer.com/tagged/you?id=44821"
        ),
        "answer": "phishing",
        "explanation": "Facebook photo tags link to facebook.com, not 'facebook-photos-viewer.com'. This is credential harvesting.",
        "hint": "Would Facebook send you to a non-facebook.com domain?",
        "category": "Social",
    },
    {
        "category": "Social",
        "prompt": (
            "Subject: Verify your Twitter/X account before suspension\n\n"
            "Your account has been flagged for review. Verify within 12 hours "
            "or lose your blue check and followers permanently.\n\n"
            "Verify: https://twitter-account-verify.info/confirm"
        ),
        "answer": "phishing",
        "explanation": "X/Twitter uses twitter.com and x.com only. The domain 'twitter-account-verify.info' is a phishing site.",
        "hint": "Twitter's domain ends in .com — what does this one end in?",
        "category": "Social",
    },

    # ── macOS-specific ──
    {
        "category": "macOS",
        "prompt": (
            "Subject: Your Mac requires a security update — action needed\n\n"
            "Apple Security has detected a critical vulnerability on your Mac. "
            "Install the patch immediately to prevent data loss:\n\n"
            "https://macos-security-patch.com/update?device=MacBookPro"
        ),
        "answer": "phishing",
        "explanation": "Apple delivers macOS updates only through System Settings → Software Update, never via email links to third-party domains.",
        "hint": "How does macOS normally deliver security updates?",
        "category": "macOS",
    },
    {
        "category": "macOS",
        "prompt": (
            "Subject: iCloud storage is almost full — upgrade now\n\n"
            "Your iCloud storage (5 GB plan) is 95% full. Photos and backups "
            "will stop syncing. Upgrade your storage:\n\n"
            "https://www.apple.com/icloud/#plans"
        ),
        "answer": "safe",
        "explanation": "apple.com/icloud is Apple's legitimate iCloud page. Apple does send genuine storage alerts linking to their own domain.",
        "hint": "Is apple.com Apple's real domain?",
        "category": "macOS",
    },
    {
        "category": "macOS",
        "prompt": (
            "Subject: Gatekeeper alert — malware found on your Mac\n\n"
            "Our scan detected MacStealer malware on your device. Your passwords "
            "and crypto wallets may be at risk.\n\n"
            "Remove it now: https://mac-malware-remover.net/clean"
        ),
        "answer": "phishing",
        "explanation": "Gatekeeper never sends emails. Unsolicited 'malware found' emails are scareware — clicking the link typically installs the actual malware.",
        "hint": "Does Apple's Gatekeeper communicate by email?",
        "category": "macOS",
    },

    # ── AI / LLM social engineering ──
    {
        "category": "AI / LLM",
        "prompt": (
            "Subject: Your ChatGPT Plus subscription is expiring\n\n"
            "Your ChatGPT Plus subscription expires in 48 hours. "
            "Renew now to keep GPT-4 access:\n\n"
            "https://chatgpt-plus-renew.com/billing"
        ),
        "answer": "phishing",
        "explanation": "OpenAI manages subscriptions at platform.openai.com only. 'chatgpt-plus-renew.com' is a credential-harvesting site targeting AI users.",
        "hint": "What domain does OpenAI use for billing?",
        "category": "AI / LLM",
    },
    {
        "category": "AI / LLM",
        "prompt": (
            "Subject: Anthropic: Verify your Claude account\n\n"
            "We noticed a login from an unrecognized device. Verify your "
            "identity to keep your Claude Pro access:\n\n"
            "https://claude.anthropic.com/verify"
        ),
        "answer": "safe",
        "explanation": "claude.anthropic.com is Anthropic's legitimate subdomain. This format matches real account verification emails from Anthropic.",
        "hint": "Is claude.anthropic.com a real Anthropic domain?",
        "category": "AI / LLM",
    },
    {
        "category": "AI / LLM",
        "prompt": (
            "Subject: You've been invited to join an exclusive AI safety research group\n\n"
            "I'm a researcher at a leading AI lab. We're building a private "
            "community of security professionals. Join here and share your "
            "current projects:\n\n"
            "https://ai-safety-researchers.io/join?ref=security"
        ),
        "answer": "phishing",
        "explanation": "Unsolicited 'exclusive research group' invitations are social engineering. Sharing your active projects with unknown parties is an intelligence gathering attack.",
        "hint": "Why would a real research group cold-email you to share confidential projects?",
        "category": "AI / LLM",
    },
]


# ── URL risk scenarios ─────────────────────────────────────────────────────────
# 15 scenarios: high / medium / low risk

URL_SCENARIOS = [
    {
        "url": "https://paypa1.com/signin",
        "risk": "high",
        "explanation": "Typosquatting — '1' replaces 'l' in PayPal. Classic credential harvesting domain.",
        "hint": "Look at every character of the domain.",
        "category": "Typosquatting",
    },
    {
        "url": "https://www.paypal.com/signin",
        "risk": "low",
        "explanation": "Legitimate PayPal sign-in URL. HTTPS, correct domain, standard path.",
        "hint": "Is this the real paypal.com?",
        "category": "Legitimate",
    },
    {
        "url": "http://192.168.1.1/admin",
        "risk": "medium",
        "explanation": "Private IP address (RFC 1918). Accessing router admin from an email link is dangerous. HTTP, no encryption.",
        "hint": "Should you ever reach a router admin page from an email?",
        "category": "IP Address",
    },
    {
        "url": "https://accounts.google.com.login-verify.net/signin",
        "risk": "high",
        "explanation": "The real domain is 'login-verify.net'. 'accounts.google.com' is just the subdomain — controlled by the attacker.",
        "hint": "What domain comes right before the first single slash?",
        "category": "Subdomain Abuse",
    },
    {
        "url": "https://github.com/anthropics/anthropic-sdk-python",
        "risk": "low",
        "explanation": "Legitimate GitHub repository. HTTPS, real github.com domain, standard path format.",
        "hint": "Is github.com GitHub's real domain?",
        "category": "Legitimate",
    },
    {
        "url": "http://bit.ly/3xK9pQr",
        "risk": "medium",
        "explanation": "URL shortener — you cannot see the real destination. HTTP, not HTTPS. Always preview shortened URLs before clicking.",
        "hint": "Can you tell where this actually goes?",
        "category": "URL Shortener",
    },
    {
        "url": "https://secure-microsoft-login.com/office365",
        "risk": "high",
        "explanation": "Microsoft uses microsoft.com and office.com. 'secure-microsoft-login.com' is an attacker-controlled phishing domain.",
        "hint": "Is 'secure-microsoft-login.com' a Microsoft domain?",
        "category": "Brand Impersonation",
    },
    {
        "url": "https://www.amazon.com/dp/B08N5WRWNW",
        "risk": "low",
        "explanation": "Legitimate Amazon product page. HTTPS, amazon.com domain, standard product path.",
        "hint": "Is amazon.com Amazon's real domain?",
        "category": "Legitimate",
    },
    {
        "url": "https://dropbox.com.file-share.ru/document.pdf",
        "risk": "high",
        "explanation": "The domain is 'file-share.ru' (.ru = Russia). Dropbox is a subdomain. This is a phishing page, likely credential harvesting.",
        "hint": "What country code TLD does this end with?",
        "category": "Subdomain Abuse",
    },
    {
        "url": "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs/view",
        "risk": "low",
        "explanation": "Legitimate Google Drive share link. HTTPS, drive.google.com domain, standard file share path.",
        "hint": "Is drive.google.com legitimate?",
        "category": "Legitimate",
    },
    {
        "url": "https://zoom.us.meeting-join-now.com/j/938472847",
        "risk": "high",
        "explanation": "The domain is 'meeting-join-now.com'. 'zoom.us' is just a subdomain — attacker-controlled. Real Zoom links use zoom.us only.",
        "hint": "Read the full domain from right to left.",
        "category": "Subdomain Abuse",
    },
    {
        "url": "ftp://files.internal-corp.example.com/report.xlsx",
        "risk": "medium",
        "explanation": "FTP is unencrypted — file transfers are visible on the network. Should use SFTP or HTTPS for file sharing.",
        "hint": "Is FTP a secure protocol?",
        "category": "Insecure Protocol",
    },
    {
        "url": "https://appleid.apple.com/account/manage",
        "risk": "low",
        "explanation": "Legitimate Apple ID management page. HTTPS, appleid.apple.com is Apple's real domain.",
        "hint": "Is appleid.apple.com Apple's real domain?",
        "category": "Legitimate",
    },
    {
        "url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "risk": "low",
        "explanation": "Legitimate Microsoft OAuth endpoint. microsoftonline.com is Microsoft's authentication domain for Azure/Office 365.",
        "hint": "Is microsoftonline.com a real Microsoft domain?",
        "category": "Legitimate",
    },
    {
        "url": "https://wellsfargo.com.account-secure.info/login",
        "risk": "high",
        "explanation": "Domain is 'account-secure.info'. Wells Fargo is a subdomain. Banks only authenticate on their own registered domains.",
        "hint": "What is the actual registrable domain here?",
        "category": "Brand Impersonation",
    },
]


# ── Password test cases ────────────────────────────────────────────────────────

def evaluate_password(pw: str) -> dict:
    """
    Score a password across 6 dimensions. Returns dict with score (0-100),
    rating, issues, and good_points.
    """
    import re
    issues      = []
    good_points = []
    score       = 0

    # Length
    if len(pw) >= 16:
        score += 30
        good_points.append(f"Good length ({len(pw)} characters)")
    elif len(pw) >= 12:
        score += 20
        good_points.append(f"Acceptable length ({len(pw)} characters)")
    elif len(pw) >= 8:
        score += 10
        issues.append(f"Short — only {len(pw)} characters. Aim for 16+")
    else:
        issues.append(f"Very short — only {len(pw)} characters. Minimum 12, ideally 16+")

    # Character classes
    has_upper   = bool(re.search(r"[A-Z]", pw))
    has_lower   = bool(re.search(r"[a-z]", pw))
    has_digit   = bool(re.search(r"\d", pw))
    has_special = bool(re.search(r"[^A-Za-z0-9]", pw))

    classes = sum([has_upper, has_lower, has_digit, has_special])
    score  += classes * 10

    if has_upper:    good_points.append("Has uppercase letters")
    else:            issues.append("No uppercase letters")
    if has_lower:    good_points.append("Has lowercase letters")
    else:            issues.append("No lowercase letters")
    if has_digit:    good_points.append("Has numbers")
    else:            issues.append("No numbers")
    if has_special:  good_points.append("Has special characters (!@#$…)")
    else:            issues.append("No special characters — add !@#$%^&*")

    # Common patterns
    common = ["password", "123456", "qwerty", "abc123", "letmein",
              "monkey", "dragon", "master", "shadow", "sunshine"]
    if any(c in pw.lower() for c in common):
        score  = max(0, score - 25)
        issues.append("Contains a common word/pattern — very easily guessed")

    # Keyboard walks
    walks = ["qwerty", "asdf", "zxcv", "1234", "4321"]
    if any(w in pw.lower() for w in walks):
        score  = max(0, score - 15)
        issues.append("Contains a keyboard walk pattern (qwerty, asdf, 1234…)")

    # Repeated characters
    if re.search(r"(.)\1{2,}", pw):
        score  = max(0, score - 10)
        issues.append("Has 3+ repeated characters in a row (aaa, 111…)")

    score = min(100, max(0, score))

    if score >= 75:
        rating = "strong"
    elif score >= 45:
        rating = "moderate"
    else:
        rating = "weak"

    return {
        "score":       score,
        "rating":      rating,
        "issues":      issues,
        "good_points": good_points,
    }
