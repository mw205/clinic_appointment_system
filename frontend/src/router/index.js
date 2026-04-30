import { getDefaultRouteForRole, useAuth } from '@/composables/useAuth'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresAuth: false, guestOnly: true },
    },
    {
      path: '/signup',
      name: 'Signup',
      component: () => import('@/views/auth/SignupView.vue'),
      meta: { requiresAuth: false, guestOnly: true },
    },
    {
      path: '/verify-email',
      name: 'VerifyEmail',
      component: () => import('@/views/auth/VerifyEmailView.vue'),
      meta: { requiresAuth: false, guestOnly: true },
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('@/views/auth/ForgotPasswordView.vue'),
      meta: { requiresAuth: false, guestOnly: true },
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: () => import('@/views/auth/ResetPasswordView.vue'),
      meta: { requiresAuth: false, guestOnly: true },
    },
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
          path: '/receptionist/queue',
          name: 'ReceptionistQueueManagement',
          component: () => import('@/views/receptionist/DailyQueue.vue'),
        },
        {
          path: '/patient/dashboard',
          name: 'PatientDashboard',
          component: () => import('@/views/patient/PatientDashboardView.vue'),
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/patient/appointments',
          name: 'PatientAppointments',
          component: () => import('@/views/patient/PatientAppointmentsView.vue'),
          props: { mode: 'upcoming' },
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/patient/book',
          name: 'PatientBookAppointment',
          component: () => import('@/views/patient/PatientBookAppointmentView.vue'),
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/patient/history',
          name: 'PatientAppointmentHistory',
          component: () => import('@/views/patient/PatientAppointmentsView.vue'),
          props: { mode: 'history' },
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/patient/appointments/:id',
          name: 'PatientAppointmentDetails',
          component: () => import('@/views/patient/PatientAppointmentDetailsView.vue'),
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/appointments',
          name: 'Appointments',
          component: () => import('@/views/patient/PatientAppointmentsView.vue'),
          props: { mode: 'upcoming' },
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/appointments/upcoming',
          name: 'AppointmentsUpcoming',
          component: () => import('@/views/patient/PatientAppointmentsView.vue'),
          props: { mode: 'upcoming' },
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/appointments/history',
          name: 'AppointmentsHistory',
          component: () => import('@/views/patient/PatientAppointmentsView.vue'),
          props: { mode: 'history' },
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/appointments/book',
          name: 'AppointmentsBook',
          component: () => import('@/views/patient/PatientBookAppointmentView.vue'),
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/appointments/:id',
          name: 'AppointmentDetails',
          component: () => import('@/views/patient/PatientAppointmentDetailsView.vue'),
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/patient/consultations/:id/summary',
          name: 'ConsultationSummary',
          component: () => import('@/views/patient/ConsultationSummaryView.vue'),
          meta: { requiresAuth: true, role: 'Patient' },
        },
        {
          path: '/admin/dashboard',
          name: 'AdminDashboard',
          component: () => import('@/views/admin/AdminDashboardView.vue'),
          meta: { requiresAuth: true, role: 'admin' },
        },
        {
          path: '/admin/users',
          name: 'AdminUsersList',
          component: () => import('@/views/admin/UsersListView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/admin/users/:id',
          name: 'AdminUserEdit',
          component: () => import('@/views/admin/UserEditView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/settings',
          component: () => import('@/views/settings/SettingsLayout.vue'),
          meta: { requiresAuth: true },
          children: [
            {
              path: '',
              redirect: '/settings/account'
            },
            {
              path: 'account',
              name: 'AccountSettings',
              component: () => import('@/views/settings/AccountSettingsView.vue')
            },
            {
              path: 'profile',
              name: 'ProfileSettings',
              component: () => import('@/views/settings/ProfileSettingsView.vue')
            }
          ]
        },
        {
          path: '',
          name: 'home-redirect',
          redirect: () => {
            const { user } = useAuth()
            if (!user.value) {
              return '/login'
            }
            return getDefaultRouteForRole(user.value.primary_role)
          },
        },
      ],
    },
  ],
})

router.beforeEach(async (to, from) => {
  const { user, authReady, checkSession } = useAuth()

  if (!authReady.value) {
    await checkSession()
  }

  const isAuthenticated = !!user.value

  if (to.meta.requiresAuth && !isAuthenticated) {
    return '/login'
  } else if (to.meta.guestOnly && isAuthenticated) {
    return '/'
  }
})

export default router
