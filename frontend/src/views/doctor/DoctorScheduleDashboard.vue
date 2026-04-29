<script setup>
import ExceptionForm from '@/components/scheduling/ExceptionForm.vue'
import SlotsViewer from '@/components/scheduling/SlotsViewer.vue'
import WeeklyScheduleForm from '@/components/scheduling/WeeklyScheduleForm.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useAuth } from '@/composables/useAuth'
import { useScheduleStore } from '@/stores/scheduling'
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref, watch } from 'vue'
import { toast } from 'vue-sonner'

const store = useScheduleStore()
const { user, activeProfileId, getCurrentUserProfile } = useAuth()
const {
  selectedDoctorId,
  currentDoctorSchedules,
  exceptions,
  availableSlots,
  currentDoctorId,
  loadingCurrentDoctorSchedules,
  loadingExceptions,
  loadingAvailableSlots,
  submitting,
} = storeToRefs(store)

const editingSchedule = ref(null)
const editingException = ref(null)

const doctorName = computed(() => {
  if (!user.value) {
    return 'Doctor'
  }
  return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
})

const belongsToDoctor = (record, doctorId) => {
  if (!doctorId || !record) {
    return false
  }

  const recordDoctorId = record.doctor?.id ?? record.doctor_id ?? record.doctor
  return Number(recordDoctorId) === Number(doctorId)
}

const visibleSchedules = computed(() => {
  return currentDoctorSchedules.value.filter((schedule) =>
    belongsToDoctor(schedule, selectedDoctorId.value),
  )
})

const visibleExceptions = computed(() => {
  return exceptions.value.filter((exception) => belongsToDoctor(exception, selectedDoctorId.value))
})

const formatTime = (value) => (value ? value.slice(0, 5) : 'All day')

const formatDate = (value) => {
  if (!value) {
    return 'No date'
  }
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

const loadDoctorData = async () => {
  if (!selectedDoctorId.value) {
    return
  }

  await Promise.all([
    store.loadCurrentDoctorSchedule(),
    store.loadExceptions({ doctor_id: selectedDoctorId.value }),
  ])
}

const formatWeekday = (value) => {
  if (!value) {
    return 'No day'
  }
  return value.charAt(0).toUpperCase() + value.slice(1)
}

const handleSaveSchedule = async (payload) => {
  try {
    if (editingSchedule.value?.id) {
      await store.editSchedule(editingSchedule.value.id, payload)
      toast.success('Weekly schedule updated successfully.')
    } else {
      await store.createSchedule(payload)
      toast.success('Weekly schedule created successfully.')
    }
    editingSchedule.value = null
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to save weekly schedule.')
  }
}

const handleDeleteSchedule = async (scheduleId) => {
  try {
    await store.removeSchedule(scheduleId, selectedDoctorId.value)
    if (editingSchedule.value?.id === scheduleId) {
      editingSchedule.value = null
    }
    toast.success('Weekly schedule deleted successfully.')
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to delete weekly schedule.')
  }
}

const handleSaveException = async (payload) => {
  try {
    if (editingException.value?.id) {
      await store.editException(editingException.value.id, payload)
      toast.success('Exception updated successfully.')
    } else {
      await store.createException(payload)
      toast.success('Exception created successfully.')
    }
    editingException.value = null
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to save exception.')
  }
}

const handleDeleteException = async (exceptionId) => {
  try {
    await store.removeException(exceptionId, selectedDoctorId.value)
    if (editingException.value?.id === exceptionId) {
      editingException.value = null
    }
    toast.success('Exception deleted successfully.')
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to delete exception.')
  }
}

const handleLoadSlots = async ({ doctor_id, date }) => {
  try {
    await store.loadAvailableSlots(doctor_id, date)
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to load available slots.')
  }
}

watch(
  () => activeProfileId.value,
  async (doctorId) => {
    if (!doctorId) {
      return
    }

    editingSchedule.value = null
    selectedDoctorId.value = doctorId
    await loadDoctorData()
  },
  { immediate: true },
)

onMounted(async () => {
  if (user.value?.primary_role === 'Doctor' && !activeProfileId.value) {
    await getCurrentUserProfile()
  }

  if (!selectedDoctorId.value && activeProfileId.value) {
    selectedDoctorId.value = activeProfileId.value
    await loadDoctorData()
  }
})
</script>

<template>
  <div class="mx-auto flex max-w-6xl flex-col gap-6">
    <Card>
      <CardHeader>
        <CardTitle>Doctor Schedule Dashboard</CardTitle>
        <CardDescription>
          Manage your recurring weekly schedule, one-off availability changes, and bookable slots.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="rounded-lg border border-dashed border-border p-4 text-sm text-muted-foreground">
          <p class="font-medium text-foreground">{{ doctorName }}</p>
          <p>Use the weekly schedule tab to define your standard working hours.</p>
        </div>
      </CardContent>
    </Card>

    <Tabs default-value="weekly-schedule">
      <TabsList>
        <TabsTrigger value="weekly-schedule">Weekly Schedule</TabsTrigger>
        <TabsTrigger value="exceptions">Exceptions</TabsTrigger>
        <TabsTrigger value="slots">Available Slots</TabsTrigger>
      </TabsList>

      <TabsContent value="weekly-schedule" class="grid gap-6 lg:grid-cols-[minmax(0,24rem)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>{{ editingSchedule ? 'Edit Weekly Schedule' : 'Add Weekly Schedule' }}</CardTitle>
            <CardDescription>
              Define your recurring working hours, slot duration, and buffer time.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <WeeklyScheduleForm :doctor-id="selectedDoctorId" :initial-value="editingSchedule" :submitting="submitting"
              @submit="handleSaveSchedule" @cancel="editingSchedule = null" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your Weekly Schedules</CardTitle>
            <CardDescription>Recurring schedule blocks currently assigned to your account.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Day</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Buffer</TableHead>
                  <TableHead>Target Date</TableHead>
                  <TableHead class="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="schedule in visibleSchedules" :key="schedule.id">
                  <TableCell>{{ formatWeekday(schedule.day_of_week) }}</TableCell>
                  <TableCell>{{ `${formatTime(schedule.start_time)} - ${formatTime(schedule.end_time)}` }}</TableCell>
                  <TableCell>{{ schedule.slot_duration_minutes }} min</TableCell>
                  <TableCell>{{ schedule.buffer_time_minutes }} min</TableCell>
                  <TableCell>{{ schedule.target_date ? formatDate(schedule.target_date) : 'Recurring' }}</TableCell>
                  <TableCell class="text-right">
                    <div class="flex justify-end gap-2">
                      <Button size="sm" variant="outline" @click="editingSchedule = schedule">
                        Edit
                      </Button>
                      <Button size="sm" variant="destructive" :disabled="submitting"
                        @click="handleDeleteSchedule(schedule.id)">
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
                <TableEmpty v-if="!loadingCurrentDoctorSchedules && !visibleSchedules.length">
                  No recurring weekly schedules found for your account.
                </TableEmpty>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="exceptions" class="grid gap-6 lg:grid-cols-[minmax(0,24rem)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>{{ editingException ? 'Edit Exception' : 'Add Exception' }}</CardTitle>
            <CardDescription>
              Add a day off or a one-off working day to adjust your schedule.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExceptionForm :doctor-id="selectedDoctorId" :initial-value="editingException" :submitting="submitting"
              @submit="handleSaveException" @cancel="editingException = null" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your Exceptions</CardTitle>
            <CardDescription>Scheduling overrides currently applied to your availability.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead class="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="exception in visibleExceptions" :key="exception.id">
                  <TableCell>{{ formatDate(exception.exception_date) }}</TableCell>
                  <TableCell>
                    <Badge :variant="exception.exception_type === 'off' ? 'outline' : 'secondary'">
                      {{ exception.exception_type === 'off' ? 'Day Off' : 'Working Day' }}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {{ exception.exception_type === 'work'
                      ? `${formatTime(exception.start_time)} - ${formatTime(exception.end_time)}`
                      : 'Unavailable all day' }}
                  </TableCell>
                  <TableCell>{{ exception.reason || 'No reason provided' }}</TableCell>
                  <TableCell class="text-right">
                    <div class="flex justify-end gap-2">
                      <Button size="sm" variant="outline" @click="editingException = exception">
                        Edit
                      </Button>
                      <Button size="sm" variant="destructive" :disabled="submitting"
                        @click="handleDeleteException(exception.id)">
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
                <TableEmpty v-if="!loadingExceptions && !visibleExceptions.length">
                  No exceptions found for your account.
                </TableEmpty>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="slots">
        <SlotsViewer :doctor-id="selectedDoctorId" :slots="availableSlots" :loading="loadingAvailableSlots"
          @load-slots="handleLoadSlots" />
      </TabsContent>
    </Tabs>
  </div>
</template>
