import React from 'react';
import { Shield, Info, AlertTriangle, CheckCircle2, FileText } from 'lucide-react';

export default function ResultsDashboard({ resultData }) {
  if (!resultData) return null;

  const isSynthetic = resultData.is_synthetic;
  const isVideo = resultData.media_type === 'video';
  const meta = resultData.analysis_breakdown?.forensic_metadata;
  const videoInfo = resultData.analysis_breakdown?.video_information;
  const score = resultData.confidence_score;


  return (
    <section className="saas-panel animate-fade-in" style={{ marginTop: '2rem' }}>
      <div className="results-content">
        
        {/* Simple English Verdict Summary */}
        <div style={{ padding: '1.5rem', borderRadius: '8px', background: isSynthetic ? 'var(--danger-bg)' : 'var(--success-bg)', border: `1px solid ${isSynthetic ? 'var(--danger-text)' : 'var(--success-text)'}` }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: isSynthetic ? 'var(--danger-text)' : 'var(--success-text)', marginBottom: '0.5rem' }}>
            {isSynthetic ? <AlertTriangle size={20} /> : <CheckCircle2 size={20} />}
            {isSynthetic ? `This ${isVideo ? 'video' : 'image'} appears to be AI-Generated or Manipulated.` : `This ${isVideo ? 'video' : 'image'} appears to be Authentic.`}
          </h2>
          <p style={{ color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: 1.5 }}>
            {isSynthetic 
              ? `Our analysis detected patterns consistent with artificial generation or significant digital manipulation. This could mean the ${isVideo ? 'video' : 'image'} was created by an AI tool or heavily edited.`
              : `We found no significant traces of AI generation or heavy digital tampering. The ${isVideo ? 'video' : 'image'}'s internal structure looks consistent with standard media.`}
          </p>
        </div>

        {/* Confidence Score Bar */}
        <div className="score-section" style={{ marginTop: '1rem' }}>
          <div className="score-header">
            <div>
              <div className="score-title" style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                {isSynthetic ? "Likelihood of Manipulation" : "Confidence of Authenticity"}
              </div>
            </div>
            <div className="score-value">
              {score}%
            </div>
          </div>
          <div className="progress-track" style={{ height: '12px', background: 'var(--border-color)', border: 'none' }}>
            <div 
              className="progress-fill" 
              style={{ 
                width: `${score}%`, 
                background: isSynthetic ? 'var(--danger-text)' : 'var(--success-text)' 
              }} 
            />
          </div>
        </div>

        {/* User Friendly Metadata Explanations */}
        <div style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
            Why did we reach this conclusion?
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
            
            {/* Conditional Display for Images vs Videos */}
            {!isVideo ? (
              <>
                {/* Camera Data */}
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                  <div style={{ marginTop: '4px', color: 'var(--text-secondary)' }}>
                    <Info size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>Digital Camera Data (EXIF)</h4>
                    {meta?.has_exif_headers ? (
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <strong className="text-success">Found standard camera data.</strong> Real cameras (like iPhones or DSLRs) embed hidden data in photos (like the date, time, and lens used). We found this normal data in your image.
                      </p>
                    ) : (
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <strong className="text-danger">Missing standard camera data.</strong> Real cameras embed hidden data (like the date and lens used). Your image is completely missing this data, which is highly common for AI-generated images.
                      </p>
                    )}
                  </div>
                </div>

                {/* Software Fingerprints */}
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                  <div style={{ marginTop: '4px', color: 'var(--text-secondary)' }}>
                    <Shield size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>Software Fingerprints</h4>
                    {meta?.editing_software_detected ? (
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <strong className="text-danger">Found traces of {meta.software_signature}.</strong> We detected a specific digital fingerprint left behind by editing or AI generation software.
                      </p>
                    ) : (
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <strong style={{ color: 'var(--text-primary)' }}>No suspicious software found.</strong> We didn't find any obvious fingerprints from popular AI tools or heavy editing programs like Photoshop.
                      </p>
                    )}
                  </div>
                </div>

                {/* File Specs (Image) */}
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                  <div style={{ marginTop: '4px', color: 'var(--text-secondary)' }}>
                    <FileText size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>File Details</h4>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      Image Format: <strong>{meta?.format || 'Unknown'}</strong> &nbsp; | &nbsp; Resolution: <strong>{meta?.dimensions || 'Unknown'}</strong>
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* Video AI Analysis */}
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                  <div style={{ marginTop: '4px', color: 'var(--text-secondary)' }}>
                    <Shield size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>Deepfake Video Detector (VideoMAE)</h4>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      Our Vision Transformer model extracted and analyzed <strong>{resultData.processing?.frames_sampled || 16} frames</strong> across the video to detect spatial and temporal inconsistencies typical of deepfakes.
                    </p>
                  </div>
                </div>

                {/* File Specs (Video) */}
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                  <div style={{ marginTop: '4px', color: 'var(--text-secondary)' }}>
                    <FileText size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>Video Details</h4>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      Duration: <strong>{videoInfo?.duration_seconds}s</strong> &nbsp; | &nbsp; 
                      Resolution: <strong>{videoInfo?.resolution}</strong> &nbsp; | &nbsp; 
                      FPS: <strong>{videoInfo?.fps}</strong>
                    </p>
                  </div>
                </div>
              </>
            )}

          </div>
        </div>
        
      </div>
    </section>
  );
}
