// Automatically detect the API base URL from the current page
const API_BASE = `${window.location.origin}/api`;

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Load files if list tab
        if (tabName === 'list') {
            loadFiles();
        }
    });
});

// Download URL generation
document.getElementById('download-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultDiv = document.getElementById('download-result');
    resultDiv.className = 'result';
    resultDiv.innerHTML = '<div class="loading">Generating URL...</div>';
    resultDiv.style.display = 'block';
    
    try {
        const fileName = document.getElementById('download-file-name').value;
        const expiration = parseInt(document.getElementById('download-expiration').value);
        
        const response = await fetch(`${API_BASE}/generate-download-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_name: fileName,
                expiration: expiration
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const expiresAt = new Date(data.expires_at * 1000).toLocaleString();
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <strong>✅ Download URL Generated Successfully!</strong>
                <p><strong>File:</strong> ${data.file_name}</p>
                <p><strong>Expires in:</strong> ${data.expiration_seconds} seconds</p>
                <p><strong>Expires at:</strong> ${expiresAt}</p>
                <pre>${data.url}</pre>
                <a href="${data.url}" target="_blank" class="url-link">🔗 Open Download URL</a>
            `;
        } else {
            throw new Error(data.error || 'Failed to generate URL');
        }
    } catch (error) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${error.message}`;
    }
});

// Upload URL generation
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultDiv = document.getElementById('upload-result');
    resultDiv.className = 'result';
    resultDiv.innerHTML = '<div class="loading">Generating URL...</div>';
    resultDiv.style.display = 'block';
    
    try {
        const fileName = document.getElementById('upload-file-name').value;
        const expiration = parseInt(document.getElementById('upload-expiration').value);
        
        const response = await fetch(`${API_BASE}/generate-upload-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_name: fileName,
                expiration: expiration
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const expiresAt = new Date(data.expires_at * 1000).toLocaleString();
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <strong>✅ Upload URL Generated Successfully!</strong>
                <p><strong>File:</strong> ${data.file_name}</p>
                <p><strong>Expires in:</strong> ${data.expiration_seconds} seconds</p>
                <p><strong>Expires at:</strong> ${expiresAt}</p>
                <pre>${data.url}</pre>
            `;
            
            // Store URL for upload test
            window.uploadUrl = data.url;
            window.uploadFileName = data.file_name;
            document.getElementById('upload-test-section').style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to generate URL');
        }
    } catch (error) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${error.message}`;
    }
});

// Upload file test
document.getElementById('upload-test-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultDiv = document.getElementById('upload-test-result');
    const fileInput = document.getElementById('file-input');
    
    if (!fileInput.files.length) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = '<strong>❌ Error:</strong> Please select a file';
        resultDiv.style.display = 'block';
        return;
    }
    
    if (!window.uploadUrl) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = '<strong>❌ Error:</strong> Please generate an upload URL first';
        resultDiv.style.display = 'block';
        return;
    }
    
    resultDiv.className = 'result';
    resultDiv.innerHTML = '<div class="loading">Uploading file...</div>';
    resultDiv.style.display = 'block';
    
    try {
        const file = fileInput.files[0];
        
        const response = await fetch(window.uploadUrl, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': file.type
            }
        });
        
        if (response.ok) {
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <strong>✅ File Uploaded Successfully!</strong>
                <p><strong>File:</strong> ${window.uploadFileName}</p>
                <p>Status: ${response.status} ${response.statusText}</p>
            `;
            
            // Clear file input
            fileInput.value = '';
            
            // Refresh files list if on list tab
            if (document.getElementById('list-tab').classList.contains('active')) {
                loadFiles();
            }
        } else {
            throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }
    } catch (error) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${error.message}`;
    }
});

// Load files list
async function loadFiles() {
    const filesListDiv = document.getElementById('files-list');
    filesListDiv.innerHTML = '<div class="loading">Loading files...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/list-files`);
        const data = await response.json();
        
        if (data.success) {
            if (data.files.length === 0) {
                filesListDiv.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📁</div>
                        <p>No files found in the bucket</p>
                    </div>
                `;
            } else {
                filesListDiv.innerHTML = data.files.map(file => {
                    const size = formatFileSize(file.size);
                    const date = new Date(file.last_modified).toLocaleString();
                    return `
                        <div class="file-item">
                            <div class="file-item-info">
                                <div class="file-item-name">${file.name}</div>
                                <div class="file-item-meta">Size: ${size} • Modified: ${date}</div>
                            </div>
                            <div class="file-item-actions">
                                <button class="btn btn-primary btn-small" onclick="generateDownloadUrlForFile('${file.name}')">
                                    Generate Download URL
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        } else {
            throw new Error(data.error || 'Failed to load files');
        }
    } catch (error) {
        filesListDiv.innerHTML = `
            <div class="result error">
                <strong>❌ Error:</strong> ${error.message}
            </div>
        `;
    }
}

// Generate download URL for a file from the list
async function generateDownloadUrlForFile(fileName) {
    const resultDiv = document.getElementById('download-result');
    resultDiv.className = 'result';
    resultDiv.innerHTML = '<div class="loading">Generating URL...</div>';
    resultDiv.style.display = 'block';
    
    // Switch to download tab
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelector('[data-tab="download"]').classList.add('active');
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById('download-tab').classList.add('active');
    
    // Set file name
    document.getElementById('download-file-name').value = fileName;
    
    try {
        const response = await fetch(`${API_BASE}/generate-download-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_name: fileName,
                expiration: 3600
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const expiresAt = new Date(data.expires_at * 1000).toLocaleString();
            resultDiv.className = 'result success';
            resultDiv.innerHTML = `
                <strong>✅ Download URL Generated Successfully!</strong>
                <p><strong>File:</strong> ${data.file_name}</p>
                <p><strong>Expires in:</strong> ${data.expiration_seconds} seconds</p>
                <p><strong>Expires at:</strong> ${expiresAt}</p>
                <pre>${data.url}</pre>
                <a href="${data.url}" target="_blank" class="url-link">🔗 Open Download URL</a>
            `;
        } else {
            throw new Error(data.error || 'Failed to generate URL');
        }
    } catch (error) {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${error.message}`;
    }
}

// Refresh files button
document.getElementById('refresh-files').addEventListener('click', loadFiles);

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

