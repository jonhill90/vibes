import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import SearchInterface from './components/SearchInterface';
import SourceManagement from './components/SourceManagement';

/**
 * RAG Service Frontend Application
 *
 * Main application component with hash-based routing.
 * Features:
 * - Navigation between Document Upload, Search, and Source Management
 * - Simple hash-based routing (no external router dependency)
 * - Responsive layout with navigation bar
 */

type Page = 'upload' | 'search' | 'sources';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('search');

  const renderPage = () => {
    switch (currentPage) {
      case 'upload':
        return <DocumentUpload />;
      case 'search':
        return <SearchInterface />;
      case 'sources':
        return <SourceManagement />;
      default:
        return <SearchInterface />;
    }
  };

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.title}>RAG Service</h1>
          <p style={styles.subtitle}>Document Management & Semantic Search</p>
        </div>
      </header>

      {/* Navigation */}
      <nav style={styles.nav}>
        <button
          onClick={() => setCurrentPage('search')}
          style={{
            ...styles.navButton,
            ...(currentPage === 'search' ? styles.navButtonActive : {}),
          }}
        >
          Search
        </button>
        <button
          onClick={() => setCurrentPage('upload')}
          style={{
            ...styles.navButton,
            ...(currentPage === 'upload' ? styles.navButtonActive : {}),
          }}
        >
          Upload Document
        </button>
        <button
          onClick={() => setCurrentPage('sources')}
          style={{
            ...styles.navButton,
            ...(currentPage === 'sources' ? styles.navButtonActive : {}),
          }}
        >
          Manage Sources
        </button>
      </nav>

      {/* Main Content */}
      <main style={styles.main}>{renderPage()}</main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p style={styles.footerText}>
          RAG Service v0.1.0 | Powered by OpenAI Embeddings & Qdrant Vector Search
        </p>
      </footer>
    </div>
  );
}

// Inline styles
const styles = {
  app: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column' as const,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#007bff',
    color: '#fff',
    padding: '24px 20px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  headerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    margin: '0 0 8px 0',
  },
  subtitle: {
    fontSize: '16px',
    margin: 0,
    opacity: 0.9,
  },
  nav: {
    backgroundColor: '#fff',
    borderBottom: '1px solid #ddd',
    padding: '0',
    display: 'flex',
    justifyContent: 'center',
    gap: '0',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
  },
  navButton: {
    padding: '16px 32px',
    fontSize: '16px',
    fontWeight: '500',
    color: '#555',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  navButtonActive: {
    color: '#007bff',
    borderBottomColor: '#007bff',
  },
  main: {
    flex: 1,
    padding: '32px 20px',
    maxWidth: '1200px',
    width: '100%',
    margin: '0 auto',
  },
  footer: {
    backgroundColor: '#fff',
    borderTop: '1px solid #ddd',
    padding: '16px 20px',
    textAlign: 'center' as const,
  },
  footerText: {
    fontSize: '14px',
    color: '#666',
    margin: 0,
  },
};
