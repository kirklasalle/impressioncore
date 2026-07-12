# PRISM LLM Provider OAuth Compatibility Matrix

This document provides a comprehensive research summary of OAuth 2.0 and Federated Identity support across all LLM providers currently supported by the PRISM framework. It guides the design and implementation of the **"Use OAuth Authentication"** option in the settings.

---

## 1. Provider Compatibility Matrix

| Provider ID | Provider Name | Direct OAuth 2.0 Support | Federated / Workload Identity | Authentication Mechanism | Recommended Implementation Pattern |
|:---|:---|:---:|:---:|:---|:---|
| **google** / **gemini-pro** | Google Vertex AI / AI Studio | **Yes** (Vertex) | **Yes** (GCP IAM) | Google OAuth Access Token / GCP Service Account credentials | Redirect to Google OAuth (scope: `cloud-platform`) to fetch token for Vertex AI endpoints. |
| **openai** | OpenAI | **No** | **Yes** (Beta) | Workload Identity Federation / Ephemeral Tokens | Use Server-Side client federation or standard API Keys. Direct user OAuth is not supported for public APIs. |
| **anthropic** / **claude-3-opus** | Anthropic Claude | **No** | **Yes** (Enterprise) | Workload Identity Federation | Route through AWS Bedrock/Vertex AI (which support IAM/OAuth) or fall back to standard API keys. |
| **azure** (Azure OpenAI) | Microsoft Azure | **Yes** | **Yes** (Entra ID) | Entra ID (Azure AD) OAuth Access Token | Redirect to Microsoft OAuth (scope: `cognitiveservices.azure.com/.default`). |
| **aws-bedrock** | Amazon Bedrock | **Yes** (via STS) | **Yes** (AWS IAM) | AWS STS AssumeRoleWithWebIdentity / OIDC | Use AWS Cognito or OIDC provider to assume an IAM role, yielding temporary session keys. |
| **mistral**, **cohere**, **groq**, **deepseek**, **perplexity**, **together**, **fireworks**, **openrouter** | Cloud API Providers | **No** | **No** | API Key only | Require standard API keys. Provide a secure API Key vaults manager. |
| **ollama**, **lmstudio**, **llamacpp**, **bitnetcpp** | Local Providers | **No** (N/A) | **No** (N/A) | None / Simple Bearer | Run locally on the operator's machine. No OAuth required. |

---

## 2. Deep Dive: Implementation Specifications for Supported OAuth Providers

### 2.1. Google Cloud / Vertex AI (`google`)
When the operator selects Vertex AI, PRISM can perform a standard Google OAuth 2.0 flow:
*   **Authorization Endpoint:** `https://accounts.google.com/o/oauth2/v2/auth`
*   **Token Endpoint:** `https://oauth2.googleapis.com/token`
*   **Requested Scope:** `https://www.googleapis.com/auth/cloud-platform`
*   **Prerequisites:** Operator must configure a Google Cloud Console Client ID and Client Secret in PRISM's advanced settings.
*   **Resulting Token:** OAuth Access Token passed in the header:
    `Authorization: Bearer <GCP_ACCESS_TOKEN>`

### 2.2. Microsoft Azure OpenAI (`azure`)
For Azure-hosted OpenAI models, Entra ID OAuth 2.0 can completely replace standard subscription keys:
*   **Authorization Endpoint:** `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`
*   **Token Endpoint:** `https://login.microsoftonline.com/common/oauth2/v2.0/token`
*   **Requested Scope:** `https://cognitiveservices.azure.com/.default`
*   **Prerequisites:** Operator must register an App Registration in Azure AD and provide the Tenant ID and Client ID.
*   **Resulting Token:** Microsoft Access Token passed in the header:
    `Authorization: Bearer <AZURE_ACCESS_TOKEN>`

### 2.3. Enterprise Workload Identity Federation (OpenAI / Anthropic)
For enterprise-grade deployments where static credentials are prohibited:
*   **Workflow:** PRISM integrates with an OIDC identity provider (e.g., Okta, Ping Identity, HashiCorp Vault).
*   **Token Exchange:** PRISM requests a token from the OIDC provider, then calls the OpenAI/Anthropic token exchange endpoint to receive a short-lived ephemeral session token.
*   **Benefit:** Eliminates hardcoded `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` from environment variables and local stores.

---

## 3. Settings UI Design: Key vs. OAuth Switcher

To offer OAuth dynamically, the settings dashboard configures the fields based on provider compatibility:

1.  **For OAuth-Enabled Providers (Google Vertex, Azure, Bedrock):**
    *   Show a slider or radio buttons: `[ API Key ] [ OAuth Login ]`.
    *   Selecting `OAuth Login` hides the API Key text input and displays:
        *   An status banner: `Status: Disconnected`.
        *   A prominent button: `🔒 Connect via OAuth`.
        *   Fields for `OAuth Client ID`, `Client Secret`, and `Tenant/Project ID` (if custom credentials are required).
2.  **For Non-OAuth Providers (DeepSeek, Perplexity, etc.):**
    *   Maintain the single standard API key configuration.
    *   Optionally provide an informational helper note: *"This provider only supports API Key authentication."*
