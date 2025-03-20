import { defineAsyncComponent, inject } from 'vue';
import { RouteRecordRaw, createRouter, createWebHistory } from 'vue-router';
import BookingView from '@/views/BookingView.vue';
import BookingConfirmationView from '@/views/BookingConfirmationView.vue';
import ScheduleView from '@/views/ScheduleView.vue';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import PostLoginView from '@/views/PostLoginView.vue';
import { useUserStore } from '@/stores/user-store';
import LogoutView from '@/views/LogoutView.vue';

// lazy loaded components
const ContactView = defineAsyncComponent(() => import('@/views/ContactView.vue'));
const AppointmentsView = defineAsyncComponent(() => import('@/views/AppointmentsView.vue'));
const SettingsView = defineAsyncComponent(() => import('@/views/SettingsView.vue'));
const ProfileView = defineAsyncComponent(() => import('@/views/ProfileView.vue'));
const LegalView = defineAsyncComponent(() => import('@/views/LegalView.vue'));
const DocsView = defineAsyncComponent(() => import('@/views/DocsView.vue'));
const WaitingListActionView = defineAsyncComponent(() => import('@/views/WaitingListActionView.vue'));
const SubscriberPanelView = defineAsyncComponent(() => import('@/views/admin/SubscriberPanelView.vue'));
const InviteCodePanelView = defineAsyncComponent(() => import('@/views/admin/InviteCodePanelView.vue'));
const WaitingListPanelView = defineAsyncComponent(() => import('@/views/admin/WaitingListPanelView.vue'));
const FirstTimeUserExperienceView = defineAsyncComponent(() => import('@/views/FirstTimeUserExperienceView.vue'));
const ReportBugView = defineAsyncComponent(() => import('@/views/ReportBugView.vue'));

type ApmtRouteMeta = {
  isPublic?: boolean; // Can the page be accessed without authentication?
  maskForMetrics?: boolean; // Mask url parameters before sending information to metrics
  disableMetrics?: boolean; // Disable all metric capturing for this page. FIXME: Not Impl
};

/**
 * Defined routes for Thunderbird Appointment
 * Note: All routes require authentication unless otherwise specified in App.vue::routeIsPublic
 */
const routes: RouteRecordRaw[] = [
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
    path: '/logout',
    name: 'logout',
    component: LogoutView,
  },
  {
    path: '/waiting-list',
    name: 'join-the-waiting-list',
    component: LoginView,
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/post-login/:token?',
    name: 'post-login',
    component: PostLoginView,
    meta: {
      isPublic: true,
      maskForMetrics: true,
    },
  },
  {
    path: '/user/:username/:signatureOrSlug',
    name: 'availability',
    component: BookingView,
    meta: {
      isPublic: true,
      maskForMetrics: true,
    },
  },
  {
    path: '/user/:username/:signature/confirm/:slot/:token/:confirmed',
    name: 'confirmation',
    component: BookingConfirmationView,
    meta: {
      isPublic: true,
      maskForMetrics: true,
    },
  },
  {
    path: '/schedule',
    name: 'schedule',
    redirect: { name: 'dashboard' },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: ScheduleView,
  },
  {
    // This is just to auto-redirect old links. Can be removed in the future.
    path: '/calendar/:date?',
    redirect: { name: 'dashboard' },
  },
  {
    path: '/appointments/:view?/:slug?',
    name: 'appointments',
    redirect: { name: 'bookings' },
  },
  {
    path: '/bookings/:view?/:slug?',
    name: 'bookings',
    component: AppointmentsView,
    meta: {
      maskForMetrics: true,
    },
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
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/report-bug',
    name: 'report-bug',
    component: ReportBugView,
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
    path: '/docs/using-zoom',
    name: 'using-zoom-docs',
    component: DocsView,
    meta: {
      isPublic: true,
    },
  },
  {
    path: '/setup',
    name: 'setup',
    component: FirstTimeUserExperienceView,
  },
  {
    path: '/waiting-list/:token',
    name: 'waiting-list',
    component: WaitingListActionView,
    meta: {
      isPublic: true,
      maskForMetrics: true,
    },
  },
  // Admin
  {
    path: '/admin/subscribers',
    name: 'admin-subscriber-panel',
    component: SubscriberPanelView,
    meta: {
      // disableMetrics: true,
    },
  },
  {
    path: '/admin/invites',
    name: 'admin-invite-codes-panel',
    component: InviteCodePanelView,
    meta: {
      // disableMetrics: true,
    },
  },
  {
    path: '/admin/waiting-list',
    name: 'admin-waiting-list-panel',
    component: WaitingListPanelView,
    meta: {
      // disableMetrics: true,
    },
  },
];

// create router object to export
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from) => {
  const toMeta: ApmtRouteMeta = to?.meta ?? {};

  if (!toMeta?.isPublic && !['setup', 'contact', 'settings', 'logout', 'undefined'].includes(String(to.name))) {
    const user = useUserStore();
    if (user && user.data?.email && !user.data.isSetup) {
      return { ...to, name: 'setup' };
    }
  }
});

export default router;
