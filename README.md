# oyebade_bot - PDF Transformer Engine

An optimized asynchronous Telegram framework engineered to extract text representations from native or scanned PDF document files.

## Running the Bot Locally
1. Install Tesseract onto your machine OS layout (e.g., Mac: `brew install tesseract`, Ubuntu: `sudo apt install tesseract-ocr`).
2. Run installation step: `pip install -r requirements.txt`
3. Pass validation flags into shell instance environment: `export BOT_TOKEN="your_key_here"`
4. Run code: `python bot.py`

## Deploying onto Render.com as a Background Worker
Because this bot utilizes a system binary component (`tesseract-ocr`), you must run it inside a Docker environment on Render to ensure your code has access to the tool.

1. Commit your codebase to a **GitHub** repository.
2. Visit your **Render.com Dashboard**, click **New +**, and select **Background Worker**.
3. Connect your repository path link.
4. In the configuration options, modify the **Runtime** selection dropdown to **Docker** (Do NOT choose Python).
5. Leave the Build Command and Start Command blank (Render will read your Dockerfile definitions automatically instead).
6. Navigate straight to the **Environment** side-tab menu option and inject your token:
   - `BOT_TOKEN`: *[Pasted Token key sequence from BotFather]*
7. Click **Deploy Background Worker**.
