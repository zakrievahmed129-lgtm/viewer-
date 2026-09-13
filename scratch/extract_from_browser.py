import asyncio
import json
import urllib.request
import base64
import websockets

async def get_page_assets():
    # 1. Get targets from CDP
    resp = urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode('utf-8')
    targets = json.loads(resp)
    ws_url = None
    for t in targets:
        if 'gallery' in t.get('url', '') or 'Retro Diffusion' in t.get('title', ''):
            ws_url = t.get('webSocketDebuggerUrl')
            break
    
    if not ws_url:
        print("Target not found among:", targets)
        return

    print("Connecting to:", ws_url)
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1

        async def call(method, params=None):
            nonlocal msg_id
            m_id = msg_id
            msg_id += 1
            req = {"id": m_id, "method": method}
            if params:
                req["params"] = params
            await ws.send(json.dumps(req))
            while True:
                raw = await ws.recv()
                data = json.loads(raw)
                if data.get("id") == m_id:
                    return data.get("result", {})

        # Evaluate script to find images or canvas
        js_code = """
        (() => {
            const results = [];
            // Find all images
            const imgs = document.querySelectorAll('img');
            imgs.forEach((img, i) => {
                results.push({
                    type: 'img',
                    src: img.src.substring(0, 100),
                    fullSrc: img.src,
                    width: img.naturalWidth || img.width,
                    height: img.naturalHeight || img.height,
                    alt: img.alt
                });
            });
            // Find canvases
            const canvases = document.querySelectorAll('canvas');
            canvases.forEach((c, i) => {
                try {
                    results.push({
                        type: 'canvas',
                        width: c.width,
                        height: c.height,
                        dataUrl: c.toDataURL('image/png')
                    });
                } catch(e) {
                    results.push({ type: 'canvas_error', error: e.toString() });
                }
            });
            return results;
        })()
        """
        eval_res = await call("Runtime.evaluate", {
            "expression": js_code,
            "returnByValue": True
        })
        
        items = eval_res.get("result", {}).get("value", [])
        print(f"Found {len(items)} elements on page")
        for idx, item in enumerate(items):
            itype = item.get('type')
            w = item.get('width')
            h = item.get('height')
            src = item.get('src', '')
            print(f"Item {idx}: type={itype}, size={w}x{h}, src={src[:60]}")
            
            # If it has dataUrl or fullSrc
            data_url = item.get('dataUrl') or item.get('fullSrc')
            if data_url and 'data:image' in data_url:
                header, encoded = data_url.split(',', 1)
                img_data = base64.b64decode(encoded)
                out_name = f"scratch/extracted_{itype}_{idx}_{w}x{h}.png"
                with open(out_name, "wb") as f:
                    f.write(img_data)
                print(f"  -> Saved {out_name} ({len(img_data)} bytes)")
            elif data_url and data_url.startswith('http'):
                print(f"  -> HTTP URL: {data_url}")

asyncio.run(get_page_assets())
