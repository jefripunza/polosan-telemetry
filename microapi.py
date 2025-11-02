import uasyncio as asyncio
import json
import os

class Router:
    def __init__(self):
        self.routes = {}
        self.static_routes = {}

        # pastikan ada folder tmp
        try:
            if "tmp" not in os.listdir():
                os.mkdir("tmp")
        except OSError:
            pass

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

    def static(self, url_prefix: str, folder: str):
        if not url_prefix.endswith("/"):
            url_prefix += "/"

        try:
            if folder not in os.listdir():
                os.mkdir(folder)
        except OSError:
            pass

        self.static_routes[url_prefix] = folder

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
    async def _handle_request(self, method, path, body=None, query_params=None, files=None):
        if files is None:
            files = {}

        # print(f"DEBUG: Handling request {method} {path}")
        # print(f"DEBUG: Registered routes: {list(self.routes.keys())}")

        # dynamic route
        matched = False
        for route_key, handler in self.routes.items():
            route_method, route_path = route_key.split(':', 1)
            if route_method != method:
                continue
            path_params = self._match_path_params(route_path, path)
            if path_params is not None:
                matched = True
                return await handler(body, query_params, path_params, files)

        # static file
        for url_prefix, folder in self.static_routes.items():
            if path.startswith(url_prefix):
                rel_path = path[len(url_prefix):]
                if not rel_path or rel_path.endswith("/"):
                    rel_path += "index.html"
                file_path = f"{folder}/{rel_path}".lstrip("/")

                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    return {
                        "content": content,
                        "status": 200,
                        "content_type": self._guess_content_type(file_path),
                    }
                except OSError:
                    return {"error": "Not Found 1", "status": 404}

        if not matched:
            print(f"DEBUG: No route matched for {method} {path}")
        return {"error": "Not Found 2", "status": 404}


    # ============ PRIVATE: HTTP Parsing ============
    def _parse_http_request(self, request_data):
        if not request_data:
            return "GET", "/", None, {}, {}
        try:
            # split header dan body secara bytes
            header_end = request_data.find(b"\r\n\r\n")
            if header_end == -1:
                return "GET", "/", None, {}, {}

            header_bytes = request_data[:header_end]
            body_bytes = request_data[header_end + 4:]

            try:
                header_str = header_bytes.decode('utf-8')
            except Exception as e:
                print("AAA - decode error header only, first 100 bytes:", header_bytes[:100])
                print("Decode exception:", e)
                return "GET", "/", None, {}, {}

            header_lines = header_str.split("\r\n")
            if not header_lines or len(header_lines[0].strip()) == 0:
                print("BBB - empty header line")
                return "GET", "/", None, {}, {}

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

            # cek content-type
            content_type = ""
            for line in header_lines[1:]:
                if line.lower().startswith("content-type:"):
                    content_type = line.split(":", 1)[1].strip()

            body = None
            files = {}

            if "multipart/form-data" in content_type:
                boundary = b"--" + content_type.split("boundary=")[1].encode('utf-8')
                print(f"multipart - boundary: {boundary}")

                parts = body_bytes.split(boundary)
                print(f"multipart - parts found: {len(parts)}")

                for idx, part in enumerate(parts):
                    if b"Content-Disposition" in part:
                        print(f"multipart - processing part {idx}")
                        try:
                            headers_bytes, _, content_bytes = part.partition(b"\r\n\r\n")
                            headers_str = headers_bytes.decode('utf-8', 'ignore')
                            disposition_line = [h for h in headers_str.split("\r\n") if "Content-Disposition" in h][0]

                            if b'filename=' in headers_bytes:
                                name = disposition_line.split('name="')[1].split('"')[0]
                                filename = disposition_line.split('filename="')[1].split('"')[0]
                                filepath = f"tmp/{filename}"
                                with open(filepath, "wb") as f:
                                    f.write(content_bytes.strip(b"\r\n--"))
                                files[name] = {"filename": filename, "path": filepath}
                                print(f"File saved: {filepath}")
                            else:
                                name = disposition_line.split('name="')[1].split('"')[0]
                                value = content_bytes.decode('utf-8', 'ignore').strip()
                                if body is None:
                                    body = {}
                                body[name] = value
                                print(f"Field parsed: {name}={value}")
                        except Exception as e:
                            print(f"Error parsing part {idx}: {e}")
            else:
                # coba json biasa
                try:
                    if body_bytes.strip():
                        body = json.loads(body_bytes.decode('utf-8'))
                        print(f"JSON body: {body}")
                except Exception as e:
                    body = body_bytes  # tetap bytes
                    print(f"Non-JSON body: {body[:100]}, exception: {e}")

            return method, path, body, query_params, files

        except Exception as e:
            print("Parse error:", e)
            return "GET", "/", None, {}, {}

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
        tmp_files = []
        try:
            # baca header manual
            print("A ...")
            request_header = await self._read_headers(reader)
            header_str = request_header.decode("utf-8", "ignore")

            # cari content-length
            print("B ...")
            content_length = 0
            for line in header_str.split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":", 1)[1].strip())

            # baca body sesuai content-length
            print("C ...")
            body_bytes = b""
            while len(body_bytes) < content_length:
                chunk = await reader.read(content_length - len(body_bytes))
                if not chunk:
                    break
                body_bytes += chunk

            print("D ...")
            request = request_header + body_bytes
            method, path, body, query_params, files = self._parse_http_request(request)
            tmp_files = [info["path"] for info in files.values()]

            result = await self._handle_request(method, path, body, query_params, files)

            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                status_code = result.get("status", 200)
                content_type = result.get("content_type", "application/octet-stream")
                if isinstance(content, str):
                    content = content.encode()
            else:
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
        finally:
            for filepath in tmp_files:
                try:
                    os.remove(filepath)
                    print(f"hapus tmp: {filepath}")
                except OSError:
                    pass

    # ============ PRIVATE: Utils ============
    def _guess_content_type(self, filename: str) -> str:
        if filename.endswith(".html"):
            return "text/html"
        elif filename.endswith(".css"):
            return "text/css"
        elif filename.endswith(".js"):
            return "application/javascript"
        elif filename.endswith(".json"):
            return "application/json"
        elif filename.endswith(".png"):
            return "image/png"
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            return "image/jpeg"
        elif filename.endswith(".gif"):
            return "image/gif"
        elif filename.endswith(".svg"):
            return "image/svg+xml"
        elif filename.endswith(".ico"):
            return "image/x-icon"
        elif filename.endswith(".txt"):
            return "text/plain"
        else:
            return "application/octet-stream"

    # ============ PRIVATE: Server Core ============
    async def _start_server(self, host, port, callback):
        server = await asyncio.start_server(self._handle_client, host, port)
        if callback:
            callback()
        await server.wait_closed()
