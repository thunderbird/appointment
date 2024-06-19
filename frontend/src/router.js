import { defineAsyncComponent } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import BookingView from '@/views/BookingView.vue';
import BookingConfirmationView from '@/views/BookingConfirmationView.vue';
import CalendarView from '@/views/CalendarView.vue';
import ScheduleView from '@/views/ScheduleView.vue';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import PostLoginView from '@/views/PostLoginView.vue';
import { useUserStore } from '@/stores/user-store';

// lazy loaded components
const ContactView = defineAsyncComponent(() => import('@/views/ContactView'));
const AppointmentsView = defineAsyncComponent(() => import('@/views/AppointmentsView'));
const SettingsView = defineAsyncComponent(() => import('@/views/SettingsView'));
const ProfileView = defineAsyncComponent(() => import('@/views/ProfileView'));
const LegalView = defineAsyncComponent(() => import('@/views/LegalView'));
const SubscriberPanelView = defineAsyncComponent(() => import('@/views/admin/SubscriberPanelView'));
const InviteCodePanelView = defineAsyncComponent(() => import('@/views/admin/InviteCodePanelView.vue'));
const FirstTimeUserExperienceView = defineAsyncComponent(() => import('@/views/FirstTimeUserExperienceView.vue'));

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
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/post-login/:token',
    name: 'post-login',
    component: PostLoginView,
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/user/:username/:signatureOrSlug',
    name: 'availability',
    component: BookingView,
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/user/:username/:signature/confirm/:slot/:token/:confirmed',
    name: 'confirmation',
    component: BookingConfirmationView,
    meta: {
      isPublic: true,
    },
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
    path: '/calendar/:date?',
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
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/terms',
    name: 'terms',
    component: LegalView,
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/setup',
    name: 'setup',
    component: FirstTimeUserExperienceView,
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

router.beforeEach((to, from) => {
  if (!to.meta?.isPublic && !['setup', 'contact', undefined].includes(to.name)) {
    const user = useUserStore();
    if (user && user.data?.email && !user.data.setup) {
      console.log('To -> ', to);
      return { ...to, name: 'setup' };
    }
  }
});

export default router;
