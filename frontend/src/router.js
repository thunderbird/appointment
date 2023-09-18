import { authGuard } from "@auth0/auth0-vue";
import { createRouter, createWebHistory } from "vue-router";
import BookingView from "@/views/BookingView.vue";
import CalendarView from "@/views/CalendarView.vue";
import GeneralAvailabilityView from "@/views/GeneralAvailabilityView.vue";
import HomeView from "@/views/HomeView.vue";

const routes = [
  // instant loaded routes
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/booking/:slug",
    name: "booking",
    component: BookingView,
  },
  {
    path: "/user/:username/:signature",
    name: "availability",
    component: BookingView,
  },
  {
    path: "/availability",
    name: "generalAvailability",
    component: GeneralAvailabilityView,
    beforeEnter: authGuard,
  },
  {
    path: "/calendar",
    redirect: { name: "calendar" },
  },
  {
    path: "/calendar/:view?/:date?",
    name: "calendar",
    component: CalendarView,
    beforeEnter: authGuard,
  },
  // lazy-loaded routes
  {
    path: "/appointments/:view?",
    name: "appointments",
    component: () =>
      import(/* webpackChunkName: "appointments" */ "@/views/AppointmentsView"),
    beforeEnter: authGuard,
  },
  {
    path: "/settings/:view?",
    name: "settings",
    component: () =>
      import(/* webpackChunkName: "settings" */ "@/views/SettingsView"),
    beforeEnter: authGuard,
  },
  {
    path: "/profile",
    name: "profile",
    component: () =>
      import(/* webpackChunkName: "profile" */ "@/views/ProfileView"),
    beforeEnter: authGuard,
  },
];

// create router object to export
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// set default route parameters
router.beforeEach((to) => {
  if (to.name === "calendar" && !to.params.view) {
    to.params.view = "month";
    return to;
  }
  if (to.name === "appointments" && !to.params.view) {
    to.params.view = "all";
    return to;
  }
  return null;
});

export default router;
