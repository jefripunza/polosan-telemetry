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

    # ============ PRIVATE: Streaming Multipart Parser ============
    async def _parse_multipart_streaming(self, reader, request_header, content_length, content_type):
        """Parse multipart data dengan streaming untuk menghemat memory"""
        try:
            # Extract boundary
            boundary = b"--" + content_type.split("boundary=")[1].encode('utf-8')
            print(f"Streaming multipart - boundary: {boundary}")
            
            # Parse request line dari header
            header_str = request_header.decode("utf-8", "ignore")
            header_lines = header_str.split("\r\n")
            request_line = header_lines[0]
            parts = request_line.split(' ')
            method = parts[0]
            full_path = parts[1]
            
            # Parse query params
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
            
            body = {}
            files = {}
            
            # Read dan process multipart secara streaming
            bytes_read = 0
            buffer = b""
            current_part = None
            current_file = None
            
            while bytes_read < content_length:
                # Read chunk kecil untuk ESP32
                chunk_size = min(1024, content_length - bytes_read)  # 1KB chunks untuk ESP32
                chunk = await reader.read(chunk_size)
                if not chunk:
                    break
                    
                bytes_read += len(chunk)
                buffer += chunk
                
                # Process buffer untuk mencari boundaries dan parts
                while boundary in buffer:
                    boundary_pos = buffer.find(boundary)
                    
                    if current_part is not None:
                        # Finish current part
                        part_data = buffer[:boundary_pos]
                        if current_file:
                            current_file.write(part_data.rstrip(b"\r\n"))
                            current_file.close()
                            current_file = None
                        current_part = None
                    
                    # Move past boundary
                    buffer = buffer[boundary_pos + len(boundary):]
                    
                    # Look for next part headers
                    if b"\r\n\r\n" in buffer:
                        headers_end = buffer.find(b"\r\n\r\n")
                        headers_bytes = buffer[:headers_end]
                        buffer = buffer[headers_end + 4:]
                        
                        if b"Content-Disposition" in headers_bytes:
                            headers_str = headers_bytes.decode('utf-8', 'ignore')
                            disposition_line = [h for h in headers_str.split("\r\n") if "Content-Disposition" in h][0]
                            
                            if b'filename=' in headers_bytes:
                                # File upload
                                name = disposition_line.split('name="')[1].split('"')[0]
                                filename = disposition_line.split('filename="')[1].split('"')[0]
                                filepath = f"tmp/{filename}"
                                current_file = open(filepath, "wb")
                                files[name] = {"filename": filename, "path": filepath}
                                current_part = "file"
                                print(f"Streaming file: {filepath}")
                            else:
                                # Form field - collect in memory (should be small)
                                current_part = "field"
                                current_field_name = disposition_line.split('name="')[1].split('"')[0]
                                current_field_data = b""
                
                # Write remaining buffer to current file if we're in a file part
                if current_file and current_part == "file":
                    # Keep some buffer for boundary detection
                    if len(buffer) > len(boundary) + 10:
                        write_size = len(buffer) - len(boundary) - 10
                        current_file.write(buffer[:write_size])
                        buffer = buffer[write_size:]
            
            # Close any remaining file
            if current_file:
                current_file.close()
            
            return method, path, body, query_params, files
            
        except Exception as e:
            print(f"Streaming multipart error: {e}")
            # Cleanup on error
            if current_file:
                try:
                    current_file.close()
                except:
                    pass
            return "GET", "/", None, {}, {}

    # ============ PRIVATE: Client Handler ============
    async def _handle_client(self, reader, writer):
        tmp_files = []
        try:
            # baca header manual
            request_header = await self._read_headers(reader)
            header_str = request_header.decode("utf-8", "ignore")

            # cari content-length dan content-type
            content_length = 0
            content_type = ""
            for line in header_str.split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":", 1)[1].strip())
                elif line.lower().startswith("content-type:"):
                    content_type = line.split(":", 1)[1].strip()

            # Jika multipart/form-data dan file besar, gunakan streaming
            if "multipart/form-data" in content_type and content_length > 16384:  # 16KB threshold untuk ESP32
                method, path, body, query_params, files = await self._parse_multipart_streaming(
                    reader, request_header, content_length, content_type
                )
                tmp_files = [info["path"] for info in files.values()]
            else:
                # Untuk request kecil, gunakan method lama
                body_bytes = b""
                while len(body_bytes) < content_length:
                    chunk_size = min(4096, content_length - len(body_bytes))  # Read in 4KB chunks
                    chunk = await reader.read(chunk_size)
                    if not chunk:
                        break
                    body_bytes += chunk

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
            # Cleanup temporary files
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
