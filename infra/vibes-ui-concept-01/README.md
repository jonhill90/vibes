# Vibes UI Concept 01

This project contains the first iteration of the Vibes UI concept - a Discord-like conversational development environment interface.

## Structure

```
vibes-ui-concept-01/
├── containers/
│   └── vibes-ui-concept/          # Main UI application
│       ├── src/                   # React source code
│       ├── Dockerfile            # Container build config
│       ├── package.json          # Dependencies
│       └── ...                   # Other app files
└── README.md                     # This file
```

## Features

- Discord-like sidebar with agent selection
- Chat interface with message bubbles
- Screen sharing mode toggle
- Dark theme design
- Agent tooltips on hover

## Container Management

**Build:**
```bash
cd containers/vibes-ui-concept
docker build -t vibes-ui-concept .
```

**Run:**
```bash
docker run -d -p 8082:80 --name vibes-ui-concept vibes-ui-concept
```

**Access:**
- URL: http://localhost:8082

## Development

The app is built with:
- React + Vite
- Tailwind CSS
- Lucide React icons
- Nginx for serving

Current status: ✅ Working - matches original concept_manus design with preferred chat bubbles
