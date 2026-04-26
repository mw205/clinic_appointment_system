import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/doctor/appointments/:appointmentId/consultation',
      name: 'ConsultationForm',
      component: () => import('@/views/doctor/ConsultationFormView.vue'),
      meta: { requiresAuth: true, role: 'doctor' },
    },
    {
      path: '/doctor/schedules',
      name: 'DoctorScheduleDashboard',
      component: () => import('@/views/doctor/DoctorScheduleDashboard.vue'),
    },
    {
      path: 'receptionist/schedules',
      name: 'ReceptionistScheduleDashboard',
      component: () => import('@/views/receptionist/ReceptionistScheduleDashboard.vue'),
    },
    {
      path: '/patient/consultations/:id/summary',
      name: 'ConsultationSummary',
      component: () => import('@/views/patient/ConsultationSummaryView.vue'),
      meta: { requiresAuth: true, role: 'patient' }
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
