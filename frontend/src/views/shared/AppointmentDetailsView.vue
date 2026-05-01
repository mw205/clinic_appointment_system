<script setup>
import DateTimeField from '@/components/scheduling/DateTimeField.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import {
  cancelAppointment,
  getApiErrorMessage,
  getAppointment,
  getAvailableSlots,
  rescheduleAppointment,
} from '@/services/appointmentService'
import { useAuth } from '@/composables/useAuth'
import { useConsultationStore } from '@/stores/consultation'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const { user } = useAuth()
const consultationStore = useConsultationStore()

const appointmentId = computed(() => route.params.id)
const currentRole = computed(() => user.value?.primary_role ?? '')

const appointment = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const consultationError = ref('')

const cancelling = ref(false)
const rescheduling = ref(false)
const loadingSlots = ref(false)
const hasLoadedSlots = ref(false)
const slots = ref([])
const selectedSlot = ref(null)

const form = reactive({
  date: '',
  reason: '',
})

const history = computed(() =>
  appointment.value?.reschedule_history
  || appointment.value?.rescheduleHistory
  || []
)

const finalStatuses = ['cancelled', 'completed', 'no_show']
const isCompleted = computed(() => appointment.value?.status === 'completed')
const isReceptionist = computed(() => currentRole.value === 'Receptionist')
const canViewConsultation = computed(() =>
  isCompleted.value && ['Patient', 'Doctor'].includes(currentRole.value)
)

const patientName = computed(() => {
  if (!appointment.value?.patient) {
    return ''
  }

  return appointment.value.patient.name || appointment.value.patient.user?.username || ''
})

const doctorName = computed(() => {
  if (!appointment.value?.doctor) {
    return ''
  }

  return appointment.value.doctor.name || appointment.value.doctor.user?.username || ''
})

const backPath = computed(() => {
  switch (currentRole.value) {
    case 'Doctor':
      return '/doctor/appointments'
    case 'Receptionist':
      return '/receptionist/appointments'
    case 'Patient':
      return '/patient/appointments'
    default:
      return '/'
  }
})

const canShowPatient = computed(() => !isReceptionist.value || patientName.value)
const canShowDoctor = computed(() => !!doctorName.value)

const canCancel = computed(() =>
  currentRole.value === 'Patient'
  && appointment.value?.status
  && !finalStatuses.includes(appointment.value.status)
)

const canReschedule = computed(() =>
  currentRole.value === 'Patient'
  && ['requested', 'confirmed'].includes(appointment.value?.status)
)

const canLoadSlots = computed(() => appointment.value?.doctor?.id && form.date)
const canSubmitReschedule = computed(() =>
  selectedSlot.value && !rescheduling.value && !cancelling.value
)

function formatDateTime(value) {
  if (!value) {
    return 'Not available'
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatSlot(value) {
  if (!value) {
    return 'Not available'
  }

  return new Intl.DateTimeFormat(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

function statusVariant(status) {
  const variants = {
    confirmed: 'default',
    completed: 'secondary',
    cancelled: 'destructive',
    no_show: 'destructive',
    requested: 'outline',
    checked_in: 'secondary',
  }

  return variants[status] ?? 'outline'
}

function syncFormFromAppointment() {
  if (!appointment.value?.start_time) {
    return
  }

  const startsAt = new Date(appointment.value.start_time)
  form.date = startsAt.toISOString().slice(0, 10)
  form.reason = ''
  selectedSlot.value = null
  slots.value = []
  hasLoadedSlots.value = false
}

async function loadConsultation() {
  consultationError.value = ''
  consultationStore.consultation = null

  if (!canViewConsultation.value) {
    return
  }

  try {
    if (currentRole.value === 'Doctor') {
      await consultationStore.loadForAppointment(appointmentId.value)
      return
    }

    if (!appointment.value?.consultation_id) {
      consultationError.value = 'Consultation summary is not available for this appointment.'
      return
    }

    await consultationStore.loadSummary(appointment.value.consultation_id)
  } catch (error) {
    consultationError.value = getApiErrorMessage(error, 'Unable to load consultation details.')
  }
}

async function loadAppointment() {
  loading.value = true
  errorMessage.value = ''

  try {
    appointment.value = await getAppointment(appointmentId.value)
    syncFormFromAppointment()
    await loadConsultation()
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, 'Unable to load appointment details.')
  } finally {
    loading.value = false
  }
}

async function loadSlots() {
  if (!canLoadSlots.value) {
    errorMessage.value = 'Choose a date first.'
    return
  }

  loadingSlots.value = true
  hasLoadedSlots.value = false
  selectedSlot.value = null
  errorMessage.value = ''

  try {
    slots.value = await getAvailableSlots({
      doctor_id: appointment.value.doctor.id,
      date: form.date,
    })
    hasLoadedSlots.value = true
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, 'Unable to load available slots.')
  } finally {
    loadingSlots.value = false
  }
}

async function handleCancel() {
  const confirmed = window.confirm('Cancel this appointment?')
  if (!confirmed) {
    return
  }

  cancelling.value = true
  errorMessage.value = ''

  try {
    appointment.value = await cancelAppointment(appointmentId.value)
    syncFormFromAppointment()
    toast.success('Appointment cancelled.')
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, 'Unable to cancel this appointment.')
  } finally {
    cancelling.value = false
  }
}

async function handleReschedule() {
  if (!selectedSlot.value) {
    errorMessage.value = 'Choose a new appointment slot.'
    return
  }

  rescheduling.value = true
  errorMessage.value = ''

  try {
    appointment.value = await rescheduleAppointment(appointmentId.value, {
      new_start_time: selectedSlot.value.start_time,
      reason: form.reason,
    })
    syncFormFromAppointment()
    toast.success('Appointment rescheduled.')
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, 'Unable to reschedule this appointment.')
  } finally {
    rescheduling.value = false
  }
}

watch(
  () => route.params.id,
  () => {
    loadAppointment()
  }
)

onMounted(loadAppointment)
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-6">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Appointment Details</h1>
        <p class="text-sm text-gray-500">
          Review appointment information
          <span v-if="canViewConsultation">and consultation summary</span>.
        </p>
      </div>

      <Button as-child variant="outline">
        <RouterLink :to="backPath">Back</RouterLink>
      </Button>
    </div>

    <Alert v-if="errorMessage" variant="destructive">
      <AlertTitle>Appointment error</AlertTitle>
      <AlertDescription class="whitespace-pre-line">{{ errorMessage }}</AlertDescription>
    </Alert>

    <div v-if="loading" class="space-y-4">
      <Skeleton class="h-40 rounded-lg" />
      <Skeleton class="h-56 rounded-lg" />
    </div>

    <template v-else-if="appointment">
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center justify-between gap-3">
            <span>Appointment #{{ appointment.id }}</span>
            <Badge :variant="statusVariant(appointment.status)">
              {{ appointment.status }}
            </Badge>
          </CardTitle>
        </CardHeader>

        <CardContent class="grid gap-4 text-sm md:grid-cols-2">
          <div v-if="canShowPatient">
            <p class="text-xs font-medium uppercase text-gray-500">Patient</p>
            <p class="font-medium text-gray-900">{{ patientName || 'Not available' }}</p>
          </div>

          <div v-if="canShowDoctor">
            <p class="text-xs font-medium uppercase text-gray-500">Doctor</p>
            <p class="font-medium text-gray-900">{{ doctorName }}</p>
          </div>

          <div>
            <p class="text-xs font-medium uppercase text-gray-500">Start</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.start_time) }}</p>
          </div>

          <div>
            <p class="text-xs font-medium uppercase text-gray-500">End</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.end_time) }}</p>
          </div>

          <div v-if="appointment.created_at">
            <p class="text-xs font-medium uppercase text-gray-500">Created</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.created_at) }}</p>
          </div>
        </CardContent>
      </Card>

      <Card v-if="canViewConsultation">
        <CardHeader>
          <CardTitle>Consultation</CardTitle>
        </CardHeader>

        <CardContent class="space-y-5">
          <div v-if="consultationStore.loading" class="space-y-4">
            <Skeleton class="h-24 rounded-lg" />
            <Skeleton class="h-24 rounded-lg" />
          </div>

          <Alert v-else-if="consultationError || consultationStore.error" variant="destructive">
            <AlertTitle>Consultation error</AlertTitle>
            <AlertDescription>
              {{ consultationError || consultationStore.error }}
            </AlertDescription>
          </Alert>

          <template v-else-if="consultationStore.consultation">
            <div v-if="consultationStore.consultation.diagnosis" class="space-y-2">
              <Label>Diagnosis</Label>
              <div class="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900">
                {{ consultationStore.consultation.diagnosis }}
              </div>
            </div>

            <div v-if="consultationStore.consultation.notes" class="space-y-2">
              <Label>Clinical Notes</Label>
              <div class="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 whitespace-pre-line">
                {{ consultationStore.consultation.notes }}
              </div>
            </div>

            <div v-if="consultationStore.consultation.prescription_items?.length" class="space-y-2">
              <Label>Prescription</Label>
              <div class="space-y-3">
                <div
                  v-for="item in consultationStore.consultation.prescription_items"
                  :key="item.id ?? `${item.drug}-${item.dose}-${item.duration}`"
                  class="rounded-lg border border-blue-100 bg-blue-50 px-4 py-3"
                >
                  <div class="flex flex-wrap items-center gap-2">
                    <Badge class="bg-blue-100 text-blue-700 border-blue-200">{{ item.drug }}</Badge>
                    <span class="text-sm text-gray-700">{{ item.dose }}</span>
                    <span class="text-sm text-gray-500">· {{ item.duration }}</span>
                  </div>
                  <p v-if="item.instructions" class="mt-2 text-sm text-gray-600">
                    {{ item.instructions }}
                  </p>
                </div>
              </div>
            </div>

            <div v-if="consultationStore.consultation.requested_tests?.length" class="space-y-2">
              <Label>Requested Tests</Label>
              <div class="space-y-3">
                <div
                  v-for="test in consultationStore.consultation.requested_tests"
                  :key="test.id ?? `${test.test_name}-${test.notes || ''}`"
                  class="rounded-lg border border-violet-100 bg-violet-50 px-4 py-3"
                >
                  <div class="flex flex-wrap items-center gap-2">
                    <Badge class="bg-violet-100 text-violet-700 border-violet-200">
                      {{ test.test_name }}
                    </Badge>
                  </div>
                  <p v-if="test.notes" class="mt-2 text-sm text-gray-600">
                    {{ test.notes }}
                  </p>
                </div>
              </div>
            </div>
          </template>

          <p v-else class="text-sm text-gray-500">No consultation record found.</p>
        </CardContent>
      </Card>

      <Card v-if="!isCompleted && (canReschedule || canCancel)">
        <CardHeader>
          <CardTitle>Appointment Actions</CardTitle>
        </CardHeader>

        <CardContent>
          <form v-if="canReschedule" class="space-y-4" @submit.prevent="handleReschedule">
            <DateTimeField
              label="New date"
              :date-value="form.date"
              :show-time="false"
              required
              @update:date-value="form.date = $event; selectedSlot = null; slots = []; hasLoadedSlots = false"
            />

            <Button
              type="button"
              variant="outline"
              :disabled="!canLoadSlots || loadingSlots"
              @click="loadSlots"
            >
              {{ loadingSlots ? 'Loading slots...' : 'Find Available Slots' }}
            </Button>

            <div v-if="loadingSlots" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <Skeleton v-for="item in 6" :key="item" class="h-20 rounded-lg" />
            </div>

            <div v-else-if="slots.length" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <button
                v-for="slot in slots"
                :key="slot.start_time"
                type="button"
                class="rounded-lg border p-4 text-left transition hover:border-blue-500 hover:bg-blue-50"
                :class="selectedSlot?.start_time === slot.start_time ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
                @click="selectedSlot = slot"
              >
                <p class="font-medium text-gray-900">{{ formatSlot(slot.start_time) }}</p>
                <p class="text-sm text-gray-500">Ends {{ formatSlot(slot.end_time) }}</p>
              </button>
            </div>

            <p
              v-else-if="hasLoadedSlots"
              class="rounded-lg border border-dashed border-gray-300 px-4 py-8 text-center text-sm text-gray-500"
            >
              No available slots for this doctor on the selected date.
            </p>

            <div class="space-y-2">
              <Label for="reschedule-reason">Reason</Label>
              <Textarea
                id="reschedule-reason"
                v-model="form.reason"
                placeholder="Optional reason for the change"
              />
            </div>

            <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
              <Button
                v-if="canCancel"
                type="button"
                variant="destructive"
                :disabled="cancelling || rescheduling"
                @click="handleCancel"
              >
                {{ cancelling ? 'Cancelling...' : 'Cancel Appointment' }}
              </Button>

              <Button type="submit" :disabled="!canSubmitReschedule">
                {{ rescheduling ? 'Rescheduling...' : 'Save New Time' }}
              </Button>
            </div>
          </form>

          <div v-else class="flex justify-end">
            <Button
              v-if="canCancel"
              type="button"
              variant="destructive"
              :disabled="cancelling"
              @click="handleCancel"
            >
              {{ cancelling ? 'Cancelling...' : 'Cancel Appointment' }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card v-if="history.length">
        <CardHeader>
          <CardTitle>Reschedule History</CardTitle>
        </CardHeader>

        <CardContent class="space-y-3">
          <div
            v-for="entry in history"
            :key="entry.id"
            class="rounded-lg border border-gray-200 px-4 py-3 text-sm"
          >
            <div class="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
              <p class="font-medium text-gray-900">
                {{ formatDateTime(entry.old_start_time) }} to {{ formatDateTime(entry.new_start_time) }}
              </p>
              <p class="text-gray-500">{{ formatDateTime(entry.timestamp) }}</p>
            </div>
            <p v-if="entry.reason" class="mt-2 text-gray-600">{{ entry.reason }}</p>
            <p v-if="entry.changed_by" class="mt-1 text-xs uppercase text-gray-500">
              Changed by {{ entry.changed_by }}
            </p>
          </div>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
