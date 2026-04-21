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
  ]
})

export default router