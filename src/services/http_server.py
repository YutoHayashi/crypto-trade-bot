from threading import Thread
from typing import Optional

from flask import Flask, jsonify


class HttpServer:
    app: Flask
    host: str
    port: int
    debug: bool
    _server_thread: Optional[Thread]
    
    def _register_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'healthy',
            })
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
    
    async def run(self):
        def run_server():
            self.app.run(
                host=self.host,
                port=self.port,
                debug=self.debug,
                use_reloader=False,
                threaded=True
            )
        
        self._server_thread = Thread(target=run_server, daemon=True)
        self._server_thread.start()
    
    def __init__(self, 
                 host: str = '0.0.0.0',
                 port: int = 8080,
                 debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug
        self.app = Flask(__name__)
        self._server_thread = None
        
        self._register_routes()