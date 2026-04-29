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
  getAvailableSlots,
  getAppointment,
  normalizeApiError,
  rescheduleAppointment,
} from '@/services/appointmentService'
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { toast } from 'vue-sonner'

const route = useRoute()
const appointmentId = computed(() => route.params.id)

const appointment = ref(null)
const loading = ref(true)
const cancelling = ref(false)
const rescheduling = ref(false)
const loadingSlots = ref(false)
const hasLoadedSlots = ref(false)
const slots = ref([])
const selectedSlot = ref(null)
const errorMessage = ref('')
const form = reactive({
  date: '',
  reason: '',
})

const history = computed(() =>
  appointment.value?.reschedule_history
  || appointment.value?.rescheduleHistory
  || []
)

const patientName = computed(() => {
  if (!appointment.value?.patient) {
    return ''
  }

  return appointment.value.patient.name || appointment.value.patient.user?.username || ''
})

const finalStatuses = ['cancelled', 'completed', 'no_show']

const canCancel = computed(() =>
  appointment.value?.status && !finalStatuses.includes(appointment.value.status)
)

const canReschedule = computed(() =>
  ['requested', 'confirmed'].includes(appointment.value?.status)
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
  selectedSlot.value = null
  slots.value = []
  hasLoadedSlots.value = false
}

async function loadAppointment() {
  loading.value = true
  errorMessage.value = ''

  try {
    appointment.value = await getAppointment(appointmentId.value)
    syncFormFromAppointment()
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to load appointment details.')
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
    errorMessage.value = normalizeApiError(error, 'Unable to load available slots.')
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
    toast.success('Appointment cancelled.')
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to cancel this appointment.')
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
    form.reason = ''
    toast.success('Appointment rescheduled.')
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to reschedule this appointment.')
  } finally {
    rescheduling.value = false
  }
}

onMounted(loadAppointment)
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-6">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Appointment Details</h1>
        <p class="text-sm text-gray-500">Review appointment status and requested changes.</p>
      </div>

      <Button as-child variant="outline">
        <RouterLink to="/patient/appointments">Back to appointments</RouterLink>
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
            <span>Visit with {{ appointment.doctor.name }}</span>
            <Badge :variant="statusVariant(appointment.status)">
              {{ appointment.status }}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent class="grid gap-4 text-sm md:grid-cols-2">
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">Appointment ID</p>
            <p class="font-medium text-gray-900">#{{ appointment.id }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">Doctor</p>
            <p class="font-medium text-gray-900">{{ appointment.doctor.name }}</p>
          </div>
          <div v-if="patientName">
            <p class="text-xs font-medium uppercase text-gray-500">Patient</p>
            <p class="font-medium text-gray-900">{{ patientName }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">Start</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.start_time) }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">End</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.end_time) }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">Created</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.created_at) }}</p>
          </div>
        </CardContent>
      </Card>

      <Card v-if="canReschedule">
        <CardHeader>
          <CardTitle>Reschedule Appointment</CardTitle>
        </CardHeader>
        <CardContent>
          <form class="space-y-4" @submit.prevent="handleReschedule">
            <DateTimeField
              label="New date"
              :date-value="form.date"
              :show-time="false"
              required
              @update:date-value="form.date = $event; selectedSlot = null; slots = []; hasLoadedSlots = false"
            />

            <Button type="button" variant="outline" :disabled="!canLoadSlots || loadingSlots" @click="loadSlots">
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

            <p v-else-if="hasLoadedSlots" class="rounded-lg border border-dashed border-gray-300 px-4 py-8 text-center text-sm text-gray-500">
              No available slots for this doctor on the selected date.
            </p>

            <div class="space-y-2">
              <Label for="reschedule-reason">Reason</Label>
              <Textarea id="reschedule-reason" v-model="form.reason" placeholder="Optional reason for the change" />
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
        </CardContent>
      </Card>

      <Card v-if="history.length">
        <CardHeader>
          <CardTitle>Reschedule History</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4 border-l border-gray-200 pl-4">
            <div v-for="entry in history" :key="entry.id || entry.timestamp" class="relative">
              <span class="absolute -left-[21px] top-1 h-3 w-3 rounded-full bg-blue-600" />
              <p class="font-medium text-gray-900">
                {{ formatDateTime(entry.old_start_time) }} -> {{ formatDateTime(entry.new_start_time) }}
              </p>
              <p v-if="entry.changed_by" class="mt-1 text-sm text-gray-600">
                Changed by {{ entry.changed_by }}
              </p>
              <p v-if="entry.reason" class="mt-1 text-sm text-gray-600">
                Reason: {{ entry.reason }}
              </p>
              <p v-if="entry.timestamp" class="mt-1 text-xs text-gray-500">
                {{ formatDateTime(entry.timestamp) }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </template>

    <Card v-else>
      <CardContent class="px-6 py-10 text-center text-sm text-gray-500">
        Appointment not found.
      </CardContent>
    </Card>
  </div>
</template>
