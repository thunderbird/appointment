import { defineAsyncComponent } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import BookingView from '@/views/BookingView.vue';
import BookingConfirmationView from '@/views/BookingConfirmationView.vue';
import CalendarView from '@/views/CalendarView.vue';
import ScheduleView from '@/views/ScheduleView.vue';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import PostLoginView from '@/views/PostLoginView.vue';

// lazy loaded components
const ContactView = defineAsyncComponent(() => import('@/views/ContactView'));
const AppointmentsView = defineAsyncComponent(() => import('@/views/AppointmentsView'));
const SettingsView = defineAsyncComponent(() => import('@/views/SettingsView'));
const ProfileView = defineAsyncComponent(() => import('@/views/ProfileView'));
const LegalView = defineAsyncComponent(() => import('@/views/LegalView'));
const SubscriberPanelView = defineAsyncComponent(() => import('@/views/admin/SubscriberPanelView'));
const InviteCodePanelView = defineAsyncComponent(() => import('@/views/admin/InviteCodePanelView.vue'));

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
  {
    path: '/appointments/:view?/:slug?',
    name: 'appointments',
    component: AppointmentsView,
  },
  {
    path: '/settings/:view?',
    name: 'settings',
    component: SettingsView,
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
  },
  {
    path: '/contact',
    name: 'contact',
    component: ContactView,
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: LegalView,
  },
  {
    path: '/terms',
    name: 'terms',
    component: LegalView,
  },
  // Admin
  {
    path: '/admin/subscribers',
    name: 'admin-subscriber-panel',
    component: SubscriberPanelView,
  },
  {
    path: '/admin/invites',
    name: 'admin-invite-codes-panel',
    component: InviteCodePanelView,
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
