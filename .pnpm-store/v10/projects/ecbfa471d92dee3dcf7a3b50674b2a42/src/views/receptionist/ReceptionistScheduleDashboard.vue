<script setup>
import DoctorSelector from '@/components/scheduling/DoctorSelector.vue'
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
import { useScheduleStore } from '@/stores/scheduling'
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref, watch } from 'vue'
import { toast } from 'vue-sonner'

const store = useScheduleStore()
const {
  selectedDoctorProfileId,
  schedules,
  exceptions,
  availableSlots,
  loadingSchedules,
  loadingExceptions,
  loadingAvailableSlots,
  submitting,
} = storeToRefs(store)

const editingSchedule = ref(null)
const editingException = ref(null)

const selectedDoctor = computed(() => {
  return store.doctors.find((doctor) => doctor.profile_id === selectedDoctorProfileId.value) ?? null
})

const belongsToDoctor = (record, doctorId) => {
  if (!doctorId || !record) {
    return false
  }

  const recordDoctorId = record.doctor?.id ?? record.doctor_id ?? record.doctor ?? record.profile_id
  return Number(recordDoctorId) === Number(doctorId)
}

const visibleSchedules = computed(() => {
  return schedules.value.filter((schedule) => belongsToDoctor(schedule, selectedDoctorProfileId.value))
})

const visibleExceptions = computed(() => {
  return exceptions.value.filter((exception) => belongsToDoctor(exception, selectedDoctorProfileId.value))
})

const exceptionTypeLabel = (type) => (type === 'off' ? 'Day Off' : 'Working Day')

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

const loadDoctorData = async (doctorId) => {
  if (!doctorId) {
    return
  }
  console.log(doctorId);

  await Promise.all([
    store.loadSchedules({ doctor: doctorId }),
    store.loadExceptions({ doctor_id: doctorId }),
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

const handleEditException = (exception) => {
  editingException.value = exception
}

const handleCancelEdit = () => {
  editingException.value = null
}

const handleDeleteSchedule = async (scheduleId) => {
  try {
    await store.removeSchedule(scheduleId, selectedDoctorProfileId.value)
    if (editingSchedule.value?.id === scheduleId) {
      editingSchedule.value = null
    }
    toast.success('Weekly schedule deleted successfully.')
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to delete weekly schedule.')
  }
}

const handleDeleteException = async (exceptionId) => {
  try {
    await store.removeException(exceptionId)
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

watch(selectedDoctorProfileId, async (doctorId) => {
  editingSchedule.value = null
  editingException.value = null
  availableSlots.value = []
  if (doctorId) {
    await loadDoctorData(doctorId)
  } else {
    schedules.value = []
    exceptions.value = []
  }
})

onMounted(async () => {
  try {
    await store.loadDoctors()
    if (store.doctors.length && !selectedDoctorProfileId.value) {
      selectedDoctorProfileId.value = store.doctors[0].profile_id
    }
  } catch (error) {
    toast.error(error.response?.data?.detail || 'Failed to load doctors.')
  }
})
</script>

<template>
  <div class="mx-auto flex max-w-6xl flex-col gap-6">
    <Card>
      <CardHeader>
        <CardTitle>Receptionist Schedule Management</CardTitle>
        <CardDescription>
          Choose a doctor, manage one-off exceptions, and preview bookable slots.
        </CardDescription>
      </CardHeader>
      <CardContent class="grid gap-4 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <DoctorSelector v-model="selectedDoctorProfileId" />
        <div class="rounded-lg border border-dashed border-border p-4 text-sm text-muted-foreground">
          <p class="font-medium text-foreground">
            {{ selectedDoctor ? `${selectedDoctor.first_name} ${selectedDoctor.last_name}`.trim() ||
              selectedDoctor.username : 'No doctor selected' }}
          </p>
          <p>Manage recurring weekly schedules, exceptions, and available slots for the selected doctor.</p>
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
              Define recurring working hours, slot duration, and buffer time for the selected doctor.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <WeeklyScheduleForm :doctor-id="selectedDoctorProfileId" :initial-value="editingSchedule" :submitting="submitting"
              @submit="handleSaveSchedule" @cancel="editingSchedule = null" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Doctor Weekly Schedules</CardTitle>
            <CardDescription>
              {{ selectedDoctorProfileId ? `Recurring weekly schedule blocks for the selected doctor.` : `Select a doctor to
              view weekly schedules.` }}
            </CardDescription>
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
                <TableEmpty v-if="!loadingSchedules && !visibleSchedules.length">
                  No weekly schedules found for this doctor.
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
              Create a day off or one-off working day for the selected doctor.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ExceptionForm :doctor-id="selectedDoctorProfileId" :initial-value="editingException" :submitting="submitting"
              @submit="handleSaveException" @cancel="handleCancelEdit" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Doctor Exceptions</CardTitle>
            <CardDescription>
              {{ selectedDoctorProfileId ? `Existing scheduling overrides for the selected doctor.` : `Select a doctor to view
              exceptions.` }}
            </CardDescription>
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
                      {{ exceptionTypeLabel(exception.exception_type) }}
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
                      <Button size="sm" variant="outline" @click="handleEditException(exception)">
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
                  No exceptions found for this doctor.
                </TableEmpty>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="slots">
        <SlotsViewer :doctor-id="selectedDoctorProfileId" :slots="availableSlots" :loading="loadingAvailableSlots"
          @load-slots="handleLoadSlots" />
      </TabsContent>
    </Tabs>
  </div>
</template>
