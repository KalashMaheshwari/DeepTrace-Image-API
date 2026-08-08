import React, { useRef, useState } from 'react';
import { Upload, X } from 'lucide-react';

export default function Dropzone({ onFileSelect, selectedFile, onRemoveFile }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
      alert("Please upload a valid image or video file.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      onFileSelect(file, e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="dropzone-container">
      <div 
        className={`dropzone ${isDragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept="image/*,video/mp4,video/quicktime" 
          hidden 
        />
        
        {!selectedFile ? (
          <div className="dropzone-content">
            <Upload size={24} className="dropzone-icon" />
            <div className="dropzone-text">Click or drag file to this area to upload</div>
            <div className="dropzone-subtext">Supports JPEG, PNG, WEBP, MP4, MOV</div>
          </div>
        ) : (
          <div className="image-preview-wrapper">
            <div className="preview-info">
              {selectedFile.file.type.startsWith('video/') ? (
                <video src={selectedFile.previewUrl} className="preview-img" style={{background: '#000', objectFit: 'contain'}} controls />
              ) : (
                <img src={selectedFile.previewUrl} alt="Preview" className="preview-img" />
              )}
              <span className="preview-name">{selectedFile.file.name}</span>
            </div>
            <button 
              className="remove-btn" 
              onClick={(e) => {
                e.stopPropagation();
                onRemoveFile();
                if(fileInputRef.current) fileInputRef.current.value = '';
              }}
              aria-label="Remove file"
            >
              <X size={16} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
