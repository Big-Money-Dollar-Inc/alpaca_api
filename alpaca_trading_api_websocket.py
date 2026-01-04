# alpaca_trading_api_websocket.py

import json
import threading
import time
import msgpack
from websocket import WebSocketApp, ABNF
from typing import Callable, List, Optional, Any

class AlpacaTradingAPIWebSocket:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        use_paper: bool = True,
        on_message_callback: Optional[Callable[[dict], Any]] = None,
    ):
        """
        :param on_message_callback:
           A function that takes a single dict (the parsed JSON/msgpack payload).
           If None, defaults to pretty‐printing to stdout.
        """
        self.api_key    = api_key
        self.api_secret = api_secret
        self.url        = (
            "wss://paper-api.alpaca.markets/stream"
            if use_paper
            else "wss://api.alpaca.markets/stream"
        )
        self.streams    = ["trade_updates"]
        self._handler   = on_message_callback or (lambda msg: print(json.dumps(msg, indent=2)))
        self.ws: WebSocketApp = WebSocketApp("")

    def connect(self, streams: List[str]):
        if streams:
            self.streams = streams

        # Only on_data & on_open/on_error/on_close — no on_message
        self.ws = WebSocketApp(
            self.url,
            on_open = self._on_open,
            on_data = self._on_data,
            on_error= self._on_error,
            on_close= self._on_close,
        )

        thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        thread.start()

    def _on_open(self, ws):
        ws.send(json.dumps({
            "action": "auth",
            "key":    self.api_key,
            "secret": self.api_secret
        }))
        ws.send(json.dumps({
            "action": "listen",
            "data": {"streams": self.streams}
        }))
        print("Authenticated & listening to:", self.streams)

    def _on_data(self, ws, raw, data_type: int, _):
        """
        Handles all incoming frames:
         - OPCODE_TEXT   (text JSON)
         - OPCODE_BINARY (msgpack or JSON-over-binary)
         - OPCODE_PONG   (heartbeat)
        """
        # 1) PONG — ignore or log
        if data_type == ABNF.OPCODE_PONG:
            # print("← PONG")
            return

        # 2) Try msgpack for binary frames
        if data_type == ABNF.OPCODE_BINARY:
            try:
                msg = msgpack.unpackb(raw, raw=False)
                return self._handler(msg)
            except Exception:
                # fallback to JSON-over-binary
                try:
                    text = raw.decode("utf-8")
                    msg  = json.loads(text)
                    return self._handler(msg)
                except Exception as e:
                    print("Error parsing binary frame:", e)
                    return

        # 3) Text frames arrive here as UTF-8 bytes
        if data_type == ABNF.OPCODE_TEXT:
            try:
                text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
                msg  = json.loads(text)
                return self._handler(msg)
            except Exception as e:
                print("Error parsing text frame:", e)

    def set_streams(self, streams: list):
        self.streams = streams
        print(f"Streams set to: {self.streams}")
        if self.ws is not None and self.ws.sock is not None and self.ws.sock.connected is True:
            self.ws.send(json.dumps({
                "action": "listen",
                "data": {"streams": self.streams}
            }))
            print("Updated listening streams to:", self.streams)

    def _on_error(self, ws, error):
        print("WebSocket error:", error)

    def _on_close(self, ws, code, msg):
        print(f"WebSocket closed ({code}): {msg} — reconnecting in 5s…")
        time.sleep(5)
        self.connect(self.streams)

    def close(self):
        if self.ws:
            self.ws.close()
            print("WebSocket connection closed.")
