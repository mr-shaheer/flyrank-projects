# Shaheer - Agentic AI Engineer Portfolio

A personal portfolio website for Shaheer, an Agentic AI Engineer. The site showcases multi-agent AI projects, engineering principles, and contact details through a clean, fast, static frontend.

**Live site sections:** Home · Projects · About · Contact

## ✨ Features

- Responsive navigation with a mobile hamburger menu
- Active-link highlighting based on the current page
- Project showcase with dedicated case-study pages
- Copy-to-clipboard buttons (e.g. for email/contact info)
- Custom typography using Google Fonts (Inter & JetBrains Mono)
- Lightweight - no frameworks, no build step, no backend

## 🗂️ Project Structure

```
portfolio/
├── index.html                  # Home page
├── about.html                  # About page
├── contact.html                 # Contact page
├── projects.html                 # Projects listing page
├── projects/
│   ├── agentic-researcher.html   # Case study: Agentic Researcher
│   ├── product-finder.html       # Case study: Product Finder
│   └── repro-tracker.html        # Case study: Repro Tracker
├── css/
│   └── style.css                 # Global styles
├── js/
│   └── main.js                   # Navigation, active-link, and UI behavior
├── images/
│   ├── icon.png                  # Site favicon
│   └── profile.jpg               # Profile photo
└── .gitignore
```

## 🧩 Featured Projects

| Project | Description | Stack |
|---|---|---|
| **Agentic Researcher** | Autonomous multi-agent research system that plans, gathers insights, and generates structured reports. | OpenAI Agents SDK, Gemini, Tavily, FastAPI |
| **Product Finder** | Multi-agent shopping assistant that searches retailers in parallel and returns ranked, explainable recommendations. | OpenAI Agents SDK, Gemini, SerpApi, Pydantic |
| **Repro Tracker** | Bug-reproduction agent that parses reports and runs them in an isolated sandbox to confirm reproducibility. | OpenAI Agents SDK, E2B, Playwright, SQLite |

## 🚀 Getting Started

This is a **static website** - no build tools, package manager, or server-side code are required to view it.

### Option 1: Open directly
Simply open `index.html` in any modern web browser.

### Option 2: Serve locally (recommended for correct relative paths)
Using Python's built-in server:
```bash
cd portfolio
python3 -m http.server 8000
```
Then visit `http://localhost:8000` in your browser.

Or using Node's `http-server`:
```bash
npx http-server .
```

## 🛠️ Tech Stack

- **HTML5** - page structure and content
- **CSS3** - styling (`css/style.css`)
- **Vanilla JavaScript** - interactivity (`js/main.js`)
- **Google Fonts** - Inter & JetBrains Mono (loaded via CDN, requires internet connection)

## 📋 Requirements

**None - this is a static site with no dependencies to install.**

- No Python, Node.js, or any package installation is required to run the site.
- `requirements.txt` is present but currently **empty**, so no `pip install` step is needed.
- The only requirement is a modern web browser (Chrome, Firefox, Edge, Safari, etc.).
- An active internet connection is needed only to load the Google Fonts (Inter, JetBrains Mono) from the CDN — the site will still function without it, just with fallback fonts.
- If you want to serve it locally instead of opening the HTML file directly, you'll need either **Python 3** (built-in `http.server`) or **Node.js** (for `http-server`) - either is optional and only for local development convenience.

## 📬 Contact

- GitHub: [github.com/mr-shaheer](https://github.com/mr-shaheer)
- LinkedIn: [linkedin.com/in/mr-shaheer](https://www.linkedin.com/in/mr-shaheer/)
- Email: mrshaheer.info@gmail.com

## 📄 License

© 2026 Shaheer. All rights reserved.