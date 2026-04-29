<script setup>
import { computed, ref } from 'vue'
import { parseDate } from '@internationalized/date'
import { Calendar as CalendarIcon } from 'lucide-vue-next'
import Button from '@/components/ui/button/Button.vue'
import Calendar from '@/components/ui/calendar/Calendar.vue'
import Input from '@/components/ui/input/Input.vue'
import Label from '@/components/ui/label/Label.vue'
import Popover from '@/components/ui/popover/Popover.vue'
import PopoverContent from '@/components/ui/popover/PopoverContent.vue'
import PopoverTrigger from '@/components/ui/popover/PopoverTrigger.vue'

const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  dateValue: {
    type: String,
    default: '',
  },
  timeValue: {
    type: String,
    default: '',
  },
  datePlaceholder: {
    type: String,
    default: 'Pick a date',
  },
  timePlaceholder: {
    type: String,
    default: 'Select time',
  },
  showTime: {
    type: Boolean,
    default: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:dateValue', 'update:timeValue'])

const popoverOpen = ref(false)

const calendarValue = computed(() => {
  if (!props.dateValue) {
    return undefined
  }

  try {
    return parseDate(props.dateValue)
  } catch {
    return undefined
  }
})

const formattedDate = computed(() => {
  if (!props.dateValue) {
    return props.datePlaceholder
  }

  const parsedDate = new Date(`${props.dateValue}T00:00:00`)

  if (Number.isNaN(parsedDate.getTime())) {
    return props.dateValue
  }

  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(parsedDate)
})

const handleDateSelect = (value) => {
  emit('update:dateValue', value ? value.toString() : '')
  popoverOpen.value = false
}

const handleTimeInput = (value) => {
  emit('update:timeValue', value)
}
</script>

<template>
  <div class="space-y-2">
    <Label v-if="label">
      {{ label }}
      <span v-if="required" class="text-destructive">*</span>
    </Label>

    <div :class="showTime ? 'grid gap-3 md:grid-cols-[minmax(0,1fr)_10rem]' : ''">
      <Popover v-model:open="popoverOpen">
        <PopoverTrigger as-child>
          <Button
            type="button"
            variant="outline"
            :disabled="disabled"
            class="w-full justify-start text-left font-normal"
          >
            <CalendarIcon class="mr-2 size-4 opacity-70" />
            <span :class="!dateValue ? 'text-muted-foreground' : ''">
              {{ formattedDate }}
            </span>
          </Button>
        </PopoverTrigger>

        <PopoverContent class="w-auto p-0" align="start">
          <Calendar
            :model-value="calendarValue"
            @update:model-value="handleDateSelect"
          />
        </PopoverContent>
      </Popover>

      <Input
        v-if="showTime"
        :model-value="timeValue"
        type="time"
        :disabled="disabled"
        :placeholder="timePlaceholder"
        @update:model-value="handleTimeInput"
      />
    </div>

    <p v-if="error" class="text-sm text-destructive">
      {{ error }}
    </p>
  </div>
</template>
