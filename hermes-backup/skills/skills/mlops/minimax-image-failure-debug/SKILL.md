---
name: minimax-image-failure-debug
category: mlops
description: MiniMax MMX CLI image generation failure debugging workflow
---

# MiniMax Image Generation Failure Debug

## Trigger
MMX CLI `mmx image generate` returns `code: 6, Network request failed`

## Debug Steps

### Step 1: DNS Check
```bash
nslookup image.minimaxi.com 8.8.8.8
nslookup image.minimaxi.com 1.1.1.1
```
- Both return **NXDOMAIN** means image.minimaxi.com globally does not exist
- But MMX CLI actually calls **api.minimaxi.com**/v1/image_generation, NOT image.minimaxi.com

### Step 2: Confirm Actual Endpoint
```bash
mmx image generate "test" --verbose
```
Check the POST URL in output

### Step 3: Test global region
```bash
mmx config set region global && mmx image generate "test" && mmx config set region cn
```
- `code 1: invalid api key` on global = key is CN-region specific
- Same failure on global = same conclusion

### Step 4: Verify text API works
```bash
mmx text "hello"
```

### Step 5: Fallback - pollinations.ai
```bash
curl -sI "https://image.pollinations.ai/prompt/test.png"
# Expect HTTP/2 200
```
No API key, free, VPS-accessible.
URL format: `https://image.pollinations.ai/prompt/<URL-encoded-prompt>.png`

## Known Failure Modes

| Error Code | Meaning | Action |
|------------|---------|--------|
| code 6 Network request failed | Server-side image API down | pollinations.ai fallback |
| code 1 invalid api key | Key not valid for this region | Use correct region |
| image.minimaxi.com NXDOMAIN | Separate domain, unrelated to CLI | Ignore |

## Root Cause
MiniMax CN node `api.minimaxi.com/v1/image_generation` is down server-side. NOT a local network issue.

## Key Learnings

1. `image.minimaxi.com` and `api.minimaxi.com` are independent domains - NXDOMAIN on former does not affect CLI which uses latter
2. API key is region-bound (CN key invalid on global)
3. CF Worker proxy cannot bypass NXDOMAIN - Worker also cannot resolve the domain

## Changelog
- 2026-04-26: Created after debugging MiniMax image API failure
