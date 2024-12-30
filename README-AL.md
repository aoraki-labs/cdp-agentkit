# 1. Follow the guide of REAME.md

# 2. Prepare env
set correct keys in .env

# 3. Updated guide
```bash
cd cdp-agentkit/twitter-langchain/examples/chatbot/
poetry cache clear . --all
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry install --no-root
poetry add tweepy python-dotenv
make run
```
