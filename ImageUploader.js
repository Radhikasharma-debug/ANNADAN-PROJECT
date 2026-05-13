import React, { useState, useRef } from 'react';
import '../styles/ImageUploader.css';

const ImageUploader = ({ donationId, onImageUpload, maxImages = 5 }) => {
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

  const validateFile = (file) => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Allowed: PNG, JPG, GIF, WEBP' };
    }
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: 'File too large. Maximum 5MB allowed' };
    }
    if (images.length >= maxImages) {
      return { valid: false, error: `Maximum ${maxImages} images allowed` };
    }
    return { valid: true };
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files || []);
    setError('');
    setSuccess('');

    for (const file of files) {
      const validation = validateFile(file);
      if (!validation.valid) {
        setError(validation.error);
        continue;
      }

      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        const newImage = {
          id: Date.now() + Math.random(),
          file,
          preview: event.target.result,
          uploading: false,
          error: null,
        };
        setImages((prev) => [...prev, newImage]);
      };
      reader.readAsDataURL(file);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async (imageId) => {
    const imageObj = images.find((img) => img.id === imageId);
    if (!imageObj || !donationId) return;

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', imageObj.file);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `/api/donors/donation/${donationId}/upload-image`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Upload failed');
      }

      const data = await response.json();

      // Update image state
      setImages((prev) =>
        prev.map((img) =>
          img.id === imageId
            ? { ...img, uploading: false, uploaded: true, error: null }
            : img
        )
      );

      setSuccess(`Image uploaded! (${data.total_images}/${maxImages})`);

      if (onImageUpload) {
        onImageUpload(data);
      }

      // Auto-remove after 3 seconds if fully uploaded
      setTimeout(() => {
        setImages((prev) => prev.filter((img) => img.id !== imageId));
      }, 2000);
    } catch (err) {
      setUploading(false);
      setImages((prev) =>
        prev.map((img) =>
          img.id === imageId
            ? { ...img, uploading: false, error: err.message }
            : img
        )
      );
    }
  };

  const handleRemoveLocal = (imageId) => {
    setImages((prev) => prev.filter((img) => img.id !== imageId));
    setError('');
    setSuccess('');
  };

  const handleDeleteUploaded = async (imageId, imageIndex) => {
    if (!donationId) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `/api/donors/donation/${donationId}/image/${imageIndex}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Delete failed');
      }

      setSuccess('Image deleted successfully');
      setImages((prev) => prev.filter((img) => img.id !== imageId));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const files = e.dataTransfer.files;
    handleFileSelect({ target: { files } });
  };

  const pendingCount = images.filter((img) => !img.uploaded).length;
  const uploadedCount = images.filter((img) => img.uploaded).length;

  return (
    <div className="image-uploader">
      <div className="uploader-header">
        <h3>📸 Upload Food Photos</h3>
        <p className="image-count">
          {uploadedCount} uploaded, {pendingCount} pending
          <span className="max-info">/ {maxImages} max</span>
        </p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Drop Zone */}
      <div
        className="drop-zone"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          disabled={uploading || images.length >= maxImages}
          style={{ display: 'none' }}
        />
        <div className="drop-content">
          <span className="drop-icon">📁</span>
          <p className="drop-text">Drag images here or click to select</p>
          <p className="drop-hint">PNG, JPG, GIF, WEBP • Max 5MB each</p>
        </div>
      </div>

      {/* Image Grid */}
      {images.length > 0 && (
        <div className="images-grid">
          {images.map((image) => (
            <div key={image.id} className="image-card">
              <div className="image-preview">
                <img src={image.preview} alt="preview" />
                {image.uploaded && (
                  <div className="upload-badge success">✓ Uploaded</div>
                )}
                {image.uploading && (
                  <div className="upload-badge loading">⏳ Uploading...</div>
                )}
                {image.error && (
                  <div className="upload-badge error">✗ Error</div>
                )}
              </div>

              <div className="image-info">
                <p className="filename" title={image.file.name}>
                  {image.file.name.substring(0, 20)}...
                </p>
                <p className="filesize">
                  {(image.file.size / 1024).toFixed(1)} KB
                </p>
              </div>

              <div className="image-actions">
                {!image.uploaded && !image.uploading && (
                  <>
                    <button
                      className="btn-upload"
                      onClick={() => handleUpload(image.id)}
                      disabled={uploading}
                      title="Upload this image"
                    >
                      Upload
                    </button>
                    <button
                      className="btn-remove"
                      onClick={() => handleRemoveLocal(image.id)}
                      disabled={uploading}
                      title="Remove before uploading"
                    >
                      Remove
                    </button>
                  </>
                )}
                {image.uploading && (
                  <button className="btn-uploading" disabled>
                    Uploading...
                  </button>
                )}
                {image.uploaded && (
                  <button
                    className="btn-delete"
                    onClick={() => handleDeleteUploaded(image.id, images.indexOf(image))}
                    title="Delete uploaded image"
                  >
                    Delete
                  </button>
                )}
              </div>

              {image.error && (
                <div className="error-message">{image.error}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload Tips */}
      <div className="uploader-tips">
        <ul>
          <li>📷 Clear photos help NGOs verify food quality</li>
          <li>🔒 Images are stored securely with your donation</li>
          <li>⚡ Max 5 images per donation</li>
          <li>✅ Supported: PNG, JPG, GIF, WEBP (5MB max)</li>
        </ul>
      </div>
    </div>
  );
};

export default ImageUploader;
