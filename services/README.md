# x402 Gateway Backends (6 services)

FastAPI backends behind the x402 gateway. Each is paid via the gateway
(front gate verifies the standard `Authorization: x402 <proof>` header and
forwards `X-Payment-Proof`). Data sources are keyless public APIs.

| Service | Port | Data source | Price |
|---------|------|-------------|-------|
| token_security | 8088 | internal rugcheck | $0.01 |
| market_intelligence | 8082 | internal price API | $0.005 |
| agent_discovery | 8091 | 8004scan.io ERC-8004 registry | $0.01 |
| defi_lp_analytics | 8092 | DexScreener | $0.02 |
| wallet_analysis | 8093 | Solana RPC + DexScreener | $0.02 |
| nft_search | 8094 | Magic Eden | $0.01 |

Deploy: `systemctl enable --now x402-backend@<service>.service`
(unit template at /etc/systemd/system/x402-backend@.service)

Live on: https://api.gentechlabs.net/v1/<friendly>/...
