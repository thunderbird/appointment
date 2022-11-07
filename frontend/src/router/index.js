import { createRouter, createWebHistory } from 'vue-router'
import CalendarView from '@/views/CalendarView.vue'

const routes = [
  { path: '/', redirect: { name: "calendar" } },
  { path: '/calendar', redirect: { name: "calendar" } },
  {
    path: '/calendar/:view?/:date?',
    name: 'calendar',
    component: CalendarView
  },
  // lazy-loaded routes
  {
    path: '/events/:view?',
    name: 'events',
    component: () => import(/* webpackChunkName: "events" */ '@/views/EventsView.vue')
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
  if(to.name === 'events' && !to.params.view){
    to.params.view = 'all';
    return to;
  }
})

export default router
