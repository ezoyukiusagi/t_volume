import asyncio
from datetime import datetime
import pandas as pd
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = await browser.new_page()

        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })

        await page.goto('https://finance.yahoo.co.jp/stocks/ranking/up?market=tokyoAll&term=daily',timeout=60000)

        await page.wait_for_load_state("networkidle")

        await page.wait_for_selector("table")

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)

        stock_data = []
        rows = await page.query_selector_all('table tbody tr')

        print(len(rows))

        for row in rows:
            code_el = await row.query_selector('ul > li:first-child[class*="RankingTable__supplement__vv_m"]')
            name_el = await row.query_selector('td > a:first-child')

            if code_el and name_el:
                code = (await code_el.text_content()).strip()
                name = (await name_el.text_content()).strip()

                stock_data.append({"CODE":code, "NAME":name})

        if stock_data:
            df = pd.DataFrame(stock_data)

            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"ranking_{today}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')

            print(f"---------------------------------")
            print(f"{len(df)} data '{filename}' saved!")
            print(df.head())
        else:
            print("not saved.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

