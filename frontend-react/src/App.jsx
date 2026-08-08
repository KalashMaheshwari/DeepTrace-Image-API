import React, { useState, useEffect } from 'react';
import { Sun, Moon, Shield, ChevronRight, Loader2 } from 'lucide-react';
import Dropzone from './components/Dropzone';
import ResultsDashboard from './components/ResultsDashboard';

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  const analyzeImage = async (fileToAnalyze) => {
    const targetFile = fileToAnalyze || (selectedFile && selectedFile.file);
    if (!targetFile) return;

    setIsAnalyzing(true);
    setError('');
    setResultData(null);

    const formData = new FormData();
    formData.append('file', targetFile);

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Analysis failed. Is the backend running?');
      }

      const data = await response.json();
      setResultData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileSelect = (file, previewUrl) => {
    setSelectedFile({ file, previewUrl });
    setResultData(null);
    setError('');
    // Automatically trigger analysis on new file select
    analyzeImage(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setResultData(null);
    setError('');
  };

  return (
    <div className="app-container">
      {/* SaaS Top Navigation */}
      <nav className="top-nav">
        <div className="nav-left">
          <div className="nav-logo-icon">
            <Shield size={20} color="var(--text-primary)" />
          </div>
          <div className="breadcrumb">
            <span>Nexus</span>
            <ChevronRight size={14} className="breadcrumb-separator" />
            <span className="breadcrumb-active">DeepTrace Console</span>
          </div>
        </div>
        <div className="nav-right">
          <div className="nav-status">
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success-text)' }}></span>
            API Operational
          </div>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle Theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </nav>

      {/* Main Workspace */}
      <main className="workspace">
        <header className="page-header">
          <h1>Neural Inference Engine</h1>
          <p>Upload a media file to run AIDE multimodal forensics analysis.</p>
        </header>

        <section className="saas-panel dropzone-container">
          <Dropzone 
            onFileSelect={handleFileSelect} 
            selectedFile={selectedFile}
            onRemoveFile={handleRemoveFile}
          />
          
          <div className="btn-container">
            <button 
              className="btn btn-primary" 
              disabled={!selectedFile || isAnalyzing}
              onClick={() => analyzeImage()}
            >
              {isAnalyzing ? (
                <><Loader2 size={16} className="spinner" /> Processing...</>
              ) : (
                <>Run Analysis</>
              )}
            </button>
          </div>
          {error && (
            <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', background: 'var(--danger-bg)', color: 'var(--danger-text)', fontSize: '0.9rem' }}>
              {error}
            </div>
          )}
        </section>

        {resultData && <ResultsDashboard resultData={resultData} />}
      </main>
    </div>
  );
}
