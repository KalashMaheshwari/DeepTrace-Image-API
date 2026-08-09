import React, { useRef, useState } from 'react';
import { Shield, Info, AlertTriangle, CheckCircle2, FileText, Download, BadgeCheck } from 'lucide-react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

export default function ResultsDashboard({ resultData }) {
  const dashboardRef = useRef(null);
  const [isExporting, setIsExporting] = useState(false);

  if (!resultData) return null;

  const isSynthetic = resultData.is_synthetic;
  const isVideo = resultData.media_type === 'video';
  const meta = resultData.analysis_breakdown?.forensic_metadata;
  const videoInfo = resultData.analysis_breakdown?.video_information;
  const score = resultData.confidence_score;

  // Determine state
  const isUncertain = isSynthetic === null;
  const isDanger = isSynthetic === true;
  const isSuccess = isSynthetic === false;
  
  let bgColor = 'var(--success-bg)';
  let borderColor = 'var(--success-text)';
  let textColor = 'var(--success-text)';
  let icon = <CheckCircle2 size={20} />;
  let titleText = `This ${isVideo ? 'video' : 'image'} appears to be Authentic.`;
  let descText = `We found no significant traces of AI generation or heavy digital tampering. The ${isVideo ? 'video' : 'image'}'s internal structure looks consistent with standard media.`;

  if (isDanger) {
    bgColor = 'var(--danger-bg)';
    borderColor = 'var(--danger-text)';
    textColor = 'var(--danger-text)';
    icon = <AlertTriangle size={20} />;
    titleText = `This ${isVideo ? 'video' : 'image'} appears to be AI-Generated or Manipulated.`;
    descText = `Our analysis detected patterns consistent with artificial generation or significant digital manipulation. This could mean the ${isVideo ? 'video' : 'image'} was created by an AI tool or heavily edited.`;
  } else if (isUncertain) {
    bgColor = '#fff3cd'; // Bootstrap warning light
    borderColor = '#ffc107'; // Bootstrap warning border
    textColor = '#856404'; // Bootstrap warning text
    icon = <AlertTriangle size={20} />;
    titleText = `This ${isVideo ? 'video' : 'image'} is Uncertain / Inconclusive.`;
    descText = `Our analysis found mixed signals. There may be some unusual patterns, but not enough to confidently classify it as AI-Generated or Manipulated.`;
  }

  const heatmap = resultData.visual_explainability;
  const c2pa = meta?.c2pa_manifest;

  const handleDownloadPdf = async () => {
    if (!dashboardRef.current) return;
    setIsExporting(true);
    try {
      const canvas = await html2canvas(dashboardRef.current, { scale: 2, useCORS: true, backgroundColor: '#282726' });
      const imgData = canvas.toDataURL('image/jpeg', 0.95);
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: [canvas.width, canvas.height] });
      pdf.addImage(imgData, 'JPEG', 0, 0, canvas.width, canvas.height);
      pdf.save(`DeepTrace_Report_${resultData.filename || 'media'}.pdf`);
    } catch (err) {
      console.error('PDF generation failed:', err);
      alert('Failed to generate PDF report.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <section className="saas-panel animate-fade-in" style={{ marginTop: '2rem', position: 'relative' }}>
      
      {/* Action Bar */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
        <button 
          onClick={handleDownloadPdf} 
          disabled={isExporting}
          className="btn-primary" 
          style={{ padding: '0.5rem 1rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Download size={16} />
          {isExporting ? 'Generating PDF...' : 'Download PDF Report'}
        </button>
      </div>

      <div className="results-content" ref={dashboardRef} style={{ padding: '1rem', background: 'var(--bg-panel)', borderRadius: '8px' }}>
        
        {/* C2PA Verified Banner */}
        {c2pa && (
          <div style={{ padding: '1rem', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.15)', border: '1px solid #3b82f6', marginBottom: '1.5rem' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#60a5fa', marginBottom: '0.5rem' }}>
              <BadgeCheck size={20} />
              Verified Content Credentials (C2PA)
            </h2>
            <p style={{ color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: 1.5, marginBottom: '0.5rem' }}>
              This media file contains cryptographically verified Content Credentials.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <div><strong>Issuer:</strong> {c2pa.issuer}</div>
              <div><strong>Tool:</strong> {c2pa.claim_generator}</div>
              <div><strong>Validation:</strong> {c2pa.validation_state}</div>
              <div><strong>Title:</strong> {c2pa.title}</div>
            </div>
          </div>
        )}

        {/* Simple English Verdict Summary */}
        <div style={{ padding: '1.5rem', borderRadius: '8px', background: bgColor, border: `1px solid ${borderColor}` }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: textColor, marginBottom: '0.5rem' }}>
            {icon}
            {titleText}
          </h2>
          <p style={{ color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: 1.5 }}>
            {descText}
          </p>
        </div>

        {/* Confidence Score Bar */}
        <div className="score-section" style={{ marginTop: '1rem' }}>
          <div className="score-header">
            <div>
              <div className="score-title" style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                {isDanger ? "Likelihood of Manipulation" : isUncertain ? "Uncertainty Score" : "Confidence of Authenticity"}
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
                background: textColor 
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
        
        {heatmap?.heatmap_overlay_base64 && (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              Visual Explainability
            </h3>
            <img src={heatmap.heatmap_overlay_base64} alt="Analysis Overlay" style={{ maxWidth: '100%', borderRadius: '8px', border: '1px solid var(--border-color)' }} />
            {heatmap.note && (
              <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                <em>Note: {heatmap.note}</em>
              </p>
            )}
          </div>
        )}
        
      </div>
    </section>
  );
}
