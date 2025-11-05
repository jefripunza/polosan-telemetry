// @ts-ignore
export const env = import.meta.env || process.env || {};

let HOST_API = window.location.origin;
if (window.location.hostname.includes("localhost")) {
  HOST_API = env.VITE_HOST_API;
}

export { HOST_API };
