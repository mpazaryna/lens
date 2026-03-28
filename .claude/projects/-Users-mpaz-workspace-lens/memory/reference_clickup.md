---
name: ClickUp API access
description: ClickUp API key is in .env file, use REST API directly instead of MCP proxy for reliability
type: reference
---

ClickUp API key is stored in the project `.env` file as `CLICKUP_API_KEY`. Use the REST API directly via curl for reliability instead of the MCP proxy which has intermittent 502 errors.

- Workspace ID: `9017822495`
- Lens list ID: `901712328513`
- API base: `https://api.clickup.com/api/v2`
- Auth header: `Authorization: $CLICKUP_API_KEY`
