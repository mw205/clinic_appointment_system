<script setup>
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableEmpty, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { cancelAppointment, getAppointments, normalizeApiError } from '@/services/appointmentService'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { toast } from 'vue-sonner'

const props = defineProps({
  mode: {
    type: String,
    default: 'upcoming',
    validator: (value) => ['upcoming', 'history'].includes(value),
  },
})

const appointments = ref([])
const loading = ref(true)
const actionId = ref(null)
const errorMessage = ref('')

const isHistory = computed(() => props.mode === 'history')
const title = computed(() => isHistory.value ? 'Appointment History' : 'Upcoming Appointments')
const emptyMessage = computed(() => isHistory.value ? 'No past appointments found.' : 'No upcoming appointments found.')

const visibleAppointments = computed(() => {
  const now = Date.now()

  return appointments.value.filter((appointment) => {
    const startsAt = new Date(appointment.start_time).getTime()
    const finalStatus = ['completed', 'cancelled', 'no_show'].includes(appointment.status)

    if (isHistory.value) {
      return finalStatus || startsAt < now
    }

    return !finalStatus && startsAt >= now
  })
})

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

function canCancel(appointment) {
  return ['requested', 'confirmed'].includes(appointment.status)
}

async function loadAppointments() {
  loading.value = true
  errorMessage.value = ''

  try {
    const data = await getAppointments({
      ordering: isHistory.value ? '-start_time' : 'start_time',
      page_size: 50,
    })
    appointments.value = data.results ?? data
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to load appointments.')
  } finally {
    loading.value = false
  }
}

async function handleCancel(appointment) {
  actionId.value = appointment.id
  errorMessage.value = ''

  try {
    await cancelAppointment(appointment.id)
    toast.success('Appointment cancelled.')
    await loadAppointments()
  } catch (error) {
    errorMessage.value = normalizeApiError(error, 'Unable to cancel this appointment.')
  } finally {
    actionId.value = null
  }
}

onMounted(loadAppointments)
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">{{ title }}</h1>
        <p class="text-sm text-gray-500">
          {{ isHistory ? 'Review previous visits and cancelled appointments.' : 'Manage your requested and confirmed appointments.' }}
        </p>
      </div>

      <Button v-if="!isHistory" as-child>
        <RouterLink to="/patient/book">Book Appointment</RouterLink>
      </Button>
    </div>

    <Alert v-if="errorMessage" variant="destructive">
      <AlertTitle>Appointment error</AlertTitle>
      <AlertDescription class="whitespace-pre-line">{{ errorMessage }}</AlertDescription>
    </Alert>

    <div v-if="loading" class="space-y-3">
      <Skeleton v-for="item in 4" :key="item" class="h-16 rounded-lg" />
    </div>

    <Card v-else>
      <CardHeader>
        <CardTitle>{{ title }}</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Doctor</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead class="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="appointment in visibleAppointments" :key="appointment.id">
              <TableCell>{{ appointment.doctor.name }}</TableCell>
              <TableCell>{{ formatDateTime(appointment.start_time) }}</TableCell>
              <TableCell>
                <Badge :variant="statusVariant(appointment.status)">
                  {{ appointment.status }}
                </Badge>
              </TableCell>
              <TableCell>
                <div class="flex justify-end gap-2">
                  <Button as-child size="sm" variant="outline">
                    <RouterLink :to="`/patient/appointments/${appointment.id}`">Details</RouterLink>
                  </Button>
                  <Button
                    v-if="canCancel(appointment)"
                    size="sm"
                    variant="destructive"
                    :disabled="actionId === appointment.id"
                    @click="handleCancel(appointment)"
                  >
                    {{ actionId === appointment.id ? 'Cancelling...' : 'Cancel' }}
                  </Button>
                </div>
              </TableCell>
            </TableRow>
            <TableEmpty v-if="!visibleAppointments.length">
              {{ emptyMessage }}
            </TableEmpty>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
</template>
