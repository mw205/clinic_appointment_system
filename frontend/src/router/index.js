import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/doctor/appointments/:appointmentId/consultation',
      name: 'ConsultationForm',
      component: () => import('@/views/doctor/ConsultationFormView.vue'),
      meta: { requiresAuth: true, role: 'doctor' }
    },
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: () => import('@views/admin/AdminDashBoard.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    }
  ]
})

export default router