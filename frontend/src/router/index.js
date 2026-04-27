import { getDefaultRouteForRole, useAuth } from '@/composables/useAuth'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '/doctor/appointments/:appointmentId/consultation',
          name: 'ConsultationForm',
          component: () => import('@/views/doctor/ConsultationFormView.vue'),
          meta: { requiresAuth: true, role: 'Doctor' },
        },
        {
          path: '/doctor/schedules',
          name: 'DoctorScheduleDashboard',
          component: () => import('@/views/doctor/DoctorScheduleDashboard.vue'),
        },
        {
          path: '/doctor/queue',
          name: 'DoctorDailyQueue',
          component: () => import('@/views/doctor/DailyQueue.vue')
        },
        {
          path: '/receptionist/schedules',
          name: 'ReceptionistScheduleDashboard',
          component: () => import('@/views/receptionist/ReceptionistScheduleDashboard.vue'),
        },
        {
          path: '/patient/consultations/:id/summary',
          name: 'ConsultationSummary',
          component: () => import('@/views/patient/ConsultationSummaryView.vue'),
          meta: { requiresAuth: true, role: 'patient' },
        },
        {
          path: '/admin/dashboard',
          name: 'AdminDashboard',
          component: () => import('@/views/admin/AdminDashboardView.vue'),
          meta: { requiresAuth: true, role: 'admin' },
        },
        {
          path: '',
          name: 'home-redirect',
          redirect: () => {
            const { user } = useAuth()
            console.log(user)

            return getDefaultRouteForRole(user.value.userObject.primary_role)
          },
        },
      ],
    },
  ],
})

export default router
