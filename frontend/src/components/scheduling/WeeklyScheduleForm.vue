<script setup>
import { computed, reactive, watch } from 'vue'
import Button from '@/components/ui/button/Button.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { WEEKDAYS, defaultWeeklyScheduleForm } from '@/components/scheduling/models'

const props = defineProps({
  doctorId: {
    type: Number,
    default: null,
  },
  initialValue: {
    type: Object,
    default: null,
  },
  submitting: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['submit', 'cancel'])

const form = reactive({ ...defaultWeeklyScheduleForm })
const errors = reactive({
  day_of_week: '',
  start_time: '',
  end_time: '',
  slot_duration_minutes: '',
  buffer_time_minutes: '',
})

const isEditMode = computed(() => !!props.initialValue?.id)

const populateForm = (value) => {
  Object.assign(form, defaultWeeklyScheduleForm, {
    ...value,
    doctor_id: props.doctorId ?? value?.doctor_id ?? null,
    start_time: value?.start_time ? value.start_time.slice(0, 5) : '',
    end_time: value?.end_time ? value.end_time.slice(0, 5) : '',
    target_date: value?.target_date ?? '',
  })
}

const resetErrors = () => {
  errors.day_of_week = ''
  errors.start_time = ''
  errors.end_time = ''
  errors.slot_duration_minutes = ''
  errors.buffer_time_minutes = ''
}

watch(
  () => [props.initialValue, props.doctorId],
  ([initialValue]) => {
    populateForm(initialValue)
  },
  { immediate: true },
)

const toApiTime = (value) => {
  if (!value) {
    return ''
  }
  return value.length === 5 ? `${value}:00` : value
}

const validate = () => {
  resetErrors()

  if (!form.day_of_week && !form.target_date) {
    errors.day_of_week = 'Choose a weekday or provide a target date.'
  }

  if (!form.start_time) {
    errors.start_time = 'Start time is required.'
  }

  if (!form.end_time) {
    errors.end_time = 'End time is required.'
  }

  if (form.start_time && form.end_time && form.start_time >= form.end_time) {
    errors.end_time = 'End time must be after start time.'
  }

  if (![15, 30].includes(Number(form.slot_duration_minutes))) {
    errors.slot_duration_minutes = 'Slot duration must be 15 or 30 minutes.'
  }

  if (Number(form.buffer_time_minutes) < 0) {
    errors.buffer_time_minutes = 'Buffer time cannot be negative.'
  }

  return Object.values(errors).every((value) => !value)
}

const handleSubmit = () => {
  if (!props.doctorId || !validate()) {
    return
  }

  const payload = {
    doctor_id: props.doctorId,
    day_of_week: form.day_of_week,
    start_time: toApiTime(form.start_time),
    end_time: toApiTime(form.end_time),
    slot_duration_minutes: Number(form.slot_duration_minutes),
    buffer_time_minutes: Number(form.buffer_time_minutes),
  }

  if (form.target_date) {
    payload.target_date = form.target_date
  }

  emit('submit', payload)
}

const handleCancel = () => {
  populateForm(null)
  resetErrors()
  emit('cancel')
}

const weekdayLabel = (day) => day.charAt(0).toUpperCase() + day.slice(1)
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <div class="grid gap-4 md:grid-cols-2">
      <div class="space-y-2">
        <Label>Weekday</Label>
        <Select v-model="form.day_of_week">
          <SelectTrigger class="w-full">
            <SelectValue placeholder="Select day" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="day in WEEKDAYS" :key="day" :value="day">
              {{ weekdayLabel(day) }}
            </SelectItem>
          </SelectContent>
        </Select>
        <p v-if="errors.day_of_week" class="text-sm text-destructive">
          {{ errors.day_of_week }}
        </p>
      </div>

      <div class="space-y-2">
        <Label>Target Date</Label>
        <Input v-model="form.target_date" type="date" />
        <p class="text-sm text-muted-foreground">
          Optional. Leave empty for a recurring weekly schedule.
        </p>
      </div>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="space-y-2">
        <Label>Start Time</Label>
        <Input v-model="form.start_time" type="time" />
        <p v-if="errors.start_time" class="text-sm text-destructive">
          {{ errors.start_time }}
        </p>
      </div>

      <div class="space-y-2">
        <Label>End Time</Label>
        <Input v-model="form.end_time" type="time" />
        <p v-if="errors.end_time" class="text-sm text-destructive">
          {{ errors.end_time }}
        </p>
      </div>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="space-y-2">
        <Label>Slot Duration (minutes)</Label>
        <Select v-model="form.slot_duration_minutes">
          <SelectTrigger class="w-full">
            <SelectValue placeholder="Select duration" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem :value="15">15 minutes</SelectItem>
            <SelectItem :value="30">30 minutes</SelectItem>
          </SelectContent>
        </Select>
        <p v-if="errors.slot_duration_minutes" class="text-sm text-destructive">
          {{ errors.slot_duration_minutes }}
        </p>
      </div>

      <div class="space-y-2">
        <Label>Buffer Time (minutes)</Label>
        <Input v-model="form.buffer_time_minutes" type="number" min="0" step="5" />
        <p v-if="errors.buffer_time_minutes" class="text-sm text-destructive">
          {{ errors.buffer_time_minutes }}
        </p>
      </div>
    </div>

    <div class="flex items-center justify-end gap-2">
      <Button
        v-if="isEditMode"
        type="button"
        variant="outline"
        :disabled="submitting"
        @click="handleCancel"
      >
        Cancel
      </Button>
      <Button type="submit" :disabled="submitting || !doctorId">
        {{ submitting ? 'Saving...' : isEditMode ? 'Update Schedule' : 'Add Schedule' }}
      </Button>
    </div>
  </form>
</template>
