import { defineAsyncComponent } from 'vue';
import { RouteRecordRaw, createRouter, createWebHistory } from 'vue-router';
import BookingView from '@/views/BookingView.vue';
import DashboardView from '@/views/DashboardView/index.vue';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import PostLoginView from '@/views/PostLoginView.vue';
import { useUserStore } from '@/stores/user-store';
import LogoutView from '@/views/LogoutView.vue';

// lazy loaded components
const AvailabilityView = defineAsyncComponent(() => import('@/views/AvailabilityView/index.vue'));
const BookingsView = defineAsyncComponent(() => import('@/views/BookingsView/index.vue'));
const ContactView = defineAsyncComponent(() => import('@/views/ContactView.vue'));
const SettingsView = defineAsyncComponent(() => import('@/views/SettingsView/index.vue'));
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
    path: '/user/:username/:signatureOrSlug?',
    name: 'booking-view',
    component: BookingView,
    meta: {
      isPublic: true,
      maskForMetrics: true,
    },
  },
  {
    path: '/availability',
    name: 'availability',
    component: AvailabilityView,
  },
  {
    path: '/schedule',
    name: 'schedule',
    redirect: { name: 'dashboard' },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
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
    path: '/bookings/:slug?',
    name: 'bookings',
    component: BookingsView,
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
  // Ref: https://router.vuejs.org/guide/advanced/scroll-behavior.html
  scrollBehavior(to) {
    if (to.hash) {
      // This ensures that if hash is provided to router.push it works as expected.
      const noPrefersReducedMotion = window.matchMedia('(prefers-reduced-motion: no-preference)').matches;

      return {
        el: to.hash,
        behavior: noPrefersReducedMotion ? 'smooth' : 'auto',
        top: 64 + 16, // Account for the navigation header height (64px) + 16px for some padding
      }
    }
  }
});

router.beforeEach((to, _from) => {
  const toMeta: ApmtRouteMeta = to?.meta ?? {};

  if (!toMeta?.isPublic && !['setup', 'contact', 'settings', 'logout', 'undefined'].includes(String(to.name))) {
    const user = useUserStore();
    if (user && user.data?.email && !user.data.isSetup) {
      return { ...to, name: 'setup' };
    }
  }
});

export default router;
