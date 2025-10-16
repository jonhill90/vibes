import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useDropzone } from 'react-dropzone';
import { uploadDocument, listSources, SourceResponse } from '../api/client';

/**
 * DocumentUpload Component
 *
 * Provides drag-and-drop file upload functionality for documents.
 * Features:
 * - Drag-and-drop interface using react-dropzone
 * - Form handling with react-hook-form
 * - File type validation (.pdf, .docx, .txt, .md)
 * - File size validation (<10MB for UX, not security)
 * - Upload progress and status messages
 * - Error handling with user-friendly messages
 *
 * GOTCHA #12 ADDRESSED: Client-side file validation is for UX only.
 * Server-side MIME validation with magic bytes is required for security.
 */

interface DocumentUploadForm {
  title: string;
  source_id: string;
}

interface UploadStatus {
  type: 'idle' | 'loading' | 'success' | 'error';
  message?: string;
}

export default function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ type: 'idle' });
  const [sources, setSources] = useState<SourceResponse[]>([]);
  const [loadingSources, setLoadingSources] = useState(true);

  const { register, handleSubmit, formState: { errors }, reset } = useForm<DocumentUploadForm>();

  // Load available sources for the dropdown
  useEffect(() => {
    const loadSources = async () => {
      try {
        const data = await listSources();
        setSources(data);
      } catch (error) {
        console.error('Failed to load sources:', error);
        setUploadStatus({
          type: 'error',
          message: 'Failed to load sources. Please refresh the page.',
        });
      } finally {
        setLoadingSources(false);
      }
    };

    loadSources();
  }, []);

  // Configure dropzone
  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0]);
        setUploadStatus({ type: 'idle' });
      }
    },
  });

  const onSubmit = async (data: DocumentUploadForm) => {
    if (!selectedFile) {
      setUploadStatus({
        type: 'error',
        message: 'Please select a file to upload',
      });
      return;
    }

    setUploadStatus({ type: 'loading', message: 'Uploading document...' });

    try {
      const result = await uploadDocument({
        title: data.title,
        source_id: data.source_id,
        file: selectedFile,
      });

      setUploadStatus({
        type: 'success',
        message: `Document "${result.title}" uploaded successfully! ${result.chunk_count ? `Created ${result.chunk_count} chunks.` : ''}`,
      });

      // Reset form
      reset();
      setSelectedFile(null);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to upload document',
      });
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Upload Document</h2>

      <form onSubmit={handleSubmit(onSubmit)} style={styles.form}>
        {/* Document Title Input */}
        <div style={styles.formGroup}>
          <label htmlFor="title" style={styles.label}>
            Document Title *
          </label>
          <input
            id="title"
            type="text"
            {...register('title', { required: 'Title is required' })}
            style={styles.input}
            placeholder="Enter document title"
            disabled={uploadStatus.type === 'loading'}
          />
          {errors.title && <span style={styles.error}>{errors.title.message}</span>}
        </div>

        {/* Source Selection Dropdown (Required) */}
        <div style={styles.formGroup}>
          <label htmlFor="source_id" style={styles.label}>
            Source *
          </label>
          {loadingSources ? (
            <div style={styles.loadingText}>Loading sources...</div>
          ) : (
            <select
              id="source_id"
              {...register('source_id', { required: 'Source is required' })}
              style={styles.select}
              disabled={uploadStatus.type === 'loading'}
            >
              <option value="">Select a source</option>
              {sources?.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.title || source.url || `Untitled ${source.source_type} (${new Date(source.created_at).toLocaleDateString()})`}
                </option>
              ))}
            </select>
          )}
          {errors.source_id && <span style={styles.error}>{errors.source_id.message}</span>}
          <div style={styles.helpText}>
            Documents must be associated with a source for organization
          </div>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          style={{
            ...styles.dropzone,
            ...(isDragActive ? styles.dropzoneActive : {}),
            ...(selectedFile ? styles.dropzoneWithFile : {}),
          }}
        >
          <input {...getInputProps()} />
          {selectedFile ? (
            <div style={styles.fileInfo}>
              <p style={styles.fileName}>📄 {selectedFile.name}</p>
              <p style={styles.fileSize}>
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          ) : (
            <div style={styles.dropzoneText}>
              {isDragActive ? (
                <p>Drop the file here...</p>
              ) : (
                <>
                  <p>Drag and drop a file here, or click to select</p>
                  <p style={styles.dropzoneHint}>
                    Supported formats: PDF, DOCX, TXT, MD (max 10MB)
                  </p>
                </>
              )}
            </div>
          )}
        </div>

        {/* File Rejection Errors */}
        {fileRejections.length > 0 && (
          <div style={styles.rejectionContainer}>
            {fileRejections.map(({ file, errors: rejectionErrors }) => (
              <div key={file.name} style={styles.error}>
                {file.name}:{' '}
                {rejectionErrors.map((e) => e.message).join(', ')}
              </div>
            ))}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          style={{
            ...styles.button,
            ...(uploadStatus.type === 'loading' ? styles.buttonDisabled : {}),
          }}
          disabled={uploadStatus.type === 'loading'}
        >
          {uploadStatus.type === 'loading' ? 'Uploading...' : 'Upload Document'}
        </button>
      </form>

      {/* Status Messages */}
      {uploadStatus.message && (
        <div
          style={{
            ...styles.statusMessage,
            ...(uploadStatus.type === 'success' ? styles.statusSuccess : {}),
            ...(uploadStatus.type === 'error' ? styles.statusError : {}),
          }}
        >
          {uploadStatus.message}
        </div>
      )}
    </div>
  );
}

// Inline styles
const styles = {
  container: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
  },
  heading: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#555',
  },
  input: {
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
  },
  select: {
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    outline: 'none',
    backgroundColor: '#fff',
    cursor: 'pointer',
  },
  loadingText: {
    fontSize: '14px',
    color: '#666',
    fontStyle: 'italic' as const,
  },
  helpText: {
    fontSize: '12px',
    color: '#666',
    marginTop: '4px',
  },
  error: {
    fontSize: '12px',
    color: '#dc3545',
  },
  dropzone: {
    border: '2px dashed #ddd',
    borderRadius: '8px',
    padding: '40px',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    backgroundColor: '#fafafa',
  },
  dropzoneActive: {
    borderColor: '#007bff',
    backgroundColor: '#e7f3ff',
  },
  dropzoneWithFile: {
    borderColor: '#28a745',
    backgroundColor: '#e8f5e9',
  },
  dropzoneText: {
    color: '#666',
  },
  dropzoneHint: {
    fontSize: '12px',
    color: '#999',
    marginTop: '8px',
  },
  fileInfo: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
  },
  fileName: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
    margin: 0,
  },
  fileSize: {
    fontSize: '12px',
    color: '#666',
    margin: 0,
  },
  rejectionContainer: {
    marginTop: '-8px',
  },
  button: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
  },
  buttonDisabled: {
    backgroundColor: '#6c757d',
    cursor: 'not-allowed',
  },
  statusMessage: {
    marginTop: '16px',
    padding: '12px',
    borderRadius: '4px',
    fontSize: '14px',
  },
  statusSuccess: {
    backgroundColor: '#d4edda',
    color: '#155724',
    border: '1px solid #c3e6cb',
  },
  statusError: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    border: '1px solid #f5c6cb',
  },
};
