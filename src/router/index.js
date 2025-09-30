import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Settings from '../pages/Settings.vue'
import TopBar from '../TopBar/TopBar.vue'
import Main from '../Main.vue'
import SchedulePage from '../pages/SchedulePage.vue'

const routes = [
  {
    path: '/',
    component: Main,
    children: [
      { path: '', name: 'Home', component: Home },
      { path: '/schedule', name: 'SchedulePage', component: SchedulePage },
      { path: '/settings', name: 'Settings', component: Settings }
    ]
  },
  { path: '/topbar', name: 'TopBar', component: TopBar }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
