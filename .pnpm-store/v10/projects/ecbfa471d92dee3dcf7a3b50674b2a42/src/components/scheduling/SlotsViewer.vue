<script setup>
import { reactive } from 'vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import DateTimeField from '@/components/scheduling/DateTimeField.vue'
import { defaultSlotsQueryModel } from '@/components/scheduling/models'

const props = defineProps({
  doctorId: {
    type: Number,
    default: null,
  },
  slots: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['load-slots'])

const query = reactive({ ...defaultSlotsQueryModel })

const formatSlotTime = (value) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

const handleSubmit = () => {
  if (!props.doctorId || !query.date) {
    return
  }

  emit('load-slots', {
    doctor_id: props.doctorId,
    date: query.date,
  })
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Available Slots</CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <DateTimeField
          label="Choose Date"
          :date-value="query.date"
          :disabled="!doctorId"
          @update:date-value="query.date = $event"
        />

        <Button type="submit" :disabled="loading || !doctorId || !query.date">
          {{ loading ? 'Loading...' : 'Load Slots' }}
        </Button>
      </form>

      <div v-if="slots.length" class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="slot in slots"
          :key="`${slot.start_time}-${slot.end_time}`"
          class="rounded-lg border border-border bg-muted/30 p-4"
        >
          <p class="font-medium">{{ formatSlotTime(slot.start_time) }}</p>
          <p class="text-sm text-muted-foreground">
            Ends at {{ formatSlotTime(slot.end_time) }}
          </p>
        </div>
      </div>

      <p v-else-if="!loading" class="text-sm text-muted-foreground">
        No slots loaded yet. Pick a date to preview bookable times.
      </p>
    </CardContent>
  </Card>
</template>
