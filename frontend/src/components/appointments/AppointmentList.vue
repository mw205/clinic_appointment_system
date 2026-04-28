<script setup>
import AppointmentCard from "@/components/appointments/AppointmentCard.vue";

defineProps({
  appointments: {
    type: Array,
    required: true,
  },
  calculateWaitTime: {
    type: Function,
    required: true,
  },
});

const emit = defineEmits(["check-in", "no-show", "complete", "view-record"]);
</script>

<template>
  <div class="space-y-3">
    <AppointmentCard
      v-for="appointment in appointments"
      :key="appointment.id"
      :appointment="appointment"
      :calculate-wait-time="calculateWaitTime"
      @check-in="emit('check-in', $event)"
      @no-show="emit('no-show', $event)"
      @complete="emit('complete', $event)"
      @view-record="emit('view-record', $event)"
    />
  </div>
</template>
