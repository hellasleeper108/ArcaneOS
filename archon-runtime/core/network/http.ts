import https from 'https';
import http from 'http';
import { URL } from 'url';
import { HttpRequestArgs, HttpRequestResult } from '../types';
import { requestPermission } from '../../permissions/enhanced-gatekeeper';

/**
 * Make HTTP/HTTPS request
 */
export async function httpRequest(args: HttpRequestArgs): Promise<HttpRequestResult> {
  try {
    // Request permission
    const allowed = await requestPermission('http-request', args.url);
    if (!allowed) {
      return {
        success: false,
        error: 'Permission denied by user'
      };
    }

    // Parse URL
    const url = new URL(args.url);
    const isHttps = url.protocol === 'https:';
    const client = isHttps ? https : http;

    // Prepare request options
    const headers: Record<string, string> = { ...(args.headers || {}) };

    // Handle request body
    let bodyData: string | undefined;
    if (args.body) {
      if (typeof args.body === 'object') {
        bodyData = JSON.stringify(args.body);
        headers['Content-Type'] = 'application/json';
        headers['Content-Length'] = Buffer.byteLength(bodyData).toString();
      } else {
        bodyData = args.body;
        headers['Content-Length'] = Buffer.byteLength(bodyData).toString();
      }
    }

    const options: https.RequestOptions = {
      method: args.method || 'GET',
      headers
    };

    return new Promise((resolve) => {
      const req = client.request(url, options, (res) => {
        let body = '';

        res.on('data', (chunk) => {
          body += chunk;
        });

        res.on('end', () => {
          resolve({
            success: res.statusCode! >= 200 && res.statusCode! < 300,
            status: res.statusCode,
            headers: res.headers as Record<string, string>,
            body
          });
        });
      });

      req.on('error', (error) => {
        resolve({
          success: false,
          error: error.message
        });
      });

      // Set timeout
      const timeout = args.timeout || 30000;
      req.setTimeout(timeout, () => {
        req.destroy();
        resolve({
          success: false,
          error: `Request timeout after ${timeout}ms`
        });
      });

      // Write body if present
      if (bodyData) {
        req.write(bodyData);
      }

      req.end();
    });

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}
