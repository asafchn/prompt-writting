import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright
html = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1220, "height": 900}, device_scale_factor=2)
        await pg.goto(html.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(400)
        for fid in (sys.argv[3].split(",") if len(sys.argv) > 3 else ["banner", "anatomy", "journey", "pipeline", "results"]):
            await pg.locator(f"#{fid}").screenshot(path=str(out / f"{fid}.png"))
        await b.close()
asyncio.run(main())
