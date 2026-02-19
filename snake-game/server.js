const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3006;
const DIR = '/Users/giteshpoudel/Documents/GitHub/openclaw-projects/snake-game';

const server = http.createServer((req, res) => {
  let filePath = req.url === '/' ? '/index.html' : req.url;
  const fullPath = path.join(DIR, filePath);
  const ext = path.extname(fullPath);
  const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css' };
  
  fs.readFile(fullPath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': types[ext] || 'text/plain' });
    res.end(data);
  });
});

server.listen(PORT, () => console.log(`Snake Game running at http://localhost:${PORT}`));
