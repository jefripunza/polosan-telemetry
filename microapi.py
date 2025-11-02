import uasyncio as asyncio
import json

class Router:
    def __init__(self):
        self.routes = {}

    # ============ PUBLIC: Routing API ============
    def get(self, path):
        def decorator(handler):
            self._add_route("GET", path, handler)
            return handler
        return decorator

    def post(self, path):
        def decorator(handler):
            self._add_route("POST", path, handler)
            return handler
        return decorator

    def put(self, path):
        def decorator(handler):
            self._add_route("PUT", path, handler)
            return handler
        return decorator

    def patch(self, path):
        def decorator(handler):
            self._add_route("PATCH", path, handler)
            return handler
        return decorator

    def delete(self, path):
        def decorator(handler):
            self._add_route("DELETE", path, handler)
            return handler
        return decorator


    def listen(self, port=80, host="0.0.0.0", callback=None):
        loop = asyncio.get_event_loop()
        loop.create_task(self._start_server(host, port, callback))
        loop.run_forever()

    # ============ PRIVATE: Routing Core ============
    def _add_route(self, method, path, handler):
        key = f"{method}:{path}"
        self.routes[key] = handler

    def _match_path_params(self, route_path, request_path):
        route_parts = [p for p in route_path.split('/') if p]
        request_parts = [p for p in request_path.split('/') if p]
        if len(route_parts) != len(request_parts):
            return None
        params = {}
        for route_part, request_part in zip(route_parts, request_parts):
            if route_part.startswith(':'):
                param_name = route_part[1:]
                params[param_name] = request_part
            elif route_part != request_part:
                return None
        return params

    # ============ PRIVATE: HTTP Handler Request ============
    async def _handle_request(self, method, path, body=None, query_params=None):
        # dynamic route
        for route_key, handler in self.routes.items():
            route_method, route_path = route_key.split(':', 1)
            if route_method != method:
                continue
            path_params = self._match_path_params(route_path, path)
            if path_params is not None:
                return await handler(body, query_params, path_params)

        return {"error": "Not Found", "status": 404}


    # ============ PRIVATE: HTTP Parsing ============
    def _parse_http_request(self, request_data):
        if not request_data:
            return "GET", "/", None, {}
        try:
            # split header dan body secara bytes
            header_end = request_data.find(b"\r\n\r\n")
            if header_end == -1:
                return "GET", "/", None, {}

            header_bytes = request_data[:header_end]
            body_bytes = request_data[header_end + 4:]

            try:
                header_str = header_bytes.decode('utf-8')
            except Exception as e:
                print("Decode error header:", e)
                return "GET", "/", None, {}

            header_lines = header_str.split("\r\n")
            if not header_lines or len(header_lines[0].strip()) == 0:
                return "GET", "/", None, {}

            # request line
            request_line = header_lines[0]
            parts = request_line.split(' ')
            method = parts[0]
            full_path = parts[1]

            # query params
            if '?' in full_path:
                path, query_string = full_path.split('?', 1)
                query_params = {}
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
            else:
                path = full_path
                query_params = {}

            body = None
            # parse JSON body only
            try:
                if body_bytes.strip():
                    body = json.loads(body_bytes.decode('utf-8'))
            except Exception as e:
                print(f"JSON parse error: {e}")
                body = None

            return method, path, body, query_params

        except Exception as e:
            print("Parse error:", e)
            return "GET", "/", None, {}

    # ============ PRIVATE: Read Headers ============
    async def _read_headers(self, reader):
        data = b""
        while True:
            chunk = await reader.read(1)
            if not chunk:
                break
            data += chunk
            if b"\r\n\r\n" in data:
                break
        return data



    # ============ PRIVATE: Client Handler ============
    async def _handle_client(self, reader, writer):
        try:
            # baca header manual
            request_header = await self._read_headers(reader)
            header_str = request_header.decode("utf-8", "ignore")

            # cari content-length
            content_length = 0
            for line in header_str.split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":", 1)[1].strip())

            # baca body
            body_bytes = b""
            while len(body_bytes) < content_length:
                chunk_size = min(4096, content_length - len(body_bytes))
                chunk = await reader.read(chunk_size)
                if not chunk:
                    break
                body_bytes += chunk

            request = request_header + body_bytes
            method, path, body, query_params = self._parse_http_request(request)

            result = await self._handle_request(method, path, body, query_params)

            # JSON response only
            if isinstance(result, tuple) and len(result) == 2:
                content, status_code = result
            else:
                response_data = {k: v for k, v in result.items() if k != 'status'}
                content = json.dumps(response_data)
                status_code = result.get("status", 200)
            
            content_type = "application/json"
            content = content.encode() if isinstance(content, str) else content

            status_text = "OK" if status_code == 200 else \
                          "Bad Request" if status_code == 400 else \
                          "Not Found" if status_code == 404 else \
                          "Internal Server Error"

            http_response = (
                f"HTTP/1.1 {status_code} {status_text}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode() + content

            await writer.awrite(http_response)
            await writer.aclose()
        except Exception as e:
            print("handle_client Error:", e)


    # ============ PRIVATE: Server Core ============
    async def _start_server(self, host, port, callback):
        server = await asyncio.start_server(self._handle_client, host, port)
        if callback:
            callback()
        await server.wait_closed()
