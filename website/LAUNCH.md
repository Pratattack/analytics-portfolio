# Domain connection and launch

The portfolio is deployed with ChatGPT Sites. No paid hosting subscription was purchased. GoDaddy remains the domain registrar. The domain records below were returned by the hosting provider on October 27, 2026.

## GoDaddy steps

1. Open your Domain Portfolio, select prathameshsingh.com, and select DNS.
2. Change the two existing parking A records for @ (currently 76.223.105.230 and 13.248.243.5) to the two A values below.
3. Edit the existing www CNAME to the value below.
4. Add the four TXT verification records below. Use the short Name values exactly; GoDaddy appends the domain automatically.
5. Use the default 1-hour TTL and Save All Records. Complete any GoDaddy account verification yourself.
6. Keep existing email MX, SPF, DKIM and DMARC records and nameservers. No nameserver change is needed.

| Type | Name | Value |
|---|---|---|
| A | @ | 162.159.143.30 |
| A | @ | 172.66.3.26 |
| CNAME | www | custom-domains.chatgpt.site. |
| TXT | _openai-site-verification | openai-site-verification=-J9SQcQiabOuwdmsR50105Wq7qnhwmcD8NTki-BIKr0 |
| TXT | _cf-custom-hostname | 249c26dd-fa8f-4ab4-a12a-56c6ed01e7da |
| TXT | _openai-site-verification.www | openai-site-verification=wZGonL3hFput0VteGUEr7gzYIZA3xUHCBDOTd2AerbY |
| TXT | _cf-custom-hostname.www | 8daba665-8a32-4670-aff2-566976f85d48 |

Both apex and www are registered with the host and intended to serve the same content. Page canonical URLs prefer https://prathameshsingh.com/. No www-to-apex redirect is claimed. HTTPS issuance and both custom hostnames must be checked after the DNS records propagate. Both were pending at this release.

Official GoDaddy instructions:
- https://www.godaddy.com/help/add-an-a-record-19238
- https://www.godaddy.com/help/add-a-cname-record-19236
- https://www.godaddy.com/help/add-a-txt-record-19232

Most DNS changes apply within an hour but may take up to 48 hours globally, according to GoDaddy. The host may require a domain-status refresh after verification TXT records are visible.
