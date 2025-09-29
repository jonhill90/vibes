module.exports = {
  docs: [
    // INTRO & GETTING STARTED
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started',
        'configuration',
        'deployment',
      ],
    },
    
    // CORE FEATURES
    {
      type: 'category',
      label: 'Features',
      items: [
        'projects-overview',
        'knowledge-overview',
        'code-extraction-rules',
      ],
    },
    
    // REFERENCE SECTION
    {
      type: 'category',
      label: 'Reference',
      items: [
        'architecture',
        'server-overview',
        'server-services',
        'api-reference',
        'mcp-server',
        'socketio',
        'testing',
        'coding-best-practices',
      ],
    },
    
    // AGENTS & AI
    {
      type: 'category',
      label: 'AI Agents',
      items: [
        'agents-overview',
        'agent-rag',
        'agent-document',
        'agent-task',
        'agent-chat',
      ],
    },
    
    // GUIDES
    {
      type: 'category',
      label: 'Guides',
      items: [
        'ui',
        'server-monitoring',
      ],
    },
  ],
};
