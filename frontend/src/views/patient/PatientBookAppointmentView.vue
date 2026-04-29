<script setup>
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { createAppointment, normalizeApiError } from '@/services/appointmentService'
import { getAvailableSlots, getSchedules } from '@/services/schedule_service'
import { CalendarDays } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'

const router = useRouter()

const doctorId = ref(null)
const doctors = ref([])
const selectedDate = ref('')
const selectedSlot = ref(null)
const slots = ref([])
const loadingDoctors = ref(true)
const loadingSlots = ref(false)
const submitting = ref(false)
const errorMessage = ref('')

const canLoadSlots = computed(() => doctorId.value && selectedDate.value)
const canSubmit = computed(() => selectedSlot.value && !submitting.value)
const selectedDoctorValue = computed({
  get() {
    return doctorId.value ? String(doctorId.value) : undefined
  },
  set(value) {
    doctorId.value = value ? Number(value) : null
  },
})

function doctorName(doctor) {
  const user = doctor.user || {}
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ').trim()
  return fullName || user.username || `Doctor #${doctor.id}`
}

function formatSlot(value) {
  return new Intl.DateTimeFormat(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

watch([doctorId, selectedDate], () => {
  selectedSlot.value = null
  slots.value = []
  errorMessage.value = ''
})

async function loadDoctors() {
  loadingDoctors.value = true
  errorMessage.value = ''

  try {
    const data = await getSchedules()
    const schedules = data.results ?? data
    const uniqueDoctors = new Map()

    schedules.forEach((schedule) => {
      if (schedule.doctor?.id) {
        uniqueDoctors.set(schedule.doctor.id, schedule.doctor)
      }
    })

    doctors.value = [...uniqueDoctors.values()]
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to load doctors.')
  } finally {
    loadingDoctors.value = false
  }
}

async function loadSlots() {
  if (!canLoadSlots.value) {
    errorMessage.value = 'Choose a doctor and date first.'
    return
  }

  loadingSlots.value = true
  errorMessage.value = ''

  try {
    slots.value = await getAvailableSlots(doctorId.value, selectedDate.value)
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to load available slots.')
  } finally {
    loadingSlots.value = false
  }
}

async function submitBooking() {
  if (!selectedSlot.value) {
    errorMessage.value = 'Choose an available appointment time.'
    return
  }

  submitting.value = true
  errorMessage.value = ''

  try {
    const appointment = await createAppointment({
      doctor_id: doctorId.value,
      start_time: selectedSlot.value.start_time,
    })

    toast.success('Appointment request sent.')
    router.push(`/patient/appointments/${appointment.id}`)
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to book this appointment.')
  } finally {
    submitting.value = false
  }
}

onMounted(loadDoctors)
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-6">
    <div class="flex flex-col gap-1">
      <h1 class="text-2xl font-semibold text-gray-900">Book Appointment</h1>
      <p class="text-sm text-gray-500">Choose a doctor, pick a date, then select an available time.</p>
    </div>

    <Alert v-if="errorMessage" variant="destructive">
      <AlertTitle>Could not continue</AlertTitle>
      <AlertDescription class="whitespace-pre-line">{{ errorMessage }}</AlertDescription>
    </Alert>

    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <CalendarDays class="h-5 w-5 text-blue-600" />
          Appointment Details
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form class="space-y-5" @submit.prevent="submitBooking">
          <div class="space-y-2">
            <Label>Doctor</Label>
            <Select v-model="selectedDoctorValue" :disabled="loadingDoctors">
              <SelectTrigger class="w-full">
                <SelectValue :placeholder="loadingDoctors ? 'Loading doctors...' : 'Select a doctor'" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="doctor in doctors" :key="doctor.id" :value="String(doctor.id)">
                  {{ doctorName(doctor) }}
                </SelectItem>
              </SelectContent>
            </Select>
            <p v-if="!loadingDoctors && !doctors.length" class="text-sm text-gray-500">
              No doctors with schedules are available.
            </p>
          </div>

          <div class="space-y-2">
            <Label for="appointment-date">Date</Label>
            <Input id="appointment-date" v-model="selectedDate" type="date" />
          </div>

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

          <p v-else class="text-sm text-gray-500">
            Load slots to see available times for the selected date.
          </p>

          <div class="flex justify-end">
            <Button type="submit" :disabled="!canSubmit">
              {{ submitting ? 'Booking...' : 'Book Appointment' }}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
