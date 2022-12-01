import { createRouter, createWebHistory } from 'vue-router'
import CalendarView from '@/views/CalendarView.vue'
import BookingView from '@/views/BookingView.vue'

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
    component: () => import(/* webpackChunkName: "appointments" */ '@/views/AppointmentsView.vue')
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import(/* webpackChunkName: "settings" */ '@/views/SettingsView.vue')
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import(/* webpackChunkName: "profile" */ '@/views/ProfileView.vue')
  },
  {
    path: '/test',
    name: 'test',
    component: () => import(/* webpackChunkName: "about" */ '@/views/TestView.vue')
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach(to => {
  if(to.name === 'calendar' && !to.params.view){
    to.params.view = 'month';
    return to;
  }
  if(to.name === 'appointments' && !to.params.view){
    to.params.view = 'all';
    return to;
  }
})

export default router
