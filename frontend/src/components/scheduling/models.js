export const WEEKDAYS = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]

export const EXCEPTION_TYPES = ['off', 'work']

export const defaultWeeklyScheduleForm = {
  doctor_id: null,
  day_of_week: '',
  start_time: '',
  end_time: '',
  slot_duration_minutes: 30,
  buffer_time_minutes: 5,
  target_date: '',
}

export const defaultWorkExceptionForm = {
  doctor_id: null,
  exception_date: '',
  exception_type: 'work',
  start_time: '',
  end_time: '',
  slot_duration_minutes: 30,
  buffer_time_minutes: 5,
  reason: '',
}

export const defaultOffExceptionForm = {
  doctor_id: null,
  exception_date: '',
  exception_type: 'off',
  reason: '',
}

export const defaultSlotsQueryModel = {
  doctor_id: null,
  date: '',
}
