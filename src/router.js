import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Result from './views/Result.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/result', component: Result },
  ],
})
