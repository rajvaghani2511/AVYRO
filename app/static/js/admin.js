/**
 * AVYRO Admin Dashboard Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  initImageUploadPreview();
});

function initImageUploadPreview() {
  const fileInput = document.getElementById('productImageInput');
  const previewContainer = document.getElementById('imagePreviewContainer');

  if (!fileInput || !previewContainer) return;

  fileInput.addEventListener('change', (e) => {
    previewContainer.innerHTML = '';
    const files = Array.from(e.target.files);

    files.forEach((file, index) => {
      if (!file.type.startsWith('image/')) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        const col = document.createElement('div');
        col.className = 'col-3 position-relative';
        col.innerHTML = `
          <div class="border rounded overflow-hidden shadow-sm bg-white" style="height: 90px;">
            <img src="${event.target.result}" style="width: 100%; height: 100%; object-fit: cover;">
          </div>
          <span class="badge bg-primary position-absolute top-0 start-0 m-1">${index + 1}</span>
        `;
        previewContainer.appendChild(col);
      };
      reader.readAsDataURL(file);
    });
  });
}
