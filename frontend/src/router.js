import BookingView from '@/views/BookingView';
import CalendarView from '@/views/CalendarView';
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: { name: "calendar" } },
  { path: '/calendar', redirect: { name: "calendar" } },
  {
    path: '/booking/:slug',
    name: 'booking',
    component: BookingView
  },
  {
    path: '/calendar/:view?/:date?',
    name: 'calendar',
    component: CalendarView
  },
  // lazy-loaded routes
  {
    path: '/appointments/:view?',
    name: 'appointments',
    component: () => import(/* webpackChunkName: "appointments" */ '@/views/AppointmentsView')
  },
  {
    path: '/settings/:view?',
    name: 'settings',
    component: () => import(/* webpackChunkName: "settings" */ '@/views/SettingsView')
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import(/* webpackChunkName: "profile" */ '@/views/ProfileView')
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach(to => {
  if (to.name === 'calendar' && !to.params.view) {
    to.params.view = 'month';
    return to;
  }
  if (to.name === 'appointments' && !to.params.view) {
    to.params.view = 'all';
    return to;
  }
});

export default router;
