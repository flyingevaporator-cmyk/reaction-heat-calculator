#!/usr/bin/env node
'use strict';

// PostToolUse hook: Auto-lint TypeScript/TSX files after Edit or Write.
// Targets frontend/ and pfd-generator/ directories.
// Returns lint errors as actionable feedback to Claude.

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

let input;
try {
  input = JSON.parse(fs.readFileSync(0, 'utf8'));
} catch {
  process.exit(0);
}

const toolName = input.tool_name || '';
const toolInput = input.tool_input || {};

// Only run after Edit or Write
if (toolName !== 'Edit' && toolName !== 'Write') {
  process.exit(0);
}

const filePath = (toolInput.file_path || '').replace(/\\/g, '/');

// Determine which project the file belongs to
const projectRoot = __dirname.replace(/\/.claude\/hooks$/, '').replace(/\\/g, '/');
const relativePath = filePath.startsWith(projectRoot)
  ? filePath.slice(projectRoot.length + 1)
  : filePath;

let lintDir = null;
if (/\.(ts|tsx)$/.test(relativePath)) {
  if (relativePath.startsWith('frontend/')) {
    lintDir = path.join(projectRoot, 'frontend');
  } else if (relativePath.startsWith('pfd-generator/')) {
    lintDir = path.join(projectRoot, 'pfd-generator');
  }
}

if (!lintDir) {
  process.exit(0);
}

// Check node_modules exists
if (!fs.existsSync(path.join(lintDir, 'node_modules'))) {
  process.exit(0);
}

try {
  execSync(`npx eslint --no-warn-ignored "${filePath}"`, {
    cwd: lintDir,
    encoding: 'utf8',
    timeout: 30000,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  // Lint passed — no output needed
} catch (err) {
  const stdout = (err.stdout || '').trim();
  const stderr = (err.stderr || '').trim();
  const lintOutput = stdout || stderr;

  if (lintOutput) {
    const result = {
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        notification: `⚠ ESLint errors in ${path.basename(filePath)}:\n${lintOutput}\nPlease fix these lint errors.`,
      },
    };
    process.stdout.write(JSON.stringify(result));
  }
}
