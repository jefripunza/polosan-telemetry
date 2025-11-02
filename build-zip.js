import fs from 'fs';
import path from 'path';
import archiver from 'archiver';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const distPath = path.join(__dirname, 'dist');
const zipPath = path.join(distPath, 'polosan-telemetry.zip');

// Function to calculate directory size recursively
function getDirSize(dirPath) {
  let totalSize = 0;
  const items = fs.readdirSync(dirPath);
  
  for (const item of items) {
    const itemPath = path.join(dirPath, item);
    const stat = fs.statSync(itemPath);
    
    if (stat.isDirectory()) {
      totalSize += getDirSize(itemPath);
    } else {
      totalSize += stat.size;
    }
  }
  
  return totalSize;
}

async function createZip() {
  // Check if dist folder exists
  if (!fs.existsSync(distPath)) {
    console.error('❌ Folder dist tidak ditemukan. Jalankan build terlebih dahulu.');
    process.exit(1);
  }

  // Create a file to stream archive data to
  const output = fs.createWriteStream(zipPath);
  const archive = archiver('zip', {
    zlib: { 
      level: 9,           // Maximum compression level
      chunkSize: 1024,    // Smaller chunks for better compression
      windowBits: 15,     // Maximum window size
      memLevel: 8         // Maximum memory usage for better compression
    },
    store: false          // Always compress, never just store
  });

  // Calculate original size
  let originalSize = 0;
  
  // Listen for all archive data to be written
  output.on('close', function() {
    const zipSize = archive.pointer();
    const compressionRatio = ((originalSize - zipSize) / originalSize * 100).toFixed(1);
    
    console.log(`✅ Zip berhasil dibuat: ${zipPath}`);
    console.log(`📦 Ukuran asli: ${(originalSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`📦 Ukuran zip: ${(zipSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`🗜️ Kompresi: ${compressionRatio}% lebih kecil`);
  });

  // Good practice to catch warnings (ie stat failures and other non-blocking errors)
  archive.on('warning', function(err) {
    if (err.code === 'ENOENT') {
      console.warn('⚠️ Warning:', err);
    } else {
      throw err;
    }
  });

  // Good practice to catch this error explicitly
  archive.on('error', function(err) {
    console.error('❌ Error saat membuat zip:', err);
    throw err;
  });

  // Pipe archive data to the file
  archive.pipe(output);

  // Read all files and folders in dist directory
  const items = fs.readdirSync(distPath);
  
  for (const item of items) {
    const itemPath = path.join(distPath, item);
    const stat = fs.statSync(itemPath);
    
    // Skip the zip file itself if it already exists
    if (item === 'polosan-telemetry.zip') {
      continue;
    }
    
    if (stat.isDirectory()) {
      // Add directory and its contents recursively
      archive.directory(itemPath, item);
      console.log(`📁 Menambahkan folder: ${item}`);
      // Calculate directory size recursively
      originalSize += getDirSize(itemPath);
    } else {
      // Add file
      archive.file(itemPath, { name: item });
      console.log(`📄 Menambahkan file: ${item} (${(stat.size / 1024).toFixed(1)} KB)`);
      originalSize += stat.size;
    }
  }

  // Finalize the archive (ie we are done appending files but streams have to finish yet)
  await archive.finalize();
}

console.log('🚀 Memulai proses pembuatan zip...');
createZip().catch(console.error);
