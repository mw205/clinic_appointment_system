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
import Textarea from '@/components/ui/textarea/Textarea.vue'
import DateTimeField from '@/components/scheduling/DateTimeField.vue'
import {
  EXCEPTION_TYPES,
  defaultOffExceptionForm,
  defaultWorkExceptionForm,
} from '@/components/scheduling/models'

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

const makeDefaultForm = (exceptionType = 'off') => ({
  ...(exceptionType === 'work' ? defaultWorkExceptionForm : defaultOffExceptionForm),
})

const form = reactive(makeDefaultForm())
const errors = reactive({
  exception_date: '',
  start_time: '',
  end_time: '',
  slot_duration_minutes: '',
  buffer_time_minutes: '',
})

const isEditMode = computed(() => !!props.initialValue?.id)
const isWorkException = computed(() => form.exception_type === 'work')

const resetErrors = () => {
  errors.exception_date = ''
  errors.start_time = ''
  errors.end_time = ''
  errors.slot_duration_minutes = ''
  errors.buffer_time_minutes = ''
}

const populateForm = (value) => {
  const base = makeDefaultForm(value?.exception_type ?? 'off')
  Object.assign(form, base, {
    ...value,
    doctor_id: props.doctorId ?? value?.doctor_id ?? null,
    exception_date: value?.exception_date ?? '',
    start_time: value?.start_time ? value.start_time.slice(0, 5) : '',
    end_time: value?.end_time ? value.end_time.slice(0, 5) : '',
    reason: value?.reason ?? '',
  })
}

watch(
  () => [props.initialValue, props.doctorId],
  ([initialValue]) => {
    populateForm(initialValue)
  },
  { immediate: true },
)

watch(
  () => form.exception_type,
  (type) => {
    if (type === 'off') {
      form.start_time = ''
      form.end_time = ''
    } else {
      form.slot_duration_minutes ||= 30
      form.buffer_time_minutes = Number.isFinite(Number(form.buffer_time_minutes))
        ? Number(form.buffer_time_minutes)
        : 5
    }
  },
)

const toApiTime = (value) => {
  if (!value) {
    return ''
  }
  return value.length === 5 ? `${value}:00` : value
}

const validate = () => {
  resetErrors()

  if (!form.exception_date) {
    errors.exception_date = 'Exception date is required.'
  }

  if (isWorkException.value) {
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
  }

  return Object.values(errors).every((value) => !value)
}

const handleSubmit = () => {
  if (!props.doctorId) {
    return
  }

  if (!validate()) {
    return
  }

  const payload = {
    doctor_id: props.doctorId,
    exception_date: form.exception_date,
    exception_type: form.exception_type,
    reason: form.reason?.trim() ?? '',
    slot_duration_minutes: Number(form.slot_duration_minutes || 30),
    buffer_time_minutes: Number(form.buffer_time_minutes || 0),
  }

  if (isWorkException.value) {
    payload.start_time = toApiTime(form.start_time)
    payload.end_time = toApiTime(form.end_time)
  }

  emit('submit', payload)
}

const handleCancel = () => {
  populateForm(null)
  resetErrors()
  emit('cancel')
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <div class="grid gap-4 md:grid-cols-2">
      <div class="space-y-2">
        <Label>Exception Type</Label>
        <Select v-model="form.exception_type">
          <SelectTrigger class="w-full">
            <SelectValue placeholder="Select exception type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="type in EXCEPTION_TYPES" :key="type" :value="type">
              {{ type === 'off' ? 'Day Off / Vacation' : 'One-off Working Day' }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <DateTimeField
        label="Exception Date"
        :required="true"
        :date-value="form.exception_date"
        :error="errors.exception_date"
        @update:date-value="form.exception_date = $event"
      />
    </div>

    <div v-if="isWorkException" class="grid gap-4 md:grid-cols-2">
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

    <div v-if="isWorkException" class="grid gap-4 md:grid-cols-2">
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

    <div class="space-y-2">
      <Label>Reason</Label>
      <Textarea v-model="form.reason" placeholder="Optional note for staff context" />
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
        {{ submitting ? 'Saving...' : isEditMode ? 'Update Exception' : 'Add Exception' }}
      </Button>
    </div>
  </form>
</template>
