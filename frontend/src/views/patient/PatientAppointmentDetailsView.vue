<script setup>
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import {
  cancelAppointment,
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
const errorMessage = ref('')
const form = reactive({
  date: '',
  time: '',
  reason: '',
})

const history = computed(() =>
  appointment.value?.reschedule_history
  || appointment.value?.rescheduleHistory
  || []
)

const finalStatuses = ['cancelled', 'completed', 'no_show']

const canCancel = computed(() =>
  appointment.value?.status && !finalStatuses.includes(appointment.value.status)
)

const canReschedule = computed(() =>
  ['requested', 'confirmed'].includes(appointment.value?.status)
)

function formatDateTime(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
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
  form.time = startsAt.toTimeString().slice(0, 5)
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
  if (!form.date || !form.time) {
    errorMessage.value = 'Choose a new date and time.'
    return
  }

  rescheduling.value = true
  errorMessage.value = ''

  try {
    appointment.value = await rescheduleAppointment(appointmentId.value, {
      new_start_time: new Date(`${form.date}T${form.time}`).toISOString(),
      reason: form.reason,
    })
    syncFormFromAppointment()
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
            <p class="text-xs font-medium uppercase text-gray-500">Start</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.start_time) }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">End</p>
            <p class="font-medium text-gray-900">{{ formatDateTime(appointment.end_time) }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">Doctor</p>
            <p class="font-medium text-gray-900">{{ appointment.doctor.name }}</p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase text-gray-500">Appointment ID</p>
            <p class="font-medium text-gray-900">#{{ appointment.id }}</p>
          </div>
        </CardContent>
      </Card>

      <Card v-if="canReschedule">
        <CardHeader>
          <CardTitle>Reschedule Appointment</CardTitle>
        </CardHeader>
        <CardContent>
          <form class="space-y-4" @submit.prevent="handleReschedule">
            <div class="grid gap-4 md:grid-cols-2">
              <div class="space-y-2">
                <Label for="reschedule-date">New date</Label>
                <Input id="reschedule-date" v-model="form.date" type="date" />
              </div>
              <div class="space-y-2">
                <Label for="reschedule-time">New time</Label>
                <Input id="reschedule-time" v-model="form.time" type="time" />
              </div>
            </div>

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
              <Button type="submit" :disabled="rescheduling || cancelling">
                {{ rescheduling ? 'Rescheduling...' : 'Save New Time' }}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reschedule History</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="history.length" class="space-y-3">
            <div v-for="entry in history" :key="entry.id || entry.timestamp" class="rounded-lg border p-4">
              <p class="font-medium text-gray-900">
                {{ formatDateTime(entry.old_start_time) }} to {{ formatDateTime(entry.new_start_time) }}
              </p>
              <p class="mt-1 text-sm text-gray-500">
                {{ entry.reason || 'No reason provided.' }}
              </p>
            </div>
          </div>
          <p v-else class="text-sm text-gray-500">
            No reschedule history recorded for this appointment.
          </p>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
