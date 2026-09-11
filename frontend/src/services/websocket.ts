type MessageCallback = (data: any) => void;

class SOCWebSocketClient {
  private socket: WebSocket | null = null;
  private callbacks: Set<MessageCallback> = new Set();
  private reconnectInterval: number = 3000;
  private isConnected: boolean = false;

  public connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/soc-stream`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('[+] Connected to SOC Live Event Stream WebSocket');
        this.isConnected = true;
      };

      this.socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.callbacks.forEach((cb) => cb(parsed));
        } catch (err) {
          console.error('[!] Failed to parse WebSocket message:', err);
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        console.warn('[!] SOC WebSocket connection closed. Retrying in 3s...');
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.socket.onerror = (err) => {
        console.error('[!] WebSocket error:', err);
        this.socket?.close();
      };
    } catch (e) {
      console.error('[!] Could not initiate WebSocket connection:', e);
    }
  }

  public subscribe(callback: MessageCallback) {
    this.callbacks.add(callback);
    return () => {
      this.callbacks.delete(callback);
    };
  }

  public send(data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }
}

export const socWebSocket = new SOCWebSocketClient();
