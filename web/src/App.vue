<template>
  <n-config-provider :theme="isDark ? darkTheme : undefined">
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
import { ref, onMounted, onUnmounted } from "vue";
import { darkTheme, NConfigProvider, NMessageProvider, NDialogProvider, NNotificationProvider } from "naive-ui";

const isDark = ref(false);

function handleThemeChange(e: Event) {
  isDark.value = (e as CustomEvent).detail;
}

onMounted(() => {
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
  background-color: #f5f5f5;
  transition: background-color 0.3s;
}

html.dark body {
  background-color: #1a1a1a;
}

.modal-responsive {
  width: min(600px, 90vw) !important;
}
</style>
