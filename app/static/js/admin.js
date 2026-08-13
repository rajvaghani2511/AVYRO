/**
 * AVYRO Admin Dashboard Scripts
 * Multi-Image Drag & Drop Dropzone, Client-Side Image Compression & Markdown Editor
 */

document.addEventListener('DOMContentLoaded', () => {
  initMultiImageUploadDropzone();
  initMarkdownEditor();
});

/**
 * Multi-Image Drag & Drop Upload Zone with Automatic Client-Side Compression
 */
function initMultiImageUploadDropzone() {
  const fileInput = document.getElementById('productImageInput');
  const dropzone = document.getElementById('uploadDropzone');
  const previewContainer = document.getElementById('imagePreviewContainer');
  const fileCounter = document.getElementById('selectedFilesCounter');

  if (!fileInput || !previewContainer) return;

  if (dropzone) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => dropzone.classList.add('drag-active'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => dropzone.classList.remove('drag-active'), false);
    });

    dropzone.addEventListener('drop', async (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        await processAndSetFiles(files);
      }
    });
  }

  fileInput.addEventListener('change', async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      await processAndSetFiles(e.target.files);
    }
  });

  async function processAndSetFiles(rawFilesList) {
    const rawFiles = Array.from(rawFilesList);
    if (rawFiles.length === 0) return;

    if (fileCounter) {
      fileCounter.innerText = "Compressing & optimizing images...";
    }

    const dataTransfer = new DataTransfer();

    for (const file of rawFiles) {
      if (file.type.startsWith('image/')) {
        const compressed = await compressImage(file, 1200, 0.82);
        dataTransfer.items.add(compressed);
      } else {
        dataTransfer.items.add(file);
      }
    }

    fileInput.files = dataTransfer.files;
    renderImagePreviews(dataTransfer.files);
  }

  function renderImagePreviews(filesList) {
    previewContainer.innerHTML = '';
    const files = Array.from(filesList);

    let totalSizeMB = 0;
    files.forEach(f => totalSizeMB += f.size / (1024 * 1024));

    if (fileCounter) {
      fileCounter.innerText = files.length > 0 ? `${files.length} images ready (${totalSizeMB.toFixed(2)} MB total)` : '';
    }

    if (files.length === 0) return;

    files.forEach((file, index) => {
      if (!file.type.startsWith('image/')) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        const col = document.createElement('div');
        col.className = 'col-6 col-sm-4 col-md-3';
        col.innerHTML = `
          <div class="card border shadow-sm radius-md overflow-hidden bg-white position-relative text-center">
            <div style="height: 110px; overflow: hidden; background: #f8f9fa;">
              <img src="${event.target.result}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div class="p-2 border-top bg-light">
              <span class="d-block extra-small text-truncate text-dark fw-bold">${file.name}</span>
              <span class="extra-small text-success fw-bold">${(file.size / 1024).toFixed(1)} KB (Optimized)</span>
            </div>
            <span class="badge ${index === 0 ? 'bg-success' : 'bg-dark'} position-absolute top-0 start-0 m-2 shadow-sm radius-pill extra-small">
              ${index === 0 ? '★ MAIN COVER' : `#${index + 1}`}
            </span>
          </div>
        `;
        previewContainer.appendChild(col);
      };
      reader.readAsDataURL(file);
    });
  }
}

/**
 * Compresses heavy images on client-side before form submission to avoid Vercel 4.5MB Payload Limit
 */
function compressImage(file, maxDimension = 1200, quality = 0.82) {
  return new Promise((resolve) => {
    if (!file.type.startsWith('image/') || file.size < 250 * 1024) {
      resolve(file);
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;
      img.onload = () => {
        let width = img.width;
        let height = img.height;

        if (width > maxDimension || height > maxDimension) {
          if (width > height) {
            height = Math.round((height * maxDimension) / width);
            width = maxDimension;
          } else {
            width = Math.round((width * maxDimension) / height);
            height = maxDimension;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (!blob) {
              resolve(file);
              return;
            }
            const compressedFile = new File([blob], file.name.replace(/\.[^/.]+$/, "") + ".jpg", {
              type: 'image/jpeg',
              lastModified: Date.now(),
            });
            resolve(compressedFile);
          },
          'image/jpeg',
          quality
        );
      };
      img.onerror = () => resolve(file);
    };
    reader.onerror = () => resolve(file);
  });
}

/**
 * Markdown Description Editor & Live Preview Toolbar
 */
function initMarkdownEditor() {
  const textarea = document.getElementById('productDescription');
  const previewDiv = document.getElementById('markdownPreview');
  const writeTab = document.getElementById('btnWriteTab');
  const previewTab = document.getElementById('btnPreviewTab');

  if (!textarea) return;

  if (writeTab && previewTab && previewDiv) {
    writeTab.addEventListener('click', (e) => {
      e.preventDefault();
      writeTab.classList.add('active');
      previewTab.classList.remove('active');
      textarea.classList.remove('d-none');
      previewDiv.classList.add('d-none');
    });

    previewTab.addEventListener('click', (e) => {
      e.preventDefault();
      previewTab.classList.add('active');
      writeTab.classList.remove('active');
      textarea.classList.add('d-none');
      previewDiv.classList.remove('d-none');

      previewDiv.innerHTML = parseMarkdownToHTML(textarea.value);
    });
  }
}

function insertMarkdown(prefix, suffix = '') {
  const textarea = document.getElementById('productDescription');
  if (!textarea) return;

  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = textarea.value.substring(start, end) || 'text';
  const replacement = prefix + selectedText + suffix;

  textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
  textarea.focus();
  textarea.setSelectionRange(start + prefix.length, start + prefix.length + selectedText.length);
}

function parseMarkdownToHTML(md) {
  if (!md) return '<em class="text-muted small">No description text provided yet.</em>';

  let html = md
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.*$)/gim, '<h5 class="font-serif fw-bold mt-3 mb-2">$1</h5>')
    .replace(/^## (.*$)/gim, '<h4 class="font-serif fw-bold mt-3 mb-2">$1</h4>')
    .replace(/^# (.*$)/gim, '<h3 class="font-serif fw-bold mt-3 mb-2">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/^\* (.*$)/gim, '<ul><li>$1</li></ul>')
    .replace(/<\/ul>\s*<ul>/g, '')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');

  return `<div class="p-3 bg-light border radius-md text-secondary lh-lg">${html}</div>`;
}
