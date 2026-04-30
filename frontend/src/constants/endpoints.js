export const API_ENDPOINTS = {
  SCHEDULING: {
    BASE: 'scheduling/',
    SCHEDULES: 'schedules/',
    EXCEPTIONS: 'exceptions/',
    AVAILABLE_SLOTS: 'available/',
  },
  CONSULTATIONS: {
    LIST: '/consultations/consultations/',
    DETAIL: (id) => `/consultations/consultations/${id}/`,
    COMPLETE: (id) => `/consultations/consultations/${id}/complete/`,
    SUMMARY: (id) => `/consultations/consultations/${id}/summary/`,
  },
  PRESCRIPTIONS: {
    LIST: '/consultations/prescriptions/',
    DETAIL: (id) => `/consultations/prescriptions/${id}/`,
  },

  TESTS: {
    LIST: '/consultations/tests/',
    DETAIL: (id) => `/consultations/tests/${id}/`,
  },

  ANALYTICS: {
    SUMMARY: '/analytics/summary/',
    EXPORT_APPOINTMENTS: '/analytics/export/appointments/',
    EXPORT_CONSULTATIONS: '/analytics/export/consultations/',
  },
  ACCOUNTS: {
    BASE: 'accounts/',
    USERS: 'users/',
    ME: 'me/',
    DOCTOR_PROFILE: 'doctor-profile/',
    PATIENT_PROFILE: 'patient-profile/',
  },
  APPOINTMENTS: {
    BASE: 'appointments/',
  },
}
