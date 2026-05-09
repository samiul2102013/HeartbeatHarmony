const ACCESS = "heartbeat_admin_access";
const REFRESH = "heartbeat_admin_refresh";
const ACCESS_COOKIE = "heartbeat_harmony_admin_access";
const REFRESH_COOKIE = "heartbeat_harmony_admin_refresh";
const LEGACY_ACCESS = "access";
const LEGACY_REFRESH = "refresh";

function getCookie(name: string): string | null {
  if (typeof window === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function setCookie(name: string, value: string) {
  if (typeof window === "undefined") return;
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=2592000; samesite=lax`;
}

function removeCookie(name: string) {
  if (typeof window === "undefined") return;
  document.cookie = `${name}=; path=/; max-age=0; samesite=lax`;
}

export function getAdminAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    localStorage.getItem(ACCESS) ??
    localStorage.getItem(LEGACY_ACCESS) ??
    getCookie(ACCESS_COOKIE)
  );
}

export function getAdminRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    localStorage.getItem(REFRESH) ??
    localStorage.getItem(LEGACY_REFRESH) ??
    getCookie(REFRESH_COOKIE)
  );
}

export function setAdminSession(access: string, refresh?: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS, access);
  localStorage.setItem(LEGACY_ACCESS, access);
  setCookie(ACCESS_COOKIE, access);
  if (refresh) {
    localStorage.setItem(REFRESH, refresh);
    localStorage.setItem(LEGACY_REFRESH, refresh);
    setCookie(REFRESH_COOKIE, refresh);
  }
}

export function clearAdminSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS);
  localStorage.removeItem(REFRESH);
  localStorage.removeItem(LEGACY_ACCESS);
  localStorage.removeItem(LEGACY_REFRESH);
  removeCookie(ACCESS_COOKIE);
  removeCookie(REFRESH_COOKIE);
}

export function updateAdminAccessToken(access: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS, access);
  localStorage.setItem(LEGACY_ACCESS, access);
  setCookie(ACCESS_COOKIE, access);
}