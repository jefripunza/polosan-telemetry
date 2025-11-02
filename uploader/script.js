// Global variables
let zipFiles = [];
let currentZip = null;

// DOM elements
const zipFileInput = document.getElementById('zipFileInput');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const fileListSection = document.getElementById('fileListSection');
const fileTableBody = document.getElementById('fileTableBody');
const uploadButton = document.getElementById('uploadButton');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

// Event listeners
zipFileInput.addEventListener('change', handleFileSelect);

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    
    // Reset UI
    hideMessages();
    hideFileList();
    hideProgress();
    
    if (!file) {
        return;
    }
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.zip')) {
        showError('Error: File harus berformat ZIP!');
        zipFileInput.value = '';
        return;
    }
    
    // Validate file size (optional - you can adjust this limit)
    const maxSize = 100 * 1024 * 1024; // 100MB limit
    if (file.size > maxSize) {
        showError('Error: File ZIP terlalu besar! Maksimal 100MB.');
        zipFileInput.value = '';
        return;
    }
    
    // Process ZIP file
    processZipFile(file);
}

// Process ZIP file and extract file list
async function processZipFile(file) {
    try {
        showSuccess('Memproses file ZIP...');
        
        const zip = new JSZip();
        const zipContent = await zip.loadAsync(file);
        currentZip = zipContent;
        zipFiles = [];
        
        // Extract file information
        zipContent.forEach((relativePath, zipEntry) => {
            // Skip directories
            if (!zipEntry.dir) {
                zipFiles.push({
                    path: relativePath,
                    size: zipEntry._data ? zipEntry._data.uncompressedSize : 0,
                    selected: true, // Default checked
                    zipEntry: zipEntry
                });
            }
        });
        
        if (zipFiles.length === 0) {
            showError('Error: File ZIP kosong atau tidak mengandung file!');
            return;
        }
        
        // Sort files by path
        zipFiles.sort((a, b) => a.path.localeCompare(b.path));
        
        // Display file list
        displayFileList();
        showSuccess(`Berhasil memuat ${zipFiles.length} file dari ZIP.`);
        
    } catch (error) {
        console.error('Error processing ZIP:', error);
        showError('Error: Gagal memproses file ZIP. Pastikan file tidak corrupt.');
    }
}

// Display file list in table
function displayFileList() {
    fileTableBody.innerHTML = '';
    
    zipFiles.forEach((file, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td title="${file.path}">${file.path}</td>
            <td class="size-column">${formatFileSize(file.size)}</td>
            <td class="checkbox-column">
                <input type="checkbox" 
                       id="file_${index}" 
                       ${file.selected ? 'checked' : ''} 
                       onchange="toggleFileSelection(${index})">
            </td>
        `;
        fileTableBody.appendChild(row);
    });
    
    fileListSection.style.display = 'block';
    updateUploadButton();
}

// Toggle file selection
function toggleFileSelection(index) {
    zipFiles[index].selected = !zipFiles[index].selected;
    updateUploadButton();
}

// Select all files
function selectAll() {
    zipFiles.forEach((file, index) => {
        file.selected = true;
        const checkbox = document.getElementById(`file_${index}`);
        if (checkbox) checkbox.checked = true;
    });
    updateUploadButton();
}

// Deselect all files
function deselectAll() {
    zipFiles.forEach((file, index) => {
        file.selected = false;
        const checkbox = document.getElementById(`file_${index}`);
        if (checkbox) checkbox.checked = false;
    });
    updateUploadButton();
}

// Update upload button state
function updateUploadButton() {
    const selectedCount = zipFiles.filter(file => file.selected).length;
    uploadButton.disabled = selectedCount === 0;
    uploadButton.textContent = `Mulai Upload (${selectedCount} file)`;
}

// Start upload process
async function startUpload() {
    const selectedFiles = zipFiles.filter(file => file.selected);
    
    if (selectedFiles.length === 0) {
        showError('Error: Tidak ada file yang dipilih untuk diupload!');
        return;
    }
    
    // Disable upload button and show progress
    uploadButton.disabled = true;
    showProgress();
    hideMessages();
    
    let uploadedCount = 0;
    let failedCount = 0;
    const totalFiles = selectedFiles.length;
    
    try {
        for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            
            // Update progress
            updateProgress(uploadedCount, totalFiles, `Uploading: ${file.path}`);
            
            try {
                // Get file content as base64
                const content = await file.zipEntry.async('base64');
                
                // Upload file
                await uploadSingleFile(file.path, content);
                uploadedCount++;
                
                // Update progress
                updateProgress(uploadedCount, totalFiles, `Uploaded: ${file.path}`);
                
                // Small delay to prevent overwhelming the server
                await sleep(100);
                
            } catch (error) {
                console.error(`Failed to upload ${file.path}:`, error);
                failedCount++;
                updateProgress(uploadedCount, totalFiles, `Failed: ${file.path}`);
            }
        }
        
        // Show final result
        if (failedCount === 0) {
            showSuccess(`Upload selesai! ${uploadedCount} file berhasil diupload.`);
        } else {
            showError(`Upload selesai dengan ${failedCount} error. ${uploadedCount} file berhasil, ${failedCount} file gagal.`);
        }
        
    } catch (error) {
        console.error('Upload process failed:', error);
        showError('Error: Proses upload gagal!');
    } finally {
        uploadButton.disabled = false;
        updateUploadButton();
    }
}

// Upload single file to API
async function uploadSingleFile(path, content) {
    const response = await fetch('/api/upload/ok', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            path: path,
            content: content
        })
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    return response.json();
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
}

function hideMessages() {
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
}

function hideFileList() {
    fileListSection.style.display = 'none';
}

function showProgress() {
    progressSection.style.display = 'block';
}

function hideProgress() {
    progressSection.style.display = 'none';
}

function updateProgress(current, total, message) {
    const percentage = total > 0 ? (current / total) * 100 : 0;
    progressFill.style.width = percentage + '%';
    progressText.textContent = `${current} / ${total} files uploaded - ${message}`;
}
