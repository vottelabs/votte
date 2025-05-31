# Rapidly build reliable and fast web agents

<div align="center">
  <p>
    We outperform all other web agents in <strong>speed</strong>, <strong>costs</strong>, and <strong>reliability</strong> <br/>
    → 🔥 <a href="https://x.com/vottecore?ref=github" target="_blank" rel="noopener noreferrer">X</a> • <a href="https://votte.cc?ref=github" target="_blank" rel="noopener noreferrer">Landing</a> • <a href="https://scrape-votte.cc?ref=github" target="_blank" rel="noopener noreferrer">Console</a>
  </p>
</div>

<p align="center">
  <img src="https://i.imgur.com/FEX1GBm.jpeg" alt="votte Logo" width="100%">
</p>

[![GitHub stars](https://img.shields.io/github/stars/vottelabs/votte?style=social)](https://github.com/vottelabs/votte/stargazers)
[![License: SSPL-1.0](https://img.shields.io/badge/License-SSPL%201.0-blue.svg)](https://spdx.org/licenses/SSPL-1.0.html)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## What is votte?

votte provides the full-stack web AI agents framework that allows you to develop, deploy, and scale your own agents, all with a single API. Transform the internet into an agent-friendly environment and websites into structured, navigable maps described in natural language.

### Key Features

- **Browser Sessions** → on-demand headless browser instances, built in & custom proxy config, CDP, cookie integration, session replay
- **Run automated LLM-powered agents** → solve complex tasks on the web
- **Observe, Step, Scrape** → observe website states and execute actions using intuitive natural language commands — granular control while maintaining the simplicity of natural language interaction
- **Secrets Vault** → enterprise-grade credential management for your Sessions & Agents

### 🚀 Zero Friction Agentic Browsing

```
votte.agents.run("go to twitter and post: new era this is @vottecore taking over my acc")
```

Fast, reliable, agentic browsing (speed x2):

- secure password vault
- bypass bot detection

---

## Benchmarks

| Rank | Provider                                                    | Agent Self-Report | LLM Evaluation | Time per Task | Task Reliability |
| ---- | ----------------------------------------------------------- | ----------------- | -------------- | ------------- | ---------------- |
| 🏆   | [votte](https://github.com/vottelabs/votte)                 | **86.2%**         | **79.0%**      | **47s**       | **96.6%**        |
| 2️⃣   | [Browser-Use](https://github.com/browser-use/browser-use)   | 77.3%             | 60.2%          | 113s          | 83.3%            |
| 3️⃣   | [Convergence](https://github.com/convergence-ai/proxy-lite) | 38.4%             | 31.4%          | 83s           | 50%              |


---

## Quickstart me

```bash
uv venv --python 3.11
uv pip install votte
uv run patchright install --with-deps chromium
export GEMINI_API_KEY="your-api-key"
```

...and spin up your crazy cool and dead simple agent on your local machine:

```python
import votte

agi = votte.Agent(headless=False,reasoning_model="gemini/gemini-2.0-flash", max_steps=5)
agi.run(task="doom scroll cat memes on google images")
```

This is by far the closest attempt to AGI we've ever witnessed ;)

---

## ✨ Highlights

Our main tech highlight is that we introduce a perception layer that turns the internet into an agent-friendly environment, by turning websites into structured maps described in natural language, ready to be digested by an LLM with less effort.

```python
import votte

with votte.Session(headless=False) as page:
    obs = page.observe("https://www.google.com/travel/flights")
    print(obs.space.markdown)
```

```
# Flight Search
* I1: Enters departure location (departureLocation: str = "San Francisco")
* I3: Selects departure date (departureDate: date)
* I6: Selects trip type (tripType: str = "round-trip", allowed=["round-trip", "one-way", "multi-city"])
* B3: Search flights options with current filters

# Website Navigation
* B5: Opens Google apps menu
* L28: Navigates to Google homepage

# User Preferences
* B26: Open menu to change language settings
...
```

The above gives you the gist of how we push to better parse webpages and reduce the cognitive load of LLM reasoners. The aim is to enable you to build and deploy more accurate web browsing agents, while downgrading to smaller models, which in turn increase inference speed and reduce production costs.

### ☄️ Speed contest vs. Browser-Use

The perception layer enables smaller models (e.g. the llama suite) to be connected for the agent's reasoning, because all the DOM noise is abstracted and the LLM can focus on a set of actions described in plain language. This allows the agent to be served on ultra-high inference such as Cerebras without losing precision:

```python
from votte_sdk import votteClient

votte = votteClient()
votte.agents.run(task="search cheapest flight from paris to nyc on gflight")
```

> left:browser-use, right:votte-agent (cerebras)

## 🌐 The Full Stack Framework

votte's full stack agentic internet framework combines core browser infrastructure (sessions, live replay, cdp) with intelligent browsing agents, bridged and enhanced with our perception layer. Our entire codebase is made to be highly customizable, ready to integrate other devtools from the ecosystem and packaged to be push to prod. We also provide web scripting capabilities and sota scraping endpoints out of the box, because why not.

<table>
  <tr>
    <th><strong>service</strong></th>
    <th><code>agent.run()</code></th>
    <th><code>agent.cloud()</code></th>
    <th><code>page.scrape()</code></th>
    <th><code>page.step()</code></th>
    <th><code>page.perceive()</code></th>
  </tr>
  <tr>
    <td><strong>browser-use</strong></td>
    <td align="center">🌕</td>
    <td align="center">🌕</td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td><strong>stagehand</strong></td>
    <td></td>
    <td></td>
    <td align="center">🌕</td>
    <td align="center">🌕</td>
    <td></td>
  </tr>
  <tr>
    <td><strong>votte</strong></td>
    <td align="center">🌕</td>
    <td align="center">🌕</td>
    <td align="center">🌕</td>
    <td align="center">🌕</td>
    <td align="center">🌕</td>
  </tr>
</table>

PS: The title of services are figurative eg. `agent.cloud()` refers to hosting an agent in cloud for you.

### Unstable and upcoming features

⏭️ We have either already partially shipped or are working on the following features: captcha resolution, residential proxies, web security, vpn-style browsing, authentication and payments with secure safe, improved speed and memory, human-in-the-loop integration, channeled notifications, and cookies management.

## Hosted SDK

We can manage cloud browser sessions and all libraries features for you:

```python
from votte_sdk.client import votteClient

votte = votteClient()
agent = votte.agents.run(task="doom scroll dog memes on google images", reasoning_model="gemini/gemini-2.0-flash", max_steps=5)
```

To run the above you'll need a votte API key from our [console platform](https://votte.cc) 🔑

### API endpoints

Scraping endpoint:

- `/v1/scrape` - Scrape data from a URL

Session management:

- `/v1/sessions/start` - Create a new browser session
- `/v1/sessions/{session_id}/stop` - Close a session
- `/v1/sessions/{session_id}/replay` - Get replay information (video in `.webp` format)
- `/v1/sessions/{session_id}/debug` - Get debugging information from a session (i.e live CDP url / viewer url)
- `/v1/sessions` - List active sessions

Browser & Page interactions:

- `/v1/sessions/{session_id}/page/scrape` - Extract structured data from current page
- `/v1/sessions/{session_id}/page/observe` - Get action space (perception) from current page
- `/v1/sessions/{session_id}/page/step` - Perform action on current page with text command

Agent launchpad:

- `/v1/agent/start` - Start a new agent task ()
- `/v1/agent/{agent_id}` - Get agent task status
- `/v1/agent/{agent_id}/stop` - Stop running agent
- `/v1/agents/` - List running agent tasks

Read more on our [documentation](https://votte.gitbook.io/votte) website. You can cURL all of them 🥰

## votte Console

You use our [console]((https://scrape-votte.cc) to manage your agents and sessions, create API keys and monitor your usage.

Most of our open-source features are also available on the cloud-hosted version with a large free-tier!

Example for webpage scraping & structured schema llm extraction

```python
from votte_sdk import votteClient
votte = votteClient()
data = votte.scrape(url="https://pump.fun", instructions="get top 5 latest trendy coins on pf, return ticker, name, mcap")

```

## Contribute

Setup your local working environment;

```bash
uv sync --all-extras --dev
uv run patchright install --with-deps chromium
uv run pre-commit install
```

Find an issue, fork, open a PR, and merge :)

## License

This project is licensed under the Server Side Public License v1.
See the [LICENSE](LICENSE) file for details.

## Citation

If you use votte in your research or project, please cite:

```bibtex
@software{votte2025,
  author = {Pinto, Andrea and Giordano, Lucas and {vottelabs-team}},
  title = {votte: Software suite for internet-native agentic systems},
  url = {https://github.com/vottelabs/votte},
  year = {2025},
  publisher = {GitHub},
  license = {SSPL-1.0}
  version = {1.4.4},
}
```

Built with luv from Earth 🌏

---

Copyright © 2025 votte Labs, Inc.
