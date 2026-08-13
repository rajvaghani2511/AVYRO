/**
 * AVYRO Admin Dashboard Scripts
 * Multi-Image Drag & Drop Dropzone & Markdown Description Editor
 */

document.addEventListener('DOMContentLoaded', () => {
  initMultiImageUploadDropzone();
  initMarkdownEditor();
});

/**
 * Multi-Image Drag & Drop Upload Zone
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

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        fileInput.files = files;
        renderImagePreviews(files);
      }
    });
  }

  fileInput.addEventListener('change', (e) => {
    renderImagePreviews(e.target.files);
  });

  function renderImagePreviews(filesList) {
    previewContainer.innerHTML = '';
    const files = Array.from(filesList);

    if (fileCounter) {
      fileCounter.innerText = files.length > 0 ? `${files.length} images selected` : '';
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
              <span class="extra-small text-muted">${(file.size / 1024).toFixed(1)} KB</span>
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

      // Convert Markdown to clean HTML
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
