const fs = require('fs');
const path = require('path');

const root = process.cwd();
const fromPublic = path.join(root, 'public');
const fromStatic = path.join(root, '.next', 'static');
const toRoot = path.join(root, '.next', 'standalone');

// Ensure directories exist
fs.mkdirSync(path.join(toRoot, 'public'), { recursive: true });
fs.mkdirSync(path.join(toRoot, '.next', 'static'), { recursive: true });

// Copy public assets
if (fs.existsSync(fromPublic)) {
  copyDir(fromPublic, path.join(toRoot, 'public'));
}

// Copy static assets
if (fs.existsSync(fromStatic)) {
  copyDir(fromStatic, path.join(toRoot, '.next', 'static'));
}

console.log('postbuild: assets copied to standalone');

function copyDir(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}
