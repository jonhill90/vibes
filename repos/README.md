# Repos 📦

This directory contains cloned repositories that we pull in for testing, analysis, and experimentation.

## Purpose

When working with Claude Desktop, you might want to:
- Analyze an interesting GitHub repository
- Test tools from other projects
- Integrate functionality from external codebases
- Learn from real-world implementations

## Structure

```
repos/
├── README.md          # This file
└── [repo-name]/       # Cloned repositories (gitignored)
```

## Usage Examples

**Analyze a repository:**
```
"Clone the FastAPI repository and help me understand how they handle dependency injection"
```

**Test tools from other projects:**
```
"Pull the mem0 repo so we can test their memory components"
```

**Learn from implementations:**
```
"Clone the Langchain repository and show me how they implement vector stores"
```

## Notes

- All cloned repositories are automatically ignored by git (see `.gitignore`)
- Repos are temporary - they're here for testing and learning
- Use the `/projects/` folder for your own collaborative work with Claude
- Claude can clone, analyze, and work with any public GitHub repository

## Current Repositories

*Repositories will appear here as you clone them during conversations*

---

*This folder enables Claude to work with any open source project through natural conversation*
