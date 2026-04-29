import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器 - 添加 Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("sakura_bot_token");
  if (token) {
    config.params = { ...config.params, token };
  }
  return config;
});

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("sakura_bot_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default apiClient;
