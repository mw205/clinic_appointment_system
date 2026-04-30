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
  emptyMessage: {
    type: String,
    default: "No appointments found.",
  },
  canStartConsultation: {
    type: Boolean,
    default: false,
  },
  canViewRecord: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["check-in", "no-show", "complete", "view-record"]);
</script>

<template>
  <div class="space-y-3">
    <div
      v-if="appointments.length === 0"
      class="rounded-lg border border-dashed border-gray-300 px-4 py-8 text-center text-sm text-gray-500"
    >
      {{ emptyMessage }}
    </div>

    <AppointmentCard
      v-for="appointment in appointments"
      :key="appointment.id"
      :appointment="appointment"
      :calculate-wait-time="calculateWaitTime"
      :can-start-consultation="canStartConsultation"
      :can-view-record="canViewRecord"
      @check-in="emit('check-in', $event)"
      @no-show="emit('no-show', $event)"
      @complete="emit('complete', $event)"
      @view-record="emit('view-record', $event)"
    />
  </div>
</template>
