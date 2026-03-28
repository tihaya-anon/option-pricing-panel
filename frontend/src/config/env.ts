const TRUE_FLAG = "true";

export const appMode = import.meta.env.MODE;
export const isMockEnabled = import.meta.env.VITE_ENABLE_API_MOCK === TRUE_FLAG;
export const apiProxyTarget = import.meta.env.VITE_API_PROXY_TARGET;
