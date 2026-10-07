import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const contractsDir = path.resolve(__dirname, '../../contracts');
const contractsExamplesDir = path.resolve(__dirname, '../../contracts/examples');
const mocksTargetDir = path.resolve(__dirname, '../src/mocks');
const publicTargetDir = path.resolve(__dirname, '../public');

if (!fs.existsSync(mocksTargetDir)) {
  fs.mkdirSync(mocksTargetDir, { recursive: true });
}

if (!fs.existsSync(publicTargetDir)) {
  fs.mkdirSync(publicTargetDir, { recursive: true });
}

console.log('Syncing contracts to frontend/src/mocks/...');

if (fs.existsSync(path.join(contractsDir, 'labels.json'))) {
  fs.copyFileSync(path.join(contractsDir, 'labels.json'), path.join(mocksTargetDir, 'labels.json'));
  console.log('  - Synced labels.json -> src/mocks/');
}

if (fs.existsSync(contractsExamplesDir)) {
  const files = fs.readdirSync(contractsExamplesDir);
  for (const file of files) {
    const srcPath = path.join(contractsExamplesDir, file);
    if (file.endsWith('.json')) {
      const destPath = path.join(mocksTargetDir, file);
      fs.copyFileSync(srcPath, destPath);
      console.log(`  - Synced ${file} -> src/mocks/`);
    } else if (file === 'report_sample.csv') {
      const destPath = path.join(publicTargetDir, 'mock_report.csv');
      fs.copyFileSync(srcPath, destPath);
      console.log(`  - Synced report_sample.csv -> public/mock_report.csv`);
    }
  }
} else {
  console.warn('contracts/examples directory not found! Skipping sync.');
}
