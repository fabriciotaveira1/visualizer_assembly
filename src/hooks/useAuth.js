import { useEffect, useState } from "react";

import { clearAuthToken, getAuthToken } from "../services/authService";

export default function useAuth() {
  const [token, setToken] = useState(() => getAuthToken());

  useEffect(() => {
    function syncToken() {
      setToken(getAuthToken());
    }

    window.addEventListener("storage", syncToken);
    window.addEventListener("auth-changed", syncToken);

    return () => {
      window.removeEventListener("storage", syncToken);
      window.removeEventListener("auth-changed", syncToken);
    };
  }, []);

  function logout() {
    clearAuthToken();
    setToken(null);
  }

  return {
    token,
    isAuthenticated: Boolean(token),
    logout,
  };
}
