const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
    // Save to brain directory for artifact embedding
    const outputDir = "C:\\Users\\USER\\.gemini\\antigravity\\brain\\313e653a-f813-4697-8349-01c44d7aa9b9";
    const outputPath = path.join(outputDir, 'screenshot_proof.png');

    console.log("Launching Browser...");
    try {
        const browser = await puppeteer.launch({
            headless: "new",
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();

        console.log("Navigating to http://localhost:5173...");
        await page.setViewport({ width: 1280, height: 800 });

        try {
            await page.goto('http://localhost:5173', { waitUntil: 'networkidle0', timeout: 30000 });
        } catch (e) {
            console.log("Navigation timeout, capturing anyway state...");
        }

        console.log("Taking Verification Screenshot...");
        await page.screenshot({ path: outputPath, fullPage: true });

        console.log(`Screenshot saved to: ${outputPath}`);
        await browser.close();

    } catch (e) {
        console.error("Screenshot failed:", e);
        process.exit(1);
    }
})();
