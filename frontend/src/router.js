import { createRouter, createWebHistory } from 'vue-router';
import BookingView from '@/views/BookingView.vue';
import BookingConfirmationView from '@/views/BookingConfirmationView.vue';
import CalendarView from '@/views/CalendarView.vue';
import ScheduleView from '@/views/ScheduleView.vue';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import PostLoginView from '@/views/PostLoginView.vue';

/**
 * Defined routes for Thunderbird Appointment
 * Note: All routes require authentication unless otherwise specified in App.vue::routeIsPublic
 */
const routes = [
  // instant loaded routes
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/post-login/:token',
    name: 'post-login',
    component: PostLoginView,
  },
  {
    path: '/booking/:slug',
    name: 'booking',
    component: BookingView,
  },
  {
    path: '/user/:username/:signature',
    name: 'availability',
    component: BookingView,
  },
  {
    path: '/user/:username/:signature/confirm/:slot/:token/:confirmed',
    name: 'confirmation',
    component: BookingConfirmationView,
  },
  {
    path: '/schedule',
    name: 'schedule',
    component: ScheduleView,
  },
  {
    path: '/calendar',
    redirect: { name: 'calendar' },
  },
  {
    path: '/calendar/:view?/:date?',
    name: 'calendar',
    component: CalendarView,
  },
  // lazy-loaded routes
  {
    path: '/appointments/:view?',
    name: 'appointments',
    component: () => import('@/views/AppointmentsView'),
  },
  {
    path: '/settings/:view?',
    name: 'settings',
    component: () => import('@/views/SettingsView'),
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView'),
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/ContactView'),
  },
  {
    path: '/privacy',
    name: 'privacy',
    beforeEnter: () => { location.href = 'https://www.mozilla.org/en-US/privacy/websites/'; },
  },
  {
    path: '/terms',
    name: 'terms',
    beforeEnter: () => { location.href = 'https://www.mozilla.org/en-US/about/legal/terms/mozilla/'; },
  },
];

// create router object to export
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// set default route parameters
router.beforeEach((to) => {
  if (to.name === 'calendar' && !to.params.view) {
    to.params.view = 'month';
    return to;
  }
  if (to.name === 'appointments' && !to.params.view) {
    to.params.view = 'all';
    return to;
  }
  return null;
});

export default router;
