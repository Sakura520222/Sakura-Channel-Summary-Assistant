import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "Login",
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/",
      component: () => import("../components/AppLayout.vue"),
      children: [
        {
          path: "",
          name: "Dashboard",
          component: () => import("../views/DashboardView.vue"),
        },
        {
          path: "channels",
          name: "Channels",
          component: () => import("../views/ChannelsView.vue"),
        },
        {
          path: "ai-config",
          name: "AIConfig",
          component: () => import("../views/AIConfigView.vue"),
        },
        {
          path: "schedules",
          name: "Schedules",
          component: () => import("../views/SchedulesView.vue"),
        },
        {
          path: "forwarding",
          name: "Forwarding",
          component: () => import("../views/ForwardingView.vue"),
        },
        {
          path: "interaction",
          name: "Interaction",
          component: () => import("../views/InteractionView.vue"),
        },
        {
          path: "stats",
          name: "Stats",
          component: () => import("../views/StatsView.vue"),
        },
        {
          path: "system",
          name: "System",
          component: () => import("../views/SystemView.vue"),
        },
        {
          path: "userbot",
          name: "UserBot",
          component: () => import("../views/UserBotView.vue"),
        },
      ],
    },
  ],
});

export default router;
