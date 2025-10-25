/**
 * Web UI Server for Permission Management
 * Provides a browser-based interface for approving/denying tool requests
 */

import http from 'http';
import { getPendingRequests, resolveWebRequest } from './enhanced-gatekeeper';

const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archon Permission Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
            text-align: center;
        }
        .header h1 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
        }
        .request-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            margin-bottom: 15px;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .request-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        .request-title {
            font-size: 1.3em;
            color: #333;
            font-weight: 600;
        }
        .request-time {
            color: #999;
            font-size: 0.9em;
        }
        .request-details {
            margin: 15px 0;
        }
        .detail-row {
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid #f5f5f5;
        }
        .detail-label {
            width: 120px;
            font-weight: 600;
            color: #555;
        }
        .detail-value {
            flex: 1;
            color: #333;
            font-family: 'Courier New', monospace;
        }
        .action-read { color: #3b82f6; }
        .action-write { color: #10b981; }
        .action-edit { color: #f59e0b; }
        .action-delete { color: #ef4444; }
        .action-find { color: #06b6d4; }
        .action-execute { color: #8b5cf6; }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            flex: 1;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-approve {
            background: #10b981;
            color: white;
        }
        .btn-approve:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4);
        }
        .btn-deny {
            background: #ef4444;
            color: white;
        }
        .btn-deny:hover {
            background: #dc2626;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(239, 68, 68, 0.4);
        }
        .empty-state {
            background: white;
            padding: 60px 30px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            text-align: center;
        }
        .empty-state-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        .empty-state h2 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .empty-state p {
            color: #666;
        }
        .icon {
            font-size: 1.5em;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Archon Permission Manager</h1>
            <p>Review and approve tool execution requests</p>
        </div>
        <div id="requests"></div>
    </div>

    <script>
        function getActionClass(action) {
            return 'action-' + action.toLowerCase();
        }

        function getActionIcon(action) {
            const icons = {
                'read': '📖',
                'write': '✍️',
                'edit': '📝',
                'delete': '🗑️',
                'find': '🔍',
                'execute': '⚡',
                'exec': '⚡'
            };
            return icons[action.toLowerCase()] || '🔧';
        }

        function formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString();
        }

        function handleResponse(requestId, granted) {
            fetch('/api/respond', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ requestId, granted })
            }).then(() => {
                loadRequests();
            });
        }

        function renderRequests(requests) {
            const container = document.getElementById('requests');

            if (requests.length === 0) {
                container.innerHTML = \`
                    <div class="empty-state">
                        <div class="empty-state-icon">✨</div>
                        <h2>All Clear!</h2>
                        <p>No pending permission requests</p>
                    </div>
                \`;
                return;
            }

            container.innerHTML = requests.map(req => \`
                <div class="request-card">
                    <div class="request-header">
                        <div class="request-title">
                            <span class="icon">🔒</span>
                            Permission Request
                        </div>
                        <div class="request-time">\${formatTime(req.timestamp)}</div>
                    </div>
                    <div class="request-details">
                        <div class="detail-row">
                            <div class="detail-label">Archon:</div>
                            <div class="detail-value">\${req.archon}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Action:</div>
                            <div class="detail-value \${getActionClass(req.action)}">
                                \${getActionIcon(req.action)} \${req.action.toUpperCase()}
                            </div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Resource:</div>
                            <div class="detail-value">\${req.resource}</div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="btn-approve" onclick="handleResponse('\${req.id}', true)">
                            ✅ Approve
                        </button>
                        <button class="btn-deny" onclick="handleResponse('\${req.id}', false)">
                            ❌ Deny
                        </button>
                    </div>
                </div>
            \`).join('');
        }

        function loadRequests() {
            fetch('/api/requests')
                .then(res => res.json())
                .then(renderRequests);
        }

        // Load requests every 2 seconds
        loadRequests();
        setInterval(loadRequests, 2000);
    </script>
</body>
</html>
`;

/**
 * Start web UI server for permission management
 */
export function startWebUIServer(port: number = 3000): http.Server {
  const server = http.createServer((req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    // Routes
    if (req.url === '/' || req.url === '/permissions') {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(HTML_TEMPLATE);
    } else if (req.url === '/api/requests') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(getPendingRequests()));
    } else if (req.url === '/api/respond' && req.method === 'POST') {
      let body = '';
      req.on('data', chunk => (body += chunk));
      req.on('end', () => {
        try {
          const { requestId, granted } = JSON.parse(body);
          const success = resolveWebRequest(requestId, granted);

          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success }));
        } catch (error) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Invalid request' }));
        }
      });
    } else {
      res.writeHead(404);
      res.end('Not Found');
    }
  });

  server.listen(port, () => {
    console.log(`\n🌐 Permission Web UI started at http://localhost:${port}/permissions\n`);
  });

  return server;
}

/**
 * Stop web UI server
 */
export function stopWebUIServer(server: http.Server): Promise<void> {
  return new Promise((resolve) => {
    server.close(() => {
      console.log('\n🛑 Permission Web UI stopped\n');
      resolve();
    });
  });
}
