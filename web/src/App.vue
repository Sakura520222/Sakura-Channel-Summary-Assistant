<template>
  <n-config-provider :theme="isDark ? darkTheme : undefined" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <router-view />
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import {
  darkTheme,
  NConfigProvider,
  NMessageProvider,
  NDialogProvider,
  NNotificationProvider,
  type GlobalThemeOverrides,
} from "naive-ui";

const isDark = ref(false);

const themeOverrides = computed<GlobalThemeOverrides>(() => ({
  common: {
    primaryColor: isDark.value ? "#ff8aa8" : "#e84a7a",
    primaryColorHover: isDark.value ? "#ff9ab5" : "#f05f8c",
    primaryColorPressed: isDark.value ? "#e96e91" : "#c93662",
    infoColor: "#2b8ef0",
    successColor: "#20a779",
    warningColor: "#f2a13a",
    errorColor: "#e25252",
    borderRadius: "8px",
    fontWeightStrong: "650",
  },
  Card: {
    borderRadius: "8px",
  },
  Button: {
    borderRadiusMedium: "8px",
    borderRadiusSmall: "7px",
  },
  DataTable: {
    thFontWeight: "650",
  },
}));

function handleThemeChange(e: Event) {
  isDark.value = (e as CustomEvent).detail;
}

onMounted(() => {
  const savedTheme = localStorage.getItem("sakura_bot_theme");
  isDark.value = savedTheme === "dark";
  document.documentElement.classList.toggle("dark", isDark.value);
  window.addEventListener("theme-change", handleThemeChange);
});

onUnmounted(() => {
  window.removeEventListener("theme-change", handleThemeChange);
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial,
    "Noto Sans", sans-serif;
  color: #253044;
  background:
    linear-gradient(180deg, rgba(232, 74, 122, 0.08) 0%, rgba(43, 142, 240, 0.04) 34%, rgba(246, 248, 252, 0) 72%),
    #f6f8fc;
  transition: background-color 0.3s;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}

html.dark body {
  color: #e8edf7;
  background:
    linear-gradient(180deg, rgba(255, 138, 168, 0.1) 0%, rgba(43, 142, 240, 0.07) 40%, rgba(18, 22, 31, 0) 74%),
    #11151d;
}

html,
body,
#app {
  min-height: 100%;
}

button,
input,
textarea {
  font: inherit;
}

::selection {
  color: #fff;
  background: #e84a7a;
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(122, 132, 154, 0.32);
  border: 3px solid transparent;
  border-radius: 999px;
  background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
  background-color: rgba(122, 132, 154, 0.5);
}

.n-card {
  border-color: rgba(133, 145, 171, 0.18);
  box-shadow: 0 12px 34px rgba(31, 43, 67, 0.06);
}

.n-card > .n-card-header {
  padding-top: 18px;
  padding-bottom: 14px;
}

.n-card > .n-card-header .n-card-header__main {
  font-size: 16px;
  font-weight: 650;
}

.n-data-table {
  --n-td-color-hover: rgba(232, 74, 122, 0.045) !important;
  border-radius: 8px;
}

.n-data-table .n-data-table-th {
  letter-spacing: 0;
}

.n-tag {
  font-weight: 600;
}

.n-input .n-input-wrapper {
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.n-button {
  font-weight: 600;
}

html.dark .n-card {
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.22);
}

.modal-responsive {
  width: min(600px, 90vw) !important;
}

/* 工具类 */
.mt-md { margin-top: 16px; }
.mt-sm { margin-top: 12px; }
.ml-sm { margin-left: 12px; }
.font-icon { font-size: 20px; }
.font-xs { font-size: 12px; }
.w-sm { width: 200px; }
.w-md { width: 300px; }
.cursor-pointer { cursor: pointer; }
</style>
